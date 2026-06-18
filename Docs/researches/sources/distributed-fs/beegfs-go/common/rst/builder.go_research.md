# sources/distributed-fs/beegfs-go/common/rst/builder.go

Purpose: implements `JobBuilderClient`, a special RST provider that turns broad user requests over paths, globs, directories, or remote prefixes into concrete BeeRemote job requests.

Important APIs are `NewJobBuilderClient`, `GetJobRequest`, `GenerateWorkRequests`, `ExecuteJobBuilderRequest`, `executeJobBuilderRequest`, and `walkLocalPathInsteadOfRemote`. Most normal provider methods return unsupported operations because the builder does not transfer data.

Control flow: `GetJobRequest` wraps `flex.JobRequestCfg` in a builder job with RST ID 0. `GenerateWorkRequests` recreates a single builder work request. `ExecuteJobBuilderRequest` compiles optional filters, chooses local or remote walking, handles download path mapping, and delegates to `executeJobBuilderRequest`. That function fans out path processing with `errgroup`, increases worker count when the submission channel is draining quickly, emits job requests, and stores resume tokens on the work request when walks hit `maxRequests`.

State includes the builder's submitted/error counters, resume token in `ExternalId`, and access to the shared RST map and mount point. It may persist RST configuration to files/directories when `--update` is set via helpers in `rst.go`.

Dependencies include filesystem walking/filtering, RST provider map, protobuf job messages, errgroup, runtime GOMAXPROCS, and path mapping helpers.

Integration points are BeeRemote job submission, local BeeGFS filesystem traversal, remote provider `GetWalk`, and `BuildJobRequests`.

Risks: concurrency updates are protected only around builder counters and resume state; path-generation logic must stay deterministic across local and remote walks. Filters are rejected for downloads. Reschedule behavior depends on provider resume tokens being correct.

Test signals: no direct builder tests here, but RST tests cover work-request recreation and segment generation; RST integration tests should cover builder walking separately.
