# sources/distributed-fs/beegfs-go/common/rst/jobrequest.go

Purpose: prepares and submits BeeRemote job requests from user-facing `flex.JobRequestCfg` values.

Important APIs/types are `JobResponse`, `SubmitJobRequest`, `prepareJobRequests`, `mountPathInfo`, and `getMountPathInfo`.

Control flow: `SubmitJobRequest` creates a BeeRemote client, spawns a goroutine, prepares one or more `beeremote.JobRequest`s, submits each through `SubmitJob`, and streams `JobResponse`s. Unavailable gRPC submit errors are marked fatal. `prepareJobRequests` resolves the BeeGFS mount, normalizes the path, sets default remote path/priority, validates filter feature support, decides whether a builder job is needed, and otherwise builds provider-specific requests from explicit RST ID, stub-file contents, or entry metadata RST IDs.

State and persistence behavior: preparation may mutate the supplied config with normalized path, remote path, priority, and remote target. It reads BeeGFS entry details, stub contents, mappings, and remote registry capabilities; it does not itself persist data except through later builder/RST flows.

Dependencies include CTL config clients, filesystem filters, registry feature checks, scheduler default priority, entry/mapping utilities, BeeRemote protobuf/gRPC clients, and OS/stat metadata.

Integration points are CLI request submission, BeeRemote RPCs, local BeeGFS metadata, stub files, RST provider map construction, and job builder fallback.

Risks: config mutation can surprise callers that reuse a cfg. `SubmitJobRequest` continues after `prepareJobRequests` error and may iterate a nil slice after sending one error response. Filter support depends on remote registry availability. Ambiguous stub/RST cases are pushed to later helpers.

Test signals: no direct tests in this subset; behavior is exercised by higher-level RST/CTL flows.
