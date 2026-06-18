# Research Report: subset-b-008097

This grouped report covers Apache Ozone Manager lock, multitenancy, Ratis, snapshot, and request dispatch sources. Each section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneManagerLock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneManagerLock.java

## Purpose
`OzoneManagerLock` is the central Ozone Manager concurrency primitive. It exposes the `IOzoneManagerLock` API over striped `ReentrantReadWriteLock` instances and enforces resource-ordering rules so OM requests do not acquire locks in cycles. It handles both the legacy numeric hierarchy represented by `LeveledResource` and a DAG resource family represented by `DAGLeveledResource`.

## Important APIs and Types
- Constructor `OzoneManagerLock(ConfigurationSource)` creates lock metrics and two resource maps: one for `LeveledResource` and one for `DAGLeveledResource`.
- Public lock APIs include `acquireReadLock`, `acquireReadLocks`, `acquireWriteLock`, `acquireWriteLocks`, `acquireResourceWriteLock`, and matching release methods.
- Multi-user helpers `acquireMultiUserLock` and `releaseMultiUserLock` acquire two `USER_LOCK` write locks through the bulk-lock path.
- Introspection/testing APIs include `getReadHoldCount`, `getWriteHoldCount`, `isWriteLockedByCurrentThread`, `getOMLockMetrics`, and `cleanup`.
- `LeveledResource` defines `S3_BUCKET_LOCK`, `VOLUME_LOCK`, `BUCKET_LOCK`, `USER_LOCK`, `S3_SECRET_LOCK`, `KEY_PATH_LOCK`, `PREFIX_LOCK`, and `SNAPSHOT_LOCK` with bit-mask ordering logic.

## Control Flow
Construction calls `getLeveledLocks` and `getFlatLocks`, each building an `EnumMap` from resource enum to a Guava-style `Striped<ReadWriteLock>`. Stripe count comes from `ozone.manager.striped.lock.size.<resource>` with a default; lock fairness is read from `OZONE_MANAGER_FAIR_LOCK`.

For single-key acquisition, `acquireLock` obtains the correct `ResourceLockTracker`, clears the per-thread `OMLockDetails`, checks `canLockResource`, finds a stripe by `CompositeKey.combineKeys(keys)`, locks either read or write side, updates wait metrics, and marks the resource locked in the tracker. Bulk acquisition uses `bulkGetLock` or `getAllLocks` and iterates in deterministic stripe order; release reverses the lock list before unlocking.

Unlock paths release the lock first and then update held-time metrics. For write unlock, the code captures `isWriteLockedByCurrentThread` before unlocking so metrics are recorded only for the owner’s final release. `updateProcessingDetails` sends timing to the current IPC call when available; for Ratis-applied writes where no `Server.Call` is present, it records wait/read/write timing into the tracker’s `OMLockDetails` so the response can carry lock timing back through the state machine.

## State and Persistence Behavior
The class does not persist state. Its mutable state is process-local: striped locks, `OMLockMetrics`, per-resource `ResourceManager` timing state, and tracker thread locals. Persistence integration is indirect: lock details are merged into OM responses and Ratis write execution, while lock ordering protects metadata cache and RocksDB update logic in request handlers.

## Dependencies and Integration Points
It integrates with `OMLockMetrics`, `ResourceLockTracker`, `LeveledResourceLockTracker`, `DAGResourceLockTracker`, `ResourceManager`, Hadoop IPC `ProcessingDetails`, and OM request classes that acquire bucket, volume, user, prefix, snapshot, and S3 locks. The `RegularBucketLockStrategy` delegates bucket locks to this class. Configuration is provided by `ConfigurationSource`.

## Risks and Edge Cases
The hierarchy is enforced per thread through trackers; callers that bypass the lock API or mix unrelated lock systems can still deadlock. Bulk locks ignore null key arrays in `bulkGetLock`, so callers must ensure input collections represent the intended locks. Reentrant acquisition is allowed for lower resources but deliberately forbidden for `USER_LOCK`, `S3_SECRET_LOCK`, and `PREFIX_LOCK` under the mask logic. Metrics start times live on enum resource managers, so correctness depends on the reentrancy checks preventing overwritten timing for nested holds.

## Test Signals
The file exposes `@VisibleForTesting` helpers for current locks and hold counts. Tests should verify hierarchy violations, allowed high-order acquisition, multi-user lock ordering, metrics timing on final release, read/write reentrancy behavior, and Ratis/no-IPC `OMLockDetails` propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneManagerLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/PoolBasedHierarchicalResourceLockManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/PoolBasedHierarchicalResourceLockManager.java

## Purpose
`PoolBasedHierarchicalResourceLockManager` implements `HierarchicalResourceLockManager` for DAG-style resources using a bounded Apache Commons pool of reusable `ReadWriteLock` objects. It provides key-level read/write locks and whole-resource write locks while enforcing DAG resource-ordering through `DAGResourceLockTracker`.

## Important APIs and Types
- Constructor reads soft and hard lock-pool limits from `OZONE_OM_HIERARCHICAL_RESOURCE_LOCKS_*` config keys.
- `acquireReadLock(DAGLeveledResource, String)` and `acquireWriteLock(...)` return closeable `HierarchicalResourceLock` handles.
- `acquireResourceWriteLock(DAGLeveledResource)` locks the resource-level write lock, blocking all key-level locks for that resource.
- `getCurrentLockedResources` delegates to the resource tracker.
- Inner `PoolBasedHierarchicalResourceKeyLock` and `PoolBasedHierarchicalResourceLock` own lifecycle and release on `close`.
- `LockReferenceCountPair` associates a pooled lock with a reference count.

## Control Flow
The manager keeps, per `DAGLeveledResource`, a resource-level `ReentrantReadWriteLock` plus a concurrent map from string key to `LockReferenceCountPair`. Key-lock acquisition first checks `resourceLockTracker.canLockResource`; then `operateOnLock` atomically computes the key map entry, borrowing a lock from the pool if needed and incrementing the reference count. The returned lock handle acquires the resource-level read lock and then the key lock. Whole-resource acquisition takes the resource-level write lock instead.

On `close`, a key lock unlocks the key lock, unlocks the resource-level read lock, updates the tracker, and decrements the reference count through `operateOnLock`. When the count reaches zero, the pooled `ReadWriteLock` is returned and the key entry is removed. The whole-resource lock only unlocks the resource write lock and tracker state.

## State and Persistence Behavior
All state is in-memory: pool contents, per-resource maps, reference counts, and tracker thread locals. There is no direct persistence. Its role is to protect hierarchical metadata operations, especially DAG-like structures such as filesystem trees or snapshot chains, before request handlers mutate OM metadata caches and RocksDB tables.

## Dependencies and Integration Points
It depends on Commons Pool `GenericObjectPool`, Ratis `UncheckedAutoCloseable`, `DAGLeveledResource`, `DAGResourceLockTracker`, and `OzoneConfiguration`. Callers are expected to use try-with-resources or otherwise close returned handles; failure to close leaks references and keeps lock objects checked out.

## Risks and Edge Cases
The key-level constructor increments reference count before acquiring the actual lock. If thread interruption or runtime failure occurs between construction steps, cleanup depends on handle close. `operateOnLock` returns pooled locks to the pool while inside a `ConcurrentHashMap.compute` callback; pool errors are wrapped into `IOException`. Whole-resource and key-level locking rely on the resource read/write lock ordering: resource write waits for all key read holders. Deadlock prevention is only as strong as `DAGResourceLockTracker`.

## Test Signals
Useful tests include pool limit exhaustion behavior, reference count increment/decrement and removal, whole-resource exclusion of key locks, close idempotence, tracker ordering rejection, and exception propagation when pool borrow fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/PoolBasedHierarchicalResourceLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ReadOnlyHierarchicalResourceLockManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ReadOnlyHierarchicalResourceLockManager.java

## Purpose
`ReadOnlyHierarchicalResourceLockManager` is a no-op implementation of `HierarchicalResourceLockManager` for read-only contexts where mutation locks should never be acquired.

## Important APIs and Types
It returns two singleton anonymous `HierarchicalResourceLock` implementations: one reports `isLockAcquired() == true` for read locks and the other reports `false` for write/resource-write locks. `getCurrentLockedResources` returns an empty stream, and `close` is a no-op.

## Control Flow
`acquireReadLock` immediately returns the acquired empty handle without touching any shared state. `acquireWriteLock` and `acquireResourceWriteLock` return the non-acquired empty handle. The returned handles have empty `close` methods.

## State and Persistence Behavior
There is no state and no persistence. The class communicates capability via the returned lock status rather than blocking.

## Dependencies and Integration Points
It implements the same interface as the pool-based manager, letting read-only metadata readers plug into code expecting a hierarchical lock manager without changing call sites.

## Risks and Edge Cases
Callers must check `isLockAcquired` for write locks if they use this implementation. Any code that assumes `acquireWriteLock` always returns a successful handle could accidentally perform writes without synchronization, so this class should only be injected into strictly read-only paths.

## Test Signals
Tests should verify all methods are non-blocking, read locks report acquired, write locks report not acquired, and current locked resources is empty.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ReadOnlyHierarchicalResourceLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/RegularBucketLockStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/RegularBucketLockStrategy.java

## Purpose
`RegularBucketLockStrategy` is the standard `OzoneLockStrategy` for non-FSO bucket operations. It validates the target bucket and acquires/releases `OzoneManagerLock.LeveledResource.BUCKET_LOCK`.

## Important APIs and Types
It implements `acquireWriteLock`, `releaseWriteLock`, `acquireReadLock`, and `releaseReadLock`. All methods take `OMMetadataManager`, volume, bucket, and key names, but the key name is unused for regular bucket locking.

## Control Flow
Acquire paths call `OMFileRequest.validateBucket(omMetadataManager, volumeName, bucketName)` before acquiring the bucket lock from `omMetadataManager.getLock()`. Release paths delegate directly to the matching `release*Lock(BUCKET_LOCK, volumeName, bucketName)`.

## State and Persistence Behavior
The class has no state and does not persist. It protects metadata reads and writes performed after validation by taking the bucket-level lock.

## Dependencies and Integration Points
It integrates with `OMMetadataManager`, `OMFileRequest.validateBucket`, `OzoneLockStrategy`, and `OzoneManagerLock`. It is a strategy slot for code that chooses lock behavior based on bucket layout or request type.

## Risks and Edge Cases
Validation happens before lock acquisition, so bucket state can theoretically change between validation and lock acquisition unless outer code holds a broader lock. Release does not validate and assumes the caller owns the lock.

## Test Signals
Tests should cover validation failure, read/write acquisition and release against `BUCKET_LOCK`, and behavior when volume/bucket names select the same stripe.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/RegularBucketLockStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ResourceLockTracker.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ResourceLockTracker.java

## Purpose
`ResourceLockTracker` is the abstract base for per-thread lock-order tracking and `OMLockDetails` collection. Concrete trackers implement resource-specific ordering rules.

## Important APIs and Types
It declares abstract `canLockResource(T)` and `getCurrentLockedResources()`. It provides `clearLockDetails`, `lockResource`, `unlockResource`, and `getOmLockDetails`. The backing `OMLockDetails` is a `ThreadLocal`.

## Control Flow
Before a lock operation, `OzoneManagerLock` or the hierarchical lock manager calls `clearLockDetails`. When a lock is successfully acquired, `lockResource` marks the thread-local details as acquired. `unlockResource` currently just returns the current details, leaving concrete subclasses to handle actual resource set updates if they override behavior.

## State and Persistence Behavior
State is per-thread and in-memory. There is no persistence. The returned `OMLockDetails` can be attached to OM responses so Ratis-applied writes still expose lock wait/held timings.

## Dependencies and Integration Points
The type parameter must implement `IOzoneManagerLock.Resource`. Concrete classes such as `LeveledResourceLockTracker` and `DAGResourceLockTracker` supply resource-order enforcement. `OzoneManagerLock.updateProcessingDetails` writes timing into this tracker when there is no Hadoop IPC call object.

## Risks and Edge Cases
The base class itself does not update a held-resource set; correctness depends on concrete subclasses. Since `OMLockDetails` is thread-local, work that crosses threads must explicitly merge or transfer details.

## Test Signals
Tests should verify concrete trackers clear and report details correctly, and that lock-acquired flags and timing values are visible through `getOmLockDetails`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ResourceLockTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om.lock` as containing OM lock strategy pattern classes and interfaces.

## Important APIs and Types
The file exports no Java types beyond the package declaration. Its JavaDoc describes the lock package role.

## Control Flow
There is no executable control flow.

## State and Persistence Behavior
There is no state or persistence behavior.

## Dependencies and Integration Points
The descriptor applies package-level documentation for the lock package used by OM request handlers and metadata managers.

## Risks and Test Signals
No runtime risk. Tests generally do not target this file; build and JavaDoc checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLock.java

## Purpose
`AuthorizerLock` defines the synchronization contract around the external multi-tenant authorizer, typically Ranger. It lets background sync and tenant OM requests coordinate reads, writes, and optimistic reads.

## Important APIs and Types
The interface exposes timed read/write acquisition (`tryReadLock`, `tryWriteLock`), stamped unlocks, optimistic read helpers, timeout-throwing wrappers, OM-request-specific write lock wrappers, and `isWriteLockHeldByCurrentThread`.

## Control Flow
Implementations return `StampedLock` stamps that callers must pass back to the matching unlock. `tryOptimisticReadThrowOnTimeout` is intended to block briefly for a read state, convert to optimistic read, and later allow validation. OM requests use `tryWriteLockInOMRequest` and `unlockWriteInOMRequest` so the implementation can remember ownership during request execution.

## State and Persistence Behavior
The interface itself has no state. It protects in-memory and remote authorizer state transitions; persistence of tenant metadata is handled elsewhere by OM request processing and the access controller backend.

## Dependencies and Integration Points
It is private/unstable and referenced by `OMMultiTenantManagerImpl.AuthorizerOp`. Concrete `AuthorizerLockImpl` uses `StampedLock`.

## Risks and Test Signals
Callers must pair stamps correctly or implementations may throw `IllegalMonitorStateException`. Tests should cover timeout behavior, optimistic read validation, and OM-request write lock ownership checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLockImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLockImpl.java

## Purpose
`AuthorizerLockImpl` implements `AuthorizerLock` with a `StampedLock`. It serializes writes to the tenant authorizer and supports optimistic reads for read-mostly paths.

## Important APIs and Types
It implements all `AuthorizerLock` methods. Fields include the `StampedLock`, `omRequestWriteLockStamp`, and `omRequestWriteLockHolderTid`. Timeout wrappers use `OZONE_TENANT_AUTHORIZER_LOCK_WAIT_MILLIS` and throw `OMException` with `TIMEOUT` or `INTERNAL_ERROR`.

## Control Flow
`tryReadLock` and `tryWriteLock` delegate to `StampedLock.try*Lock(timeout, MILLISECONDS)`. `tryOptimisticReadThrowOnTimeout` first obtains a real read lock, converts it to an optimistic read stamp, and throws if either timed out or conversion unexpectedly fails. `tryWriteLockThrowOnTimeout` wraps interrupted waits and zero stamps. `tryWriteLockInOMRequest` obtains a write stamp, verifies no previous OM request write stamp is recorded, then stores stamp and thread id. `unlockWriteInOMRequest` tolerates missing stamp because a follower or leader change may mean no local lock was held; otherwise it clears fields and unlocks by stamp. `isWriteLockHeldByCurrentThread` compares the stored holder id with the current thread id.

## State and Persistence Behavior
State is process-local. It does not persist tenant changes; it guards the sequence in which OM requests and background authorizer synchronization interact with Ranger or in-memory access controllers.

## Dependencies and Integration Points
It integrates with `OMMultiTenantManagerImpl.AuthorizerOp`, OM tenant request classes, and authorizer background sync. It depends on Guava `Preconditions`, `StampedLock`, and OM exception result codes.

## Risks and Edge Cases
The stamp and holder fields are plain longs and are only safe because the code assumes they are updated while holding the write lock. `StampedLock` is not reentrant; repeated OM request write locking fails precondition checks. `unlockWriteInOMRequest` intentionally ignores zero stamps, which prevents follower paths from failing but can mask incorrect pairing if caller state is wrong.

## Test Signals
Tests should verify read/write timeout to `OMException`, optimistic read validation after a write, non-reentrant OM request write locks, holder thread checks, and zero-stamp unlock behavior after simulated follower/leader changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLockImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/CachedTenantState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/CachedTenantState.java

## Purpose
`CachedTenantState` is an in-memory representation of tenant metadata needed by OM multi-tenancy logic: tenant id, role names, and access-id to user/admin mappings.

## Important APIs and Types
The main type stores `tenantId`, `tenantUserRoleName`, `tenantAdminRoleName`, and `HashMap<String, CachedAccessIdInfo>`. Nested `CachedAccessIdInfo` stores `userPrincipal` and mutable `isAdmin`.

## Control Flow
The constructor initializes identifiers and an empty access map. Getters expose role names, tenant id, and the mutable access map. `isTenantEmpty` checks whether the access map is empty. Equality compares identifiers and access map contents; nested equality compares principal and admin flag.

## State and Persistence Behavior
This class is explicitly in-memory cache state. It does not load or save data; callers populate it from OM tenant metadata and update it as tenant access IDs and admin status change.

## Dependencies and Integration Points
It is used by OM multi-tenant manager code to cache state derived from OM DB tables and authorizer roles/policies. It only depends on Java collections.

## Risks and Edge Cases
`getAccessIdInfoMap` exposes the mutable backing map. `hashCode` omits `accessIdInfoMap` even though `equals` includes it, which is legal only if identifiers define stable bucket placement; unequal hashes are not required for unequal objects, but equal objects must have same hash, and equal objects do because identifiers match. Concurrent callers need external synchronization.

## Test Signals
Tests should cover equality, mutable admin flag updates, empty detection, and map mutation behavior through the getter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/CachedTenantState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/InMemoryMultiTenantAccessController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/InMemoryMultiTenantAccessController.java

## Purpose
`InMemoryMultiTenantAccessController` is a development/testing implementation of `MultiTenantAccessController` that keeps policies and roles in local maps rather than talking to Ranger.

## Important APIs and Types
It implements policy CRUD, role CRUD, and `getRangerServicePolicyVersion`. Fields are `policies`, `roles`, `nextRoleID`, and `serviceVersion`.

## Control Flow
`createPolicy` rejects duplicate policy names and duplicate resource sets, stores the policy, creates missing roles referenced by role ACLs, and increments service version. `getLabeledPolicies` filters policies by label. `updatePolicy` and `deletePolicy` require existing names and increment service version. `createRole` rejects duplicates, builds a copy with the next role id, stores it, increments id and service version, and returns the input role rather than the id-enriched copy. `updateRole` finds by id, removes the old role name, stores the supplied role, and increments version. `deleteRole` removes by name.

## State and Persistence Behavior
All state is process-local and lost on restart. `serviceVersion` simulates Ranger policy version changes for synchronization logic but is not durable.

## Dependencies and Integration Points
`MultiTenantAccessController.create` selects this implementation when `OZONE_OM_TENANT_DEV_SKIP_RANGER` is true. It supports tenant OM requests and tests that should not require a Ranger service.

## Risks and Edge Cases
The class is not synchronized and is unsuitable for concurrent production use. Returning the original role from `createRole` means callers expecting the assigned id from the return value may be surprised, although `getRole` returns the stored id-enriched role. Duplicate resource detection uses exact set equality.

## Test Signals
Tests should cover duplicate policy/resource rejection, automatic role creation from policy ACLs, service version increments, role update by id, and the createRole return-value behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/InMemoryMultiTenantAccessController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessController.java

## Purpose
`MultiTenantAccessController` abstracts tenant access-control operations over Ranger or a development in-memory backend. It defines policy and role models, ACL mapping, and factory selection.

## Important APIs and Types
The interface declares policy CRUD (`createPolicy`, `getPolicy`, `getLabeledPolicies`, `updatePolicy`, `deletePolicy`), role CRUD (`createRole`, `getRole`, `updateRole`, `deleteRole`), and `getRangerServicePolicyVersion`. Static `getRangerAclStrings` maps Ozone ACL enum values to Ranger strings. Nested classes model `Acl`, `Role`, `Role.Builder`, `Policy`, and `Policy.Builder`.

## Control Flow
`Acl.allow` and `Acl.deny` construct immutable allow/deny values. `Role.Builder` accumulates role name, user and role admin maps, description, id, and creator. `Role.equals` treats absent role IDs as compatible but compares IDs when both are present. `Policy.Builder` accumulates resource sets, labels, user ACLs, role ACLs, description, id, and enabled flag; `build` requires a non-empty name. `create(ConfigurationSource)` chooses `InMemoryMultiTenantAccessController` when dev skip Ranger is set, otherwise reflectively loads `RangerClientMultiTenantAccessController`.

## State and Persistence Behavior
The interface and nested model classes are in-memory value objects. Persistence is implemented by concrete controllers: Ranger-backed controller persists to Ranger; in-memory controller does not. Policy version is the external synchronization signal used by OM tenant code.

## Dependencies and Integration Points
It depends on `IAccessAuthorizer.ACLType`, `ConfigurationSource`, `ReflectionUtils`, and `OMMultiTenantManagerImpl.OZONE_OM_TENANT_DEV_SKIP_RANGER`. Tenant create/delete/admin/access-id requests use these types to express desired Ranger state.

## Risks and Edge Cases
Builders expose mutable maps/sets into constructed objects rather than defensive immutable copies, so callers retaining builder references can mutate built roles/policies. `Policy.Builder.setId(Long)` unboxes into a primitive long and will throw on null. The reflective class name creates a runtime dependency not visible to the compiler in this file.

## Test Signals
Tests should cover ACL string mapping, equality semantics with optional role IDs, policy name validation, builder mutation behavior, factory selection based on configuration, and Ranger-client class loading failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om.multitenant` as containing Ozone multi-tenancy classes.

## Important APIs and Types
The file exports no runtime types besides the package declaration.

## Control Flow
There is no executable control flow.

## State and Persistence Behavior
There is no state or persistence.

## Dependencies and Integration Points
It gives package-level JavaDoc for tenant authorizer locks, cached tenant state, and access controller abstractions.

## Risks and Test Signals
No runtime risk. Build and documentation generation are the only relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om` as containing Ozone Manager classes.

## Important APIs and Types
It contains only package-level JavaDoc and the package declaration.

## Control Flow
There is no executable code.

## State and Persistence Behavior
There is no state or persistence behavior.

## Dependencies and Integration Points
The descriptor applies to the broad Ozone Manager package that contains metadata management, request handling, Ratis integration, security, locks, and multitenancy.

## Risks and Test Signals
No runtime risk. Compilation and JavaDoc generation are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBuffer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBuffer.java

## Purpose
`OzoneManagerDoubleBuffer` batches `OMClientResponse` objects from committed Ratis transactions and persists them to OM RocksDB in a background flush thread. It is the write-side persistence bridge between `OzoneManagerStateMachine.runCommand` and `OMMetadataManager` tables.

## Important APIs and Types
- `Builder` configures metadata manager, last-applied callback, tracing, maximum unflushed transaction count, thread prefix, S3 secret manager, and optional flush notifier.
- `start`, `stop`, `pause`, `unpause`, and `resume` control the daemon.
- `acquireUnFlushedTransactions` and `releaseUnFlushedTransactions` implement backpressure via a semaphore.
- `add(OMClientResponse, TermIndex)` appends to the current buffer.
- `flushTransactions`, `flushCurrentBuffer`, and `flushBatch` perform batch persistence.
- `FlushNotifier` lets callers wait until both buffers have gone through flush notifications.

## Control Flow
The state machine acquires one semaphore permit before scheduling a write. Request handling updates in-memory metadata caches and calls `doubleBuffer.add(response, termIndex)`. The daemon waits in `canFlush` until `currentBuffer` is non-empty, swaps `currentBuffer` and `readyBuffer`, splits ready entries around `CreateSnapshot` and `SnapshotPurge` barriers, and flushes each queue.

`flushBatch` sorts term indexes, adds each response to a RocksDB `BatchOperation` via `response.checkAndUpdateDB`, writes `TransactionInfo` for the last term/index, commits the batch, updates metrics, cleans metadata caches for epochs derived from each response’s `@CleanupTableInfo`, releases semaphore permits, and calls `updateLastAppliedIndex`. Snapshot barrier splitting ensures snapshot create/purge operations are isolated in standalone batches so RocksDB snapshot callbacks observe precise ordering.

## State and Persistence Behavior
The class persists OM metadata changes and the `TRANSACTION_INFO_KEY` transaction marker into RocksDB. It also cleans table caches and S3 secret cache after committed epochs. In-memory state includes two concurrent queues, daemon status flags, a pause flag, semaphore, metrics singleton, and flushed counts for testing. On unrecoverable batch errors, it calls `ExitUtils.terminate` to avoid continuing with potentially divergent DB state.

## Dependencies and Integration Points
It depends on `OMMetadataManager`, `OMClientResponse`, `BatchOperation`, `TransactionInfo`, `OMDBDefinition`, `CleanupTableInfo`, `S3SecretManager`, `TermIndex`, Hadoop `Daemon`, and tracing utilities. `OzoneManagerStateMachine` builds and owns it.

## Risks and Edge Cases
Every response class must carry `@CleanupTableInfo`; otherwise `addCleanupEntry` throws and terminates OM. Empty flush batches are not expected because `canFlush` waits for entries. `FlushNotifier` relies on a two-notification convention when both buffers are empty; tests that wait for flushes need to account for this. The semaphore must be released exactly once per flushed transaction or write application can stall. `pause` stops flushing but queued entries remain in memory.

## Test Signals
Tests should cover buffer swap behavior, snapshot/purge split barriers, transaction info persistence, cache cleanup table selection, S3 cache cleanup, semaphore backpressure, flush notifier completion, metrics updates, and fatal handling for missing cleanup annotations or RocksDB failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBufferMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBufferMetrics.java

## Purpose
`OzoneManagerDoubleBufferMetrics` publishes Hadoop metrics for double-buffer flush activity.

## Important APIs and Types
It is a singleton metrics source registered with `DefaultMetricsSystem`. Metrics include total flush operations, total flushed transactions, max transactions per flush iteration, RocksDB batch commit latency (`MutableRate`), average transactions per iteration (`MutableGaugeFloat`), and queue size (`MutableStat`). `updateFlush` updates the aggregate counters and gauges after a flush.

## Control Flow
`create` registers a singleton if none exists. `updateFlush` increments operation and transaction counters, recomputes average transaction count, raises the max counter if needed, and records queue size. `updateFlushTime` records commit latency. `unRegister` unregisters the source name.

## State and Persistence Behavior
Metrics state is in-memory in the Hadoop metrics system and is not persisted. It represents runtime observability for OM double-buffer flushes.

## Dependencies and Integration Points
`OzoneManagerDoubleBuffer` creates and updates this source. Tests can read getters or internal package-private metric objects.

## Risks and Edge Cases
The singleton is static. Multiple OM instances in the same JVM can share one metrics object unless unregistered carefully. `setMaxNumberOfTransactionsFlushedInOneIteration` uses `Math.negateExact` on the current value; overflow is unlikely but possible in theory for extremely large counters.

## Test Signals
Tests should verify singleton registration, flush counter increments, max update logic, average calculation, queue stat updates, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBufferMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServer.java

## Purpose
`OzoneManagerRatisServer` wraps the Apache Ratis server used by OM HA. It constructs the Raft group, translates OM requests into Raft client requests, maps Raft replies and exceptions back to OM responses, manages dynamic peer configuration, and applies OM-specific Ratis configuration.

## Important APIs and Types
- `newOMRatisServer` builds a server from local node details, peer details, security config, and bootstrap mode.
- `submitRequest(OMRequest, boolean)` sends read or write OM requests through Ratis, subject to OM prepare-state gating.
- `submitRequest(OMRequest, ClientId, long)` supports internal submissions with explicit invocation IDs.
- Peer APIs include `addOMToRatisRing`, `removeOMFromRatisRing`, `addRaftPeer`, `removeRaftPeer`, `getPeers`, and `getPeerIds`.
- `createRaftPeer` preserves the configured host string instead of pre-resolving addresses so gRPC DNS refresh can work.
- `newRaftProperties` and helper setters populate Ratis log, RPC, retry cache, snapshot, close threshold, and HA properties.
- `RaftServerStatus` and `getLeaderStatus` expose leader readiness.

## Control Flow
Construction computes the storage directory, Raft group id from OM service id, peer map, state machine, read option, optional TLS parameters, and `RaftServer` instance. `submitRequest` rejects non-prepare/cancel writes when OM is prepared, otherwise creates a `RaftClientRequest`, submits it asynchronously to the local Ratis server, and converts the reply. Read requests use `getRaftReadRequestType`, honoring client read consistency hints where provided.

`createOmResponseImpl` handles unsuccessful replies by converting `NotLeaderException`, `LeaderNotReadyException`, `LeaderSteppingDownException`, read exceptions, and state-machine exceptions. For state-machine exceptions with an `OMException` cause, it builds a failed `OMResponse` with the mapped status; successful replies are decoded with `OMRatisHelper`.

Dynamic peer changes build `SetConfigurationRequest` objects from current follower/listener lists plus or minus the target node. Ratis config methods set log segment and preallocation sizes, purge behavior, appender queue limits, pending write element limits, RPC timeouts, retry cache expiry, auto snapshot threshold, and transport ports.

## State and Persistence Behavior
Persistent state is held by the underlying Ratis server in the configured Ratis storage directory. OM metadata persistence happens in the state machine/double buffer. This class tracks in-memory peer map, Raft group, state machine, client id, call id counter, and performance metrics.

## Dependencies and Integration Points
It integrates with `OzoneManager`, `OzoneManagerStateMachine`, `OMRatisHelper`, `OzoneManagerRatisUtils`, Ratis server/client classes, OM HA metrics, `SecurityConfig`, `CertificateClient`, and Hadoop/Ozone config keys. It is the submission path for OM RPC handlers and the owner of the state machine lifecycle.

## Risks and Edge Cases
Bootstrap mode starts with an empty peer list and relies on later set-configuration transactions. `getClientId` and `getCallId` require Hadoop RPC context unless test secure OM flag is set. State-machine exception mapping assumes causes are meaningful. `getRaftLeaderAddress` resolves the leader address for exception reporting, while peer creation intentionally avoids resolution for connectivity. Misconfigured HA properties can be passed through via prefix trimming.

## Test Signals
Tests should cover prepare-mode rejection, write/read request creation, read consistency hints, retry cache hits, not-leader and leader-not-ready conversion, state-machine exception status mapping, dynamic peer configuration, DNS-preserving peer creation, TLS parameter creation, and Ratis property defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServerConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServerConfig.java

## Purpose
`OzoneManagerRatisServerConfig` declares configuration metadata for selected OM Ratis server settings.

## Important APIs and Types
The class is annotated with `@ConfigGroup` under the OM HA Ratis server prefix. Fields declare `@Config` metadata for log appender minimum wait time, retry cache expiry, read option, and leader lease read setting.

## Control Flow
There are no methods in the visible source; configuration processing discovers fields and annotations through the Ozone configuration framework.

## State and Persistence Behavior
The class holds configuration default values and metadata, not runtime state. Actual values are loaded from configuration and applied elsewhere, especially in `OzoneManagerRatisServer.newRaftProperties`.

## Dependencies and Integration Points
It integrates with `OMConfigKeys`, `RaftServerConfigKeys`, and Ozone config tags/types. Operators use these keys to tune Ratis read semantics and retry-cache behavior.

## Risks and Edge Cases
Annotation keys must stay aligned with Ratis and OM config consumers. The read option text documents semantics where `DEFAULT` is leader-only/non-linearizable and `LINEARIZABLE` supports ReadIndex.

## Test Signals
Config generation tests and property-binding tests should ensure defaults, types, tags, and key names remain correct.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerRatisServerConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerStateMachine.java

## Purpose
`OzoneManagerStateMachine` is the Ratis state machine that applies committed OM log entries to the `OzoneManager`. It validates transactions, serializes write application, feeds responses into the double buffer, serves read queries, tracks snapshots, and handles leader/snapshot lifecycle callbacks.

## Important APIs and Types
- Constructor loads snapshot info from OM DB, builds `OzoneManagerDoubleBuffer`, creates an `OzoneManagerRequestHandler`, and starts single-thread executors for apply and snapshot install.
- Ratis hooks include `initialize`, `reinitialize`, `getLatestSnapshot`, `notifyLeaderReady`, `notifyNotLeader`, `notifyLeaderChanged`, `notifyTermIndexUpdated`, `notifyConfigurationChanged`, `notifySnapshotInstalled`, `startTransaction`, `preAppendTransaction`, `applyTransaction`, `query`, `pause`, `takeSnapshot`, `notifyInstallSnapshotFromLeader`, and `close`.
- `runCommand`, `createErrorResponse`, and `processResponse` are the main write-execution helpers.

## Control Flow
`startTransaction` decodes an `OMRequest`, validates group id and request shape, and either returns a context with exception or one containing log data and the decoded request. `preAppendTransaction` handles prepare-mode authorization and gating before the log append. `applyTransaction` decodes the request from context or log data, builds a `TermIndex`, acquires one double-buffer backpressure permit, then schedules `runCommand` on a single-thread executor. This serialization preserves deterministic application order across OM replicas.

`runCommand` builds an `ExecutionContext`, delegates write handling to `RequestHandler.handleWriteRequest`, obtains lock details from the response, and returns the `OMResponse` possibly augmented with protobuf lock timing. On `IOException`, it creates a failed response and still adds a `DummyOMClientResponse` to the double buffer so transaction index advancement remains consistent. `processResponse` terminates OM for critical `INTERNAL_ERROR` and `METADATA_ERROR`, but converts successful and non-critical responses to Ratis messages.

Read-only `query` decodes an OM request and delegates to `handler.handleReadRequest` without appending a log entry. Snapshot methods use `TransactionInfo` stored in OM DB as the Ratis snapshot marker. `takeSnapshot` waits for skipped term-index notifications to be covered by double-buffer flushes, writes `TRANSACTION_INFO_KEY`, flushes RocksDB, and returns the snapshot index. Snapshot installation is delegated asynchronously to `ozoneManager.installSnapshotFromLeader`.

## State and Persistence Behavior
The state machine persists last-applied term/index through `TransactionInfo` in OM DB and relies on `OzoneManagerDoubleBuffer` for actual metadata writes. It tracks in-memory `lastNotifiedTermIndex`, `lastSkippedIndex`, `previousLeaderId`, pause count, executors, double buffer, handler, and Netty metrics. On restart/reinitialize it reloads transaction info from DB.

## Dependencies and Integration Points
It integrates with Apache Ratis `BaseStateMachine`, `OzoneManager`, `OzoneManagerRequestHandler`, `OzoneManagerDoubleBuffer`, `OzoneManagerPrepareState`, OM metrics/audit, `OMRatisHelper`, `ExecutionContext`, and snapshot provider installation. `OzoneManagerRatisServer` owns it.

## Risks and Edge Cases
The single apply executor is intentionally conservative but can bottleneck throughput. A semaphore permit is acquired before async execution; if a path fails before double-buffer add/release, writes can stall. The prepare gate must reject non-prepare/cancel writes consistently on all nodes. Critical error termination is required to prevent DB divergence. Snapshot logic relies on transaction info monotonicity and correct handling of Ratis term-index notifications for non-state-machine log entries.

## Test Signals
Tests should cover request validation failures, prepare authorization and gating, serialized apply order, backpressure, error response index advancement, critical error termination, read query bypass, snapshot transaction info loading/writing, pause/unpause double-buffer rebuild, leader change notifications, configuration change peer updates, and install-snapshot async error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om.ratis` as containing the OM Ratis server implementation.

## Important APIs and Types
It exports only package-level documentation and the package declaration.

## Control Flow
There is no executable code.

## State and Persistence Behavior
There is no state or persistence.

## Dependencies and Integration Points
The package contains Ratis server, state machine, double buffer, metrics, and config classes for OM HA.

## Risks and Test Signals
No runtime risk. Build and JavaDoc generation are relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/utils/OzoneManagerRatisUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/utils/OzoneManagerRatisUtils.java

## Purpose
`OzoneManagerRatisUtils` is a utility class for OM HA request creation, exception/status mapping, transaction-info verification, Ratis directory selection, leader checks, TLS configuration, and internal Ratis submission.

## Important APIs and Types
- `createClientRequest(OMRequest, OzoneManager)` maps each write `Type` to an `OMClientRequest` subclass.
- `getOMAclRequest` maps ACL requests by object type and bucket layout.
- `exceptionToResponseStatus` converts exceptions to protobuf `Status`.
- `getTrxnInfoFromCheckpoint` and `verifyTransactionInfo` delegate to HA utilities with OM DB definition.
- `getOMRatisDirectory` and `getOMRatisSnapshotDirectory` select configured or default directories.
- `checkLeaderStatus`, `createServerTlsConfig`, `submitRequest`, and `createErrorResponse` provide common HA helpers.

## Control Flow
`createClientRequest` switches on OM command type. Simple volume, bucket, token, S3 secret, tenant, snapshot, upgrade, purge, echo, and quota-repair commands instantiate direct request classes. Bucket-layout-sensitive key operations first extract volume and bucket names from the command-specific protobuf payload, then call `BucketLayoutAwareOMKeyRequestFactory.createRequest`. Tenant commands call `ozoneManager.checkS3MultiTenancyEnabled` before instantiation. Lease recovery checks that the target bucket is FSO and rejects non-FSO buckets.

ACL mapping branches by command and object type. Volume and bucket ACLs use direct request classes. Key ACL requests first create a base request to determine bucket layout; if FSO, they return FSO-specific variants. Non-volume/bucket/key objects map to prefix ACL request classes.

`exceptionToResponseStatus` maps `OMException` by result ordinal, invalid path to `INVALID_PATH`, `IOException` caused by `RocksDBException` to `METADATA_ERROR`, and otherwise `INTERNAL_ERROR`. TLS config is returned only when both security and gRPC TLS are enabled.

## State and Persistence Behavior
The class has no mutable state. It influences persistence by selecting the request class whose `validateAndUpdateCache` and response write path will update OM metadata. Transaction-info helpers read checkpoint DB metadata and validate that a downloaded checkpoint is newer than the local last-applied index.

## Dependencies and Integration Points
It depends on a broad set of OM request classes, `BucketLayoutAwareOMKeyRequestFactory`, `OzoneManager`, `OMConfigKeys`, `HAUtils`, `ServerUtils`, `OMDBDefinition`, `SecurityConfig`, `CertificateClient`, Ratis `ClientId`, and RocksDB exception types. It is used by request handlers and Ratis state-machine error paths.

## Risks and Edge Cases
The large switch must be kept in sync with new protobuf command types; missing cases become `INVALID_REQUEST`. Requests that require bucket layout must extract the correct nested `KeyArgs` or delete/rename args, otherwise the wrong class or invalid bucket errors result. Exception-to-status mapping relies on enum ordinal compatibility between `OMException.ResultCodes` and protobuf `Status`. Reflecting RocksDB errors through `IOException.getCause` can miss wrapped causes deeper in the chain.

## Test Signals
Tests should cover every command type mapping, FSO versus object-store variants, tenant disabled rejection, lease recovery on non-FSO buckets, ACL object-type mapping, exception/status conversion, directory default fallback, TLS config creation, and checkpoint transaction verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/utils/OzoneManagerRatisUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/utils/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om.ratis.utils` as utilities used by Ozone Manager HA.

## Important APIs and Types
It exports only package-level JavaDoc and the package declaration.

## Control Flow
There is no executable code.

## State and Persistence Behavior
There is no state or persistence.

## Dependencies and Integration Points
The package hosts utility methods for Ratis request creation, error mapping, directories, TLS, and checkpoint verification.

## Risks and Test Signals
No runtime risk. Build and documentation checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/OmRatisSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/OmRatisSnapshotProvider.java

## Purpose
`OmRatisSnapshotProvider` downloads OM DB checkpoints from the current leader for follower bootstrap/catch-up and wraps the downloaded DB as a RocksDB checkpoint. It also supports transferring leader-created OM snapshots that must exist on followers.

## Important APIs and Types
- Constructors initialize snapshot directory, peer map, HTTP policy, SPNEGO mode, URL connection factory, and whether to use the v2 inode-based checkpoint API.
- `addNewPeerNode` and `removeDecommissionedPeerNode` update the peer map.
- `downloadSnapshot(String leaderNodeID, File targetFile)` performs the HTTP POST download.
- `downloadFileWithProgress` streams the response to disk and logs progress.
- `getCheckpointFromUntarredDb` returns an `InodeMetadataRocksDBCheckpoint`.
- `writeFormData` writes multipart form-data listing SST files to exclude.
- `close` destroys the connection factory.

## Control Flow
The configuration constructor reads HTTP policy, Kerberos/SPNEGO setting, connection timeout, request timeout, and the inode-based checkpoint flag. `downloadSnapshot` looks up leader node details, builds the OM DB checkpoint endpoint URL, opens an authenticated connection as the current user, sets multipart POST headers, computes existing files from the candidate directory, writes exclusion form data, and connects. It accepts HTTP 200 and 201. The response body is streamed to `targetFile`; if streaming fails, the partial target is deleted quietly and the exception is rethrown. The connection is disconnected in a finally block.

`writeFormData` emits one multipart field per SST/existing file using the configured multipart boundary. If there are no files, it still writes an empty field. `getCheckpointFromUntarredDb` wraps the untarred directory in an inode-aware checkpoint so later install code can reason about v1/v2 checkpoint layout.

## State and Persistence Behavior
The provider persists downloaded checkpoint archives/files into the snapshot provider’s candidate/target directories managed by `RDBSnapshotProvider`. It does not directly install the DB into OM; the state machine and OM install logic consume the checkpoint. Peer-node state is held in a concurrent map.

## Dependencies and Integration Points
It extends `RDBSnapshotProvider`, depends on `OMNodeDetails` for endpoint URLs, `URLConnectionFactory`, Hadoop security `SecurityUtil`, `HAUtils` for existing-file lists, `HttpConfig.Policy`, Apache Commons `FileUtils`, and `InodeMetadataRocksDBCheckpoint`. `OzoneManagerStateMachine.notifyInstallSnapshotFromLeader` triggers snapshot installation through OM, which uses this provider.

## Risks and Edge Cases
Missing leader node id causes a null dereference before URL creation. Large downloads rely on streaming and progress logs every 30 seconds. Partial file cleanup logs but does not fail if deletion itself fails. Multipart formatting must match the OM checkpoint endpoint. SPNEGO and HTTP policy misconfiguration can make follower catch-up fail. Concurrent peer map updates are safe at map level but do not validate role/service consistency.

## Test Signals
Tests should cover endpoint URL selection for v1/v2 checkpoint API, multipart body with empty and non-empty exclusion lists, HTTP error handling, partial download cleanup, SPNEGO connection path, peer add/remove, progress streaming, and checkpoint wrapper construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/OmRatisSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.om.ratis_snapshot` as containing OM Ratis snapshot related classes.

## Important APIs and Types
It exports only package-level JavaDoc and the package declaration.

## Control Flow
There is no executable code.

## State and Persistence Behavior
There is no state or persistence.

## Dependencies and Integration Points
The package contains snapshot provider code used for OM follower catch-up and Ratis snapshot installation.

## Risks and Test Signals
No runtime risk. Build and JavaDoc checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis_snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/BucketLayoutAwareOMKeyRequestFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/BucketLayoutAwareOMKeyRequestFactory.java

## Purpose
`BucketLayoutAwareOMKeyRequestFactory` instantiates the correct `OMKeyRequest` subclass for key-like operations based on the target bucket layout, especially distinguishing object-store and file-system-optimized buckets.

## Important APIs and Types
- Static `OM_KEY_REQUEST_CLASSES` maps a generated string key to request classes.
- Static initializer registers create directory/file/key, allocate block, commit, delete, rename, multipart, set times, and object-tagging request variants.
- `createRequest` validates volume/bucket names, resolves real bucket layout, builds the lookup key, and reflectively constructs the request.
- `addRequestClass`, `getRequestInstanceFromMap`, and `getKey` support registration and lookup.

## Control Flow
The static block registers one or two classes for each supported protobuf `Type`. FSO-specific classes are registered under keys with the bucket layout suffix; object-store classes use only the type name. `createRequest` rejects blank volume or bucket names with `OMException`, calls `OzoneManagerUtils.getBucketLayout` through the metadata manager to resolve link buckets, and looks up the class by `getKey(requestType, bucketLayout)`. If found, it obtains a constructor `(OMRequest, BucketLayout)` and invokes it. Reflection errors are logged and wrapped as `INTERNAL_ERROR`; missing mappings become `NOT_SUPPORTED_OPERATION`.

## State and Persistence Behavior
The only state is the static class map. The factory does not persist anything, but it determines which request class will validate, update metadata cache, and later write DB changes through the OM response path.

## Dependencies and Integration Points
It integrates with `OzoneManagerRatisUtils.createClientRequest`, `OMMetadataManager`, `BucketLayout`, and all key request subclasses. It relies on every registered request class exposing the `(OMRequest, BucketLayout)` constructor.

## Risks and Edge Cases
Adding a new key command requires registering all supported bucket layouts. `RenameKeys` only registers object-store in the visible map, so FSO requests for that command are intentionally unsupported unless handled elsewhere. Reflection defers constructor errors to runtime. Link-bucket layout resolution means metadata manager availability and bucket validation are part of request creation.

## Test Signals
Tests should cover mapping keys for object-store and FSO layouts, blank name errors, unsupported layout/type errors, constructor mismatch error handling, link bucket layout resolution, and every registered command type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/BucketLayoutAwareOMKeyRequestFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequest.java

## Purpose
`OMClientRequest` is the abstract base for write-side OM request handlers. It defines pre-execution request augmentation, deterministic cache update contract, ACL helpers, user/remote-address extraction, audit helpers, key path normalization, error response creation, and lock detail aggregation.

## Important APIs and Types
- Constructor stores a non-null `OMRequest` and clears `OMLockDetails`.
- `preExecute(OzoneManager)` sets `UserInfo` and metadata layout version before a request is serialized to Ratis.
- Abstract `validateAndUpdateCache(OzoneManager, ExecutionContext)` is implemented by concrete write requests.
- ACL helpers include overloads of `checkAcls` and FSO-specific `checkACLsWithFSO`.
- Authentication helpers include `getUserInfo`, `getUserIfNotExists`, `createUGI`, `createUGIForApi`, `getRemoteAddress`, and `getHostName`.
- Response/audit helpers include `createErrorOMResponse`, `markForAudit`, `buildAuditMessage`, and `buildVolumeAuditMap`.
- Static key helpers normalize and validate key paths based on filesystem paths and `BucketLayout`.

## Control Flow
RPC-side pre-execution calls `preExecute`, which builds a layout-version protobuf from the OM version manager and fills user info if absent. `getUserInfo` prefers S3 authentication access id mapped to user principal, then Hadoop RPC remote user, then existing gRPC user info. Remote address/host are pulled from Hadoop RPC context or gRPC context keys. `getUserIfNotExists` falls back to the current OM process user and OM RPC server address for internal calls.

`validateAndUpdateCache` is the deterministic state-machine phase: subclasses validate, authorize as needed before entering this method, and update metadata caches without direct RocksDB persistence. The class warns not to bring external dependencies such as Ranger checks into this method because all OM replicas must apply the same deterministic updates.

ACL helpers build `OzoneObj` and `RequestContext`, resolve volume/bucket owners, create UGI from request user info, and delegate to `OzoneManager.checkAcls`, `OzoneAclUtils.checkAllAcls`, or `OmMetadataReader.checkAcls`. FSO ACL checks create an `OzonePrefixPathImpl` to support recursive path checks. Error response helpers map exceptions via `OzoneManagerRatisUtils.exceptionToResponseStatus`, using full stack text for non-OM/non-path exceptions.

## State and Persistence Behavior
`OMClientRequest` does not persist directly. It manages request metadata that will be logged through Ratis and establishes the cache-update contract that produces `OMClientResponse` objects. Persistence occurs later in `OzoneManagerDoubleBuffer` when responses write to RocksDB batches. Per-request state includes the protobuf request, cached UGI, cached remote address, audit builder, and accumulated lock details.

## Dependencies and Integration Points
It integrates with `OzoneManager`, `ExecutionContext`, `OMClientResponse`, `OMLockDetails`, `OzoneManagerRatisUtils`, Hadoop RPC/gRPC context, OM metadata readers, ACL utilities, audit logging, `BucketLayout`, and filesystem path validation utilities. Every concrete write request in OM extends this class.

## Risks and Edge Cases
Calling ACL checks inside `validateAndUpdateCache` can cause HA divergence if external authorizers return different results across replicas. `getRemoteAddress` calls `InetAddress.getByName` on request user info and can throw if malformed. User info fallback for internal calls depends on OM RPC server address being available. Key normalization rejects trailing slashes for layouts that normalize paths; callers must choose `normalizeKeyPath` versus `validateAndNormalizeKey` correctly for existing versus new keys. `buildAuditMessage` writes into a reusable builder, so request objects should not be reused across independent operations.

## Test Signals
Tests should cover preExecute user/layout population, S3 access-id user mapping, gRPC and RPC address extraction, internal-call fallback, ACL helper delegation and owner choice, UGI failure mapping to `UNAUTHORIZED`, exception-to-error-response mapping, audit message contents, key path normalization by bucket layout, trailing slash rejection, and lock detail merging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/OMClientRequest.java -->
