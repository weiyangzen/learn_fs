## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonPathCapabilities.java

Purpose: `CommonPathCapabilities` is a final constants-only catalog of capability probe names used by `FileSystem.hasPathCapability(Path, String)` and related filesystem integrations. It centralizes string keys for ACLs, append, checksums, concat, corrupt block listing, path handles, permissions, read-only connectors, snapshots, storage policies, symlinks, truncate, xattrs, batch listing, multipart upload, abortable streams, etags, lease recovery, inconsistent directory listings, bulk delete, and virtual block locations.

Important APIs and types: the class has a private constructor and exports only `public static final String` constants. `FS_EXPERIMENTAL_BATCH_LISTING` is explicitly marked `InterfaceStability.Unstable`. Several constants reference optional interfaces such as `BatchListingOperations`, `Abortable`, `EtagSource`, and `LeaseRecoverable`.

Control flow, state, and persistence: there is no runtime control flow, mutable state, serialization, or persistence. The behavior comes entirely from callers using these exact strings to advertise and query path-scoped behavior.

Dependencies and integration: this file integrates the common filesystem API with concrete stores including HDFS, object stores, and connectors. The constants are consumed by capability policies, stream capability checks, and application code deciding whether to invoke optional operations.

Risks and test signals: risk is mostly compatibility drift. String changes break ecosystem probes, and over-advertising capabilities can cause callers to depend on unsupported semantics. Tests should assert exact constant values, provider responses from `hasPathCapability`, and behavior-gated paths such as etag, abort, bulk delete, and inconsistent listing handling.
