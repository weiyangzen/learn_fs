# sources/distributed-fs/beegfs-go/common/rst/rst.go

Purpose: defines the core Remote Storage Target abstraction, provider construction, common work-request generation helpers, BeeGFS file locking/preparation logic, stub-file helpers, download path mapping, and RST map construction.

Important APIs/types are `Provider`, `SupportedRSTTypes`, `New`, `RecreateWorkRequests`, `generateSegments`, `BuildJobRequests`, `BuildJobRequest`, state predicates like `IsFileLocked` and `IsFileAlreadySynced`, `PrepareFileStateForWorkRequests`, `GetLockedInfo`, `CreateOffloadedDataFile`, `GetOffloadedUrlPartsFromFile`, `CheckEntry`, `IsValidRstId`, `GetDownloadRemotePathDirectory`, `GetDownloadInMountPath`, `NormalizePath`, `GetLastCompletedJobFromRst`, and `GetRstMap`.

Control flow: providers are selected from protobuf RST config. Job requests are recreated from job plus segment data. `BuildJobRequests` gathers locked info, handles fatal/nonfatal preconditions, clones configs per RST, calls provider-specific request building, prepares file state, and decides whether to keep BeeGFS locks. `PrepareFileStateForWorkRequests` handles synced/offloaded no-op states, stub creation, overwrite checks, preallocation, data-state transitions, persistent RST config updates, rollback on error, and external ID generation.

State and persistence behavior is substantial: BeeGFS access flags are set/cleared, file data state may switch between normal/offloaded, stub files contain `rst://id:path`, files may be preallocated or removed on rollback, and RST IDs can be written to file or directory metadata.

Dependencies include BeeGFS messaging and entry CTL packages, filesystem providers, BeeRemote/Flex protobufs, config clients, gRPC status handling, OS/fs/syscall, protobuf cloning, and timestamps.

Integration points are every RST provider, BeeRemote job lifecycle, CTL entry metadata, local filesystem operations, and S3 implementation.

Risks: locking and rollback paths are complex; missed unlocks or partial rollback can leave files locked, preallocated, or with wrong data state. `parseRstUrl` is S3-key oriented. Download path mapping must remain consistent with builder walking. Provider config mutation requires cloning discipline.

Test signals: `rst_test.go` covers request recreation and segments, while `s3_test.go` and `store_test.go` cover provider-specific and store behaviors. Many file-state branches need integration tests with BeeGFS.
