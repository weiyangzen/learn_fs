<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/buildhistory.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/buildhistory.go

Purpose: implements the build history queue: active/completed record storage, garbage collection, blob import/export, leases, status replay, deletion, finalization, and event listening.

Important APIs and types: `QueueOpt`, `Queue`, `StatusImportResult`, `NewQueue`, `gc`, `clearOrphans`, `delete`, `UpdateRef`, `Status`, `Update`, `Delete`, `OpenBlobWriter`, `Writer`, `ImportError`, `ImportStatus`, `AcquireFinalizer`, `Finalize`, and `Listen`.

Control flow: `NewQueue` configures defaults, creates a separate `_history` containerd namespace, migrates v1 data if needed, starts orphan cleanup/GC loops, and closes pubsub after graceful stop when no active finalizers remain. `Update` tracks active records for STARTED and persists COMPLETE records. `update` writes the protobuf record into Bolt and attaches all referenced blobs to a per-record lease. `ImportStatus` serializes streamed solve statuses as length-prefixed protobuf messages and counts cached/completed/total/warnings. `Listen` returns active, completed, filtered/limited, and live pubsub events while respecting ref deletion deferral.

State and persistence: active records, finalizers, listener ref counts, and deleted refs are in memory under `mu`. Completed records live in Bolt bucket `_records`; blob content and leases live in isolated containerd history namespace.

Dependencies and integration: used by llbsolver build history finalizer and control API history endpoints. Integrates with content store, lease manager, Bolt transactor, grpc error conversion, filters, and pubsub.

Risks and test signals: risks include lease/blob consistency, GC criteria, deletion while listeners hold refs, indefinite goroutines, and status stream framing. Tests in this subset cover filters and pubsub, not full queue persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/buildhistory.go -->
