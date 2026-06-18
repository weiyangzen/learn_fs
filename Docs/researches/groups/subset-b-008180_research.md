# subset-b-008180 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-idp-openid.go -->
# sources/object-store/minio/cmd/admin-handlers-idp-openid.go

## Purpose
`admin-handlers-idp-openid.go` implements the OpenID-specific bulk access-key listing admin endpoint: `GET /minio/admin/v3/idp/openid/list-access-keys-bulk`. It complements the generic IAM access-key bulk listing handler by grouping STS and service-account credentials by OpenID configuration and OpenID parent identity rather than by internal MinIO user alone.

## Important APIs, Types, And Functions
The file defines `dummyRoleARN`, used as a synthetic role ARN bucket for claim-policy OpenID providers that do not set an explicit role ARN. The only handler, `adminAPIHandlers.ListAccessKeysOpenIDBulk`, returns encrypted JSON containing `[]madmin.ListAccessKeysOpenIDResp`.

The handler uses `validateAdminSignature` instead of the simpler `validateAdminReq` because it needs both the authenticated credentials and an owner flag, then performs fine-grained `globalIAMSys.IsAllowed` checks. It consumes query/form parameters `users`, `all`, `configName`, `allConfigs`, and `listType`, and it interprets `madmin.AccessKeyListUsersOnly`, `AccessKeyListSTSOnly`, `AccessKeyListSvcaccOnly`, and `AccessKeyListAll`.

The IAM/OpenID integration points are `globalIAMSys.OpenIDConfig.Enabled`, `GetConfigList`, `GetUserIDClaim`, and `GetUserReadableClaim`; credential enumeration comes from `globalIAMSys.ListAllAccessKeys`. Responses use `madmin.OpenIDUserAccessKeys`, `madmin.ServiceAccountInfo`, and `madmin.EncryptData`.

## Control Flow
The handler first rejects uninitialized object/notification layers, invalid signatures, and disabled OpenID configuration. It derives request mode: all users, specific user list, or self-only. `all=true` requires `policy.ListUsersAdminAction`; listing access keys requires `policy.ListServiceAccountsAdminAction`, with `DenyOnly` set for self-only requests so explicit denies still block self-service reads.

It normalizes OpenID config selection: if neither `configName` nor `allConfigs` is provided, it defaults to `madmin.Default`; `all=true` cannot be combined with explicit `users`. It then builds a role-ARN-to-config map from the active OpenID provider configuration list. Configs without role ARNs are mapped under `dummyRoleARN` for claim-based providers. If no target config matches, it returns `ErrAdminNoSuchConfigTarget`.

The access-key scan filters every credential from `ListAllAccessKeys`: it requires a `sub` claim, applies `listType` to distinguish STS versus service accounts, matches role ARN or OpenID policy claim to the requested provider config, optionally matches requested users by parent user or provider ID claim, then accumulates each key under its OpenID config and parent MinIO access key. Finally it sorts users inside each config and sorts configs by name before encrypting the response with the caller's secret key.

## State And Persistence Behavior
This handler is read-only. It does not mutate IAM state, OpenID state, or site-replication state. Its observable state is a point-in-time traversal of persisted or cached IAM credentials and server OpenID provider configuration. It intentionally exposes only access key names and expirations, not secret keys. Response confidentiality depends on `madmin.EncryptData(cred.SecretKey, data)` matching the admin client protocol.

The most important state distinction is between OpenID STS keys and OpenID-created service accounts. The handler classifies an access key by `accessKey.IsServiceAccount()` after confirming OpenID claims. It also treats OpenID credentials without a `roleArn` claim but with the OpenID IAM policy claim as belonging to the synthetic config role bucket.

## Dependencies And Integration Points
The file depends on `madmin-go/v3` response and list-type constants, MinIO's string-set helper, MinIO policy action constants, global IAM and server config state, admin signature validation, and shared JSON error helpers. It integrates with the generic access-key listing behavior in `admin-handlers-users.go` but differs by using OpenID provider config metadata and OpenID claims to group results.

## Risks And Test Signals
Security risk concentrates around user filtering and self-service permissions. The handler must not allow a user to infer other users' OpenID access keys without `ListUsersAdminAction` and `ListServiceAccountsAdminAction`. The `DenyOnly` path for self-only access is a notable safeguard and should be preserved if this code is refactored.

Correctness risk exists around providers without role ARN, mixed multiple OpenID configs, and custom ID/readable claims. `dummyRoleARN` can group all claim-based providers together if multiple configs are claim-based; the surrounding config map stores the dummy ARN once, so multi-config claim-policy setups require care. There are no direct tests in this work item for this file; indirect signals come from OpenID/IAM admin tests elsewhere and from generic access-key listing semantics in `admin-handlers-users.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-idp-openid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-pools.go -->
# sources/object-store/minio/cmd/admin-handlers-pools.go

## Purpose
`admin-handlers-pools.go` implements admin APIs for erasure-server-pool lifecycle operations: decommission start/cancel/status/list and rebalance start/status/stop. These endpoints expose cluster topology operations that are only valid for distributed erasure deployments with multiple server pools.

## Important APIs, Types, And Functions
The file defines two package-level errors, `errRebalanceDecommissionAlreadyRunning` and `errDecommissionRebalanceAlreadyRunning`, to enforce mutual exclusion between rebalance and decommission operations.

Primary handlers are `StartDecommission`, `CancelDecommission`, `StatusPool`, `ListPools`, `RebalanceStart`, `RebalanceStatus`, and `RebalanceStop`. The helper `proxyDecommissionRequest` forwards decommission operations to the correct node when the selected endpoint is remote or overridden by `_MINIO_DECOM_ENDPOINT_HOST`.

The code relies on `validateAdminReq` with `policy.DecommissionAdminAction`, `policy.ServerInfoAdminAction`, or `policy.RebalanceAdminAction`. It type-asserts the object layer to `*erasureServerPools`, uses `globalEndpoints` for pool resolution and legacy topology checks, uses `globalProxyEndpoints` and `proxyRequestByNodeIndex` for routing, and calls methods such as `Decommission`, `DecommissionCancel`, `Status`, `IsDecommissionRunning`, `IsRebalanceStarted`, `initRebalanceMeta`, `StartRebalance`, and `saveRebalanceStats`.

## Control Flow
Decommission start validates that the server is initialized, rejects legacy endpoint style, requires a multi-pool `*erasureServerPools` backend, rejects if decommission or rebalance is already active, parses the path pool list either as numeric pool IDs or endpoint-set names, validates each pool index against `z.serverPools`, then either proxies to the owning endpoint or calls `z.Decommission(ctx, poolIndices...)`.

Cancel and status handlers perform similar legacy/backend/index validation for a single pool. Cancel proxies if needed, otherwise calls `DecommissionCancel`. Status calls `pools.Status` and JSON-encodes one `PoolStatus`. `ListPools` loops over all `globalEndpoints`, collects every pool status, and encodes the slice.

`RebalanceStart` is coordinated from the first node of the first pool to serialize concurrent start attempts. If this node is remote, it proxies to the matching proxy endpoint. It then rejects unsupported single-pool or non-erasure-pool backends, rejects running decommission or already-started rebalance, lists all buckets, initializes rebalance metadata with the bucket names, starts the local rebalance routine, returns the generated rebalance ID, and notifies peers to load rebalance metadata.

`RebalanceStatus` also proxies to the first pool's first node for a consistent view. It maps `errRebalanceNotStarted` and `errConfigNotFound` to `ErrAdminRebalanceNotStarted`, logs other status failures, and JSON-encodes the rebalance status. `RebalanceStop` stops rebalance through the notification system, returns no-content success, persists stopped stats, and asks peers to reload rebalance metadata.

## State And Persistence Behavior
Pool decommission and rebalance are persistent cluster operations. Decommission affects the erasure-server-pool state machine and object migration for selected pools. Rebalance initialization writes rebalance metadata, and `RebalanceStop` persists stopped state through `saveRebalanceStats`. Notification calls (`LoadRebalanceMeta`, `StopRebalance`) propagate changes across peer nodes.

The handlers intentionally centralize rebalance start/status on the first pool's first node so concurrent or distributed admin clients do not create divergent rebalance views. Decommission routing uses the selected pool's first endpoint, or `_MINIO_DECOM_ENDPOINT_HOST` when explicitly configured, to run the operation on an appropriate cluster node.

## Dependencies And Integration Points
Dependencies include MinIO mux route variables, environment lookup, policy action constants, global endpoint/proxy topology, admin error mapping, and erasure-pool implementation types. The handlers integrate directly with backend pool lifecycle code and the notification subsystem used to fan out rebalance state.

These APIs are not meaningful for filesystem, single-pool erasure, or legacy endpoint layouts and therefore return `ErrNotImplemented` in those modes.

## Risks And Test Signals
Operational risk is high because these APIs move data and affect cluster capacity. Important safeguards include legacy-topology rejection, backend type checks, multi-pool checks, pool-index validation, rebalance/decommission mutual exclusion, and coordinated proxy routing. A bug in pool lookup or proxy target selection could start work on the wrong pool or return inconsistent status.

No tests for this file are included in this work item. Likely test signals live in integration/admin suites that exercise decommission and rebalance in distributed erasure setups. Manual validation should include by-name and by-id pool addressing, remote first-node proxying, already-running errors, single-pool rejection, and rebalance metadata reload notifications.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-pools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-site-replication.go -->
# sources/object-store/minio/cmd/admin-handlers-site-replication.go

## Purpose
`admin-handlers-site-replication.go` implements MinIO admin and internal peer endpoints for site replication. It covers joining/removing/editing peer clusters, peer-applied IAM and bucket metadata replication, status/metainfo reporting, resync control, and network performance/dev-null utilities used by site-replication diagnostics.

## Important APIs, Types, And Functions
External admin handlers include `SiteReplicationAdd`, `SiteReplicationInfo`, `SiteReplicationStatus`, `SiteReplicationMetaInfo`, `SiteReplicationEdit`, `SiteReplicationRemove`, `SiteReplicationResyncOp`, `SiteReplicationDevNull`, and `SiteReplicationNetPerf`.

Internal peer handlers include `SRPeerJoin`, `SRPeerBucketOps`, `SRPeerReplicateIAMItem`, `SRPeerReplicateBucketItem`, `SRPeerGetIDPSettings`, `SRPeerEdit`, `SRStateEdit`, and `SRPeerRemove`. Option parsers `getSRAddOptions`, `getSREditOptions`, and `getSRStatusOptions` translate query parameters into `madmin` option structures. `parseJSONBody` centralizes request-body reading, optional `madmin.DecryptData`, and JSON unmarshalling into site-replication request types.

The core dependency is `globalSiteReplicationSys`, which performs peer cluster mutations, applies replicated IAM/bucket metadata, calculates status, manages resync, exposes IDP settings, and handles network performance counters.

## Control Flow
Add/edit APIs validate admin permissions, decrypt client-supplied JSON with the authenticated secret key, parse `madmin.PeerSite` or `madmin.PeerInfo`, apply option flags, call `globalSiteReplicationSys.AddPeerClusters` or `EditPeerCluster`, and return JSON status. Peer join/edit/remove/state endpoints parse unencrypted internal peer JSON and delegate to `PeerJoinReq`, `PeerEditReq`, `InternalRemoveReq`, or `PeerStateEditReq`.

`SRPeerBucketOps` dispatches bucket operations based on route variable `operation`: make with versioning, configure replication, delete or force delete, and purge-deleted-bucket. It builds `MakeBucketOptions` from query parameters, including `createdAt`, lock, versioning, and force-create flags. `SRPeerReplicateIAMItem` dispatches `madmin.SRIAMItem` variants to peer handlers for policy, service account, policy mapping, STS credential, IAM user, and group changes. Policy bytes are parsed and empty policies are treated as nil/deletion semantics.

`SRPeerReplicateBucketItem` validates a bucket name and dispatches `madmin.SRBucketMeta` variants for bucket policy, quota, versioning, tags, object lock, SSE, lifecycle, or generic metadata update. Policy and quota payloads are parsed before peer handlers are called.

Status and metainfo APIs parse `madmin.SRStatusOptions`. `SiteReplicationStatus` defaults to buckets/users/policies/groups/ILM expiry rules when no option is specified for backward compatibility, then suppresses `ILMExpiryStats` unless at least one site has ILM expiry replication enabled. Resync op parses a peer site and dispatches start or cancel by route operation.

The dev-null and netperf endpoints are diagnostic paths. `SiteReplicationDevNull` streams request bytes into discard in 128 KiB chunks while updating `globalSiteNetPerfRX.RX`, and it treats early non-EOF errors as useful network instability logs. `SiteReplicationNetPerf` enforces a minimum duration and gob-encodes the result from `siteNetperf`.

## State And Persistence Behavior
Most handlers are stateful cluster operations. Peer add/edit/remove and state edit mutate the site-replication configuration and peer state. Peer IAM and bucket metadata endpoints apply replicated state from other clusters into local IAM stores and bucket metadata stores, using `UpdatedAt` timestamps carried in madmin replication payloads. Resync start/cancel updates resync state for a peer.

Request encryption is asymmetric by call type: client-initiated add/edit uses the caller's secret key, while many internal peer replication calls pass an empty encryption key to `parseJSONBody` and expect plain JSON over authenticated peer-admin channels. Bucket make/delete operations deliberately preserve metadata such as creation time and versioning/lock flags so peers can converge.

The diagnostic endpoints mutate only in-memory network performance counters and connection state, not persistent site-replication config.

## Dependencies And Integration Points
The file depends on `madmin-go/v3` site-replication request/response types, MinIO policy action constants, bucket metadata parsers, IAM policy parsers, mux route variables, humanize sizing constants, and internal discard helpers. It integrates with the IAM handlers in `admin-handlers-users.go` through site-replication hooks: those handlers emit `madmin.SRIAMItem` changes that this file's peer endpoint can apply on remote sites.

It also integrates with bucket lifecycle/metadata systems through replicated bucket metadata handlers and with network diagnostics through `globalSiteNetPerfRX` and `siteNetperf`.

## Risks And Test Signals
The main risks are authorization mistakes between external and internal endpoints, malformed or malicious replication payloads, and divergence caused by incorrectly parsed empty policy/quota payloads. `parseJSONBody` reads the whole body without an explicit size limit in this file, so callers rely on upstream admin limits and trusted peer channels. Peer endpoints that accept unencrypted payloads must remain protected by admin signature validation and site-replication operation policies.

Backward-compatibility behavior in `SiteReplicationStatus` is intentional: removing default status flags would change older clients. ILM-expiry stats suppression is another compatibility and response-size concern.

No direct tests for this file are included in the work item. Indirect signals should include site-replication integration tests for peer add/join/remove, IAM replication, bucket metadata replication, status filters, resync start/cancel, encrypted add/edit payloads, and netperf/dev-null behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-site-replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-users-race_test.go -->
# sources/object-store/minio/cmd/admin-handlers-users-race_test.go

## Purpose
`admin-handlers-users-race_test.go` contains the slow IAM concurrency test suite for deleting users while their credentials are still attempting S3 access. Despite the filename, it is explicitly excluded under Go's `-race` build tag because the suite is too slow and can hit context deadlines when the race detector is enabled.

## Important APIs, Types, And Functions
The file defines `runAllIAMConcurrencyTests`, `TestIAMInternalIDPConcurrencyServerSuite`, and the method `TestSuiteIAM.TestDeleteUserRace`. It reuses `TestSuiteIAM` and helper assertions from `admin-handlers-users_test.go`.

The test matrix covers ErasureSD, ErasureSD with TLS, Erasure, and ErasureSet backends, each with and without etcd IAM backend. It skips Windows via `globalWindowsOSName`.

`TestDeleteUserRace` uses `madmin.AdminClient` methods `AddCannedPolicy`, `SetUser`, `AttachPolicy`, and `RemoveUser`, a MinIO S3 client for bucket access, and `github.com/minio/pkg/v3/sync/errgroup` to run many deletion/access checks concurrently.

## Control Flow
The suite setup mirrors the main IAM test suite: initialize a MinIO test server, optionally configure etcd-backed IAM, run the concurrency test, then tear down. `TestDeleteUserRace` creates a bucket, adds a policy permitting list/get/put on that bucket, creates 50 users, attaches the policy to every user, then starts 50 goroutines.

Each goroutine builds a user S3 client from that user's credentials, removes the user through the admin client, and then asserts that the deleted user's client can no longer list objects in the bucket. The errgroup aggregates remove/list failures and fails the test on any non-empty error set.

## State And Persistence Behavior
The test exercises concurrent IAM mutation and credential invalidation. It creates persistent users, policy mappings, and a canned policy, then concurrently deletes users while immediately attempting S3 authorization with credentials that were valid moments earlier. With etcd enabled, the same behavior is exercised through the etcd-backed IAM store; otherwise it uses the local IAM backend configured by the test server.

The key persistence signal is that `RemoveUser` must fully remove or invalidate the user's IAM identity and policy mapping quickly enough that subsequent authorization fails. The test does not explicitly clean up the policy or bucket because the test server teardown owns fixture cleanup.

## Dependencies And Integration Points
The file depends on the IAM admin APIs implemented in `admin-handlers-users.go`, the shared `TestSuiteIAM` setup in `admin-handlers-users_test.go`, MinIO S3 client behavior, madmin client behavior, and the optional `_MINIO_ETCD_TEST_SERVER` setup path. It integrates with backend variants to catch differences between local and etcd IAM persistence.

## Risks And Test Signals
The test is expensive and time-sensitive: it uses a 90-second context and 50 concurrent user removals, and it is disabled under race-detector builds. A failure can indicate IAM cache invalidation races, stale policy mappings, etcd propagation delays, or incorrect `RemoveUser` cleanup. The strongest signal is that a deleted credential must receive an error when listing the bucket immediately after deletion, even under concurrent admin operations.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-users-race_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-users.go -->
# sources/object-store/minio/cmd/admin-handlers-users.go

## Purpose
`admin-handlers-users.go` is the main MinIO admin IAM handler file. It implements user, group, policy, service-account/access-key, temporary-account, token-revocation, account-info, and IAM import/export endpoints under `/minio/admin/v3`. It is the HTTP boundary between authenticated admin clients and `globalIAMSys`, with explicit checks for internal users, LDAP users, OpenID-derived credentials, service accounts, STS credentials, policy mappings, and site-replication hooks.

## Important APIs, Types, And Functions
User and group handlers include `RemoveUser`, `ListBucketUsers`, `ListUsers`, `GetUserInfo`, `UpdateGroupMembers`, `GetGroup`, `ListGroups`, `SetGroupStatus`, `SetUserStatus`, and `AddUser`.

Access-key and service-account handlers include `TemporaryAccountInfo`, `AddServiceAccount`, `UpdateServiceAccount`, `InfoServiceAccount`, `ListServiceAccounts`, `DeleteServiceAccount`, `ListAccessKeysBulk`, and `InfoAccessKey`. `commonAddServiceAccount` centralizes encrypted request parsing, target-user defaulting, expiration normalization, duration-condition injection, self-service versus admin permission checks, and session policy parsing for service-account creation.

Policy handlers include `InfoCannedPolicy`, `ListBucketPolicies`, `ListCannedPolicies`, `RemoveCannedPolicy`, `AddCannedPolicy`, deprecated `SetPolicyForUserOrGroup`, modern `ListPolicyMappingEntities`, and `AttachDetachPolicyBuiltin`. `setReqInfoPolicyName` annotates audit request info with policy names.

IAM import/export uses constants for `iam-assets/policies.json`, `users.json`, `groups.json`, `svcaccts.json`, `user_mappings.json`, `group_mappings.json`, and `stsuser_mappings.json`, plus `iamExportFiles`, `ExportIAM`, `ImportIAM`, `ImportIAMV2`, and shared `importIAM`.

## Control Flow
Most mutating handlers follow a common structure: validate server initialization and admin signature/permission, parse route variables and encrypted or plain JSON payload, reject invalid identity classes, call `globalIAMSys`, return an madmin-compatible response, then emit a site-replication IAM change hook when appropriate.

User handlers forbid root-user removal, self-removal, temporary-user modification through regular-user APIs, service-account modification through user APIs, and internal user creation when LDAP is enabled. `AddUser` supports self password updates only through a deny-only permission check, rejects invalid UTF-8 and leading/trailing-space access keys, decrypts `madmin.AddOrUpdateUserReq`, and persists through `globalIAMSys.CreateUser`.

Group handlers reject temporary credentials and root credentials as members. Adding a new group rejects names with leading/trailing spaces, and internal group manipulation is disabled in LDAP mode. Status and membership changes emit `madmin.SRIAMItemGroupInfo` replication events.

Service-account creation first parses an encrypted `madmin.AddServiceAccountReq` in `commonAddServiceAccount`. It truncates expiration to seconds, rejects access keys with leading/trailing spaces, validates client-side request shape server-side, injects `svc:DurationSeconds` into condition values when expiration is set, and uses `DenyOnly` for self-service creation. `AddServiceAccount` then resolves the target user across internal IDP, requestor-derived credentials, LDAP DN lookup, and OIDC/LDAP claims before calling `globalIAMSys.NewServiceAccount`. Updates require `policy.UpdateServiceAccountAdminAction`; self-update is intentionally not allowed pending redesign. Info/list/delete allow a narrower self-service path by comparing the caller's parent user with the service account parent when the caller lacks broad list/remove permissions.

Access-key listing (`ListAccessKeysBulk`) supports all-users, explicit users, and self-only modes. All-users requires list-users permission, and access-key listing requires list-service-accounts permission with deny-only behavior for self mode. It can list STS keys, service accounts, both, or neither based on `listType`, and encrypts the response with the caller secret.

Policy flows validate policy names, content length, JSON policy syntax, non-empty policy version, LDAP DN normalization for LDAP mappings, and root/temporary-user restrictions for legacy mappings. Modern attach/detach requires octet-stream encrypted request bodies, validates `madmin.PolicyAssociationReq`, calls `PolicyDBUpdateBuiltin`, returns encrypted attached/detached results, and records policy names in audit context.

`AccountInfoHandler` computes account-level console data: bucket access by checking list/location and put permissions, bucket usage/quota/object-lock/replication/tagging details, backend info, and effective policy. Effective policy comes from consoleAdmin for root or external authZ plugin, role policy for OpenID role ARN, policies embedded in OpenID claims, or IAM policy DB for internal/LDAP users and groups.

`ExportIAM` streams a zip response containing policies, internal users, groups, service accounts, and policy mappings. It reads lower-level IAM store data directly, skips the site-replicator service account, includes service-account claims/session policies/metadata, and uses deflated zip entries under `iam-assets`. `importIAM` reads the zip into memory, opens each known asset if present, imports policies first, then users, groups, service accounts, user mappings, group mappings, and STS-user mappings. It supports LDAP normalization/skipping for service accounts and mappings, deletes an existing service account before clean re-import, accumulates `added`, `removed`, `skipped`, and `failed` entities, and returns a structured `madmin.ImportIAMResult` only for v2.

## State And Persistence Behavior
The file is state-heavy. It mutates IAM users, service accounts, temporary-account token state, groups, policies, and policy mappings through `globalIAMSys`. Some read paths use high-level IAM APIs, while export/import reaches into `globalIAMSys.store` to load users, groups, and mapped policies. IAM state may be backed by local object storage/config or etcd depending on deployment.

Site replication is a cross-cutting persistence integration. User, group, policy, policy-mapping, and non-root service-account changes call `globalSiteReplicationSys.IAMChangeHook` with `madmin.SRIAMItem` payloads and timestamps so peer clusters can converge. Root-owned service accounts are deliberately not replicated in several paths. The site-replicator service account is protected from deletion while site replication is enabled and omitted from export.

Encryption is part of the admin API state contract. Many madmin requests and responses use `madmin.EncryptData`/`DecryptData` with the requestor's secret key, while some older policy endpoints return plain JSON. Content-length and maximum-size checks protect encrypted config bodies and policy bodies in several endpoints.

Derived credentials are handled carefully. The code distinguishes `cred.AccessKey`, `cred.ParentUser`, groups, claims, service-account status, STS status, OpenID role/policy claims, LDAP normalized DNs, and root credentials. Authorization state often uses parent-user policy for derived credentials while still recording the derived access key for request context.

## Dependencies And Integration Points
The file depends on `madmin-go/v3`, MinIO internal `auth`, DNS/bucket federation config, logger request info, mux route variables, LDAP helpers, policy parsing/evaluation, zip compression, `xsync` mapped-policy maps, global IAM/site-replication/bucket metadata systems, admin error mapping, and shared helper functions for condition values and provider inference.

It integrates with `admin-handlers-site-replication.go` through `madmin.SRIAMItem` payloads, with `admin-handlers-idp-openid.go` through shared access-key and OpenID claim conventions, with S3 authorization through policy evaluation, and with admin clients in `madmin-go` through encrypted request/response types.

## Risks And Test Signals
This file has a large security surface. High-risk areas include self-service denial semantics, service-account policy escalation, target-user confusion for derived credentials, LDAP DN normalization, OpenID claim-policy handling, root-account protections, import overwrites, and site-replication hook omissions. The code contains explicit regression protections against regular users escalating via `AddUser`, service accounts updating their own policy, and restricted service accounts creating broader service accounts.

Operational risks include whole-body reads for IAM import, partial import behavior that can add some entities before failing later, direct store access during export/import, and differences between local IAM and etcd-backed IAM. `ImportIAMV2` improves observability by returning added/removed/skipped/failed entities, but non-v2 import has no structured success body.

The companion tests in this work item provide strong signals for internal IDP user lifecycle, policy create/delete/validation, default policies, group membership/status effects, service-account creation/list/info/session-policy/secret/status/delete behavior, `svc:DurationSeconds` conditions, access-management-plugin behavior, user policy escalation regression, and two service-account privilege escalation regressions. The race test adds a concurrent deletion/invalidation signal. Missing direct signals in this subset include OpenID access-key listing, IAM import/export, token revocation, LDAP-specific attach/detach/import normalization, and site-replication hook delivery.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-users.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-users_test.go -->
# sources/object-store/minio/cmd/admin-handlers-users_test.go

## Purpose
`admin-handlers-users_test.go` is the primary black-box integration test suite for MinIO admin IAM handlers. It starts real MinIO test servers across backend variants, drives madmin and S3 clients, and verifies that users, groups, policies, service accounts, plugin authorization, and selected privilege-escalation regressions behave as intended for the internal IDP.

## Important APIs, Types, And Functions
The central fixture is `TestSuiteIAM`, embedding `TestSuiteCommon` and holding endpoint, admin client, S3 client, backend description, and etcd-backend flag. Setup helpers include `newTestSuiteIAM`, `iamSetup`, `setUpEtcd`, `SetUpSuite`, `RestartIAMSuite`, `getAdminClient`, and `getUserClient`. `iamTestSuites` constructs the backend matrix: ErasureSD, ErasureSD TLS, Erasure, and ErasureSet, each with and without etcd.

Top-level suites are `TestIAMInternalIDPServerSuite` and `TestIAM_AMPInternalIDPServerSuite`. Test methods include `TestUserCreate`, `TestUserPolicyEscalationBug`, `TestAddServiceAccountPerms`, `TestPolicyCreate`, `TestCannedPolicies`, `TestGroupAddRemove`, `TestServiceAccountOpsByUser`, `TestServiceAccountDurationSecondsCondition`, `TestServiceAccountOpsByAdmin`, `TestServiceAccountPrivilegeEscalationBug`, `TestServiceAccountPrivilegeEscalationBug2_2025_10_15`, `SetUpAccMgmtPlugin`, and `TestAccMgmtPlugin`.

Assertion helpers cover IAM user creation/info negative checks, service-account create/list/info/session-policy/secret/status/delete, S3 list/upload/download/delete expectations, object tag/head/version helpers, and random credential generation.

## Control Flow
`TestIAMInternalIDPServerSuite` skips Windows, then runs every IAM scenario against every suite variant. Setup may configure etcd using `_MINIO_ETCD_TEST_SERVER`, restart the IAM suite, and rebuild clients. Each test uses a context with a 30-second timeout.

`TestUserCreate` covers create/list, policy attach, S3 access, secret-key update invalidating old credentials, disable/enable effects, and deletion invalidating credentials. `TestUserPolicyEscalationBug` crafts a signed raw `add-user` request as the user being updated and verifies the user cannot gain consoleAdmin-like bucket deletion despite receiving HTTP 200 for password/status update behavior.

Policy tests add valid and invalid JSON policies, attach them to users, prove exact S3 permissions, verify default policy presence, allow overwriting `readwrite`, reject comma-containing policy names, and reject deleting a policy still attached to a user.

Group tests create a user and group, attach a policy to the group, verify list/get group details, disable and re-enable group access, reject deleting a non-empty group, remove the member, and finally delete the empty group.

Service-account tests split admin-created and user-created flows. They verify service accounts appear in listing, info reports parent/status/implied policy, S3 access works, session policy can restrict and later allow access, secret-key updates invalidate old credentials, status updates disable access, deletion invalidates credentials, and non-admin users cannot create accounts for other users. The duration-condition test verifies `svc:DurationSeconds` policy evaluation by allowing a 30-minute service account and rejecting a two-hour one.

Privilege escalation tests create restricted service accounts for root and regular users, then verify they cannot update their own policy to full S3 access and cannot create broader service accounts bypassing their sub-policy. The access-management-plugin suite configures the policy plugin from `_MINIO_POLICY_PLUGIN_ENDPOINT`, restarts, verifies plugin-denied object upload, verifies service-account admin flows under plugin authorization, and confirms session policies are ignored when enforcement is delegated to the plugin.

## State And Persistence Behavior
The tests create real IAM users, canned policies, groups, service accounts, buckets, and objects in each temporary test server. When etcd is configured, IAM state is persisted through a unique etcd path prefix and the server is restarted to use that backend. Many assertions validate state transitions by performing S3 operations with old and new credentials rather than only inspecting admin responses.

The suite exercises both high-level admin state (`ListUsers`, `ListGroups`, `InfoServiceAccount`) and authorization side effects (bucket list, put, delete, old secret invalidation, disabled account denial). It uses server teardown for most cleanup, with some privilege-regression tests using defers for explicit bucket/user/service-account cleanup.

## Dependencies And Integration Points
The test file depends on `madmin-go/v3`, `minio-go/v7`, static V4 credentials, request signing, S3 URL encoding utilities, MinIO auth credential generation, environment variables for etcd and policy plugin, and shared test server infrastructure. It tests the HTTP handlers in `admin-handlers-users.go` through official admin clients plus a few raw signed requests.

The plugin suite integrates with the example external access-management plugin contract, assuming it denies `s3:Put*` for non-root accounts. The service-account assertions integrate admin API behavior with actual S3 authorization to catch policy-evaluation bugs.

## Risks And Test Signals
The suite is broad but expensive because it multiplies scenarios by backend and optional etcd variants. It skips Windows, so Windows-specific IAM behavior is not covered here. Plugin and etcd paths are conditional on environment variables, which means those important modes may be skipped in ordinary local runs.

Strong signals include credential invalidation after password update, disabled/deleted user denial, invalid policy rejection, attached-policy delete rejection, group disable revoking access, service-account session-policy enforcement, `svc:DurationSeconds` condition enforcement, access-management-plugin delegation, and explicit privilege escalation regressions. Missing coverage in this file includes IAM import/export, token revocation, LDAP-specific workflows, OpenID bulk listing, and site-replication hook verification.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-users_test.go -->
