<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy.go -->
# sources/cloud-native/buildkit/session/filesync/diffcopy.go

Purpose: implements the diffcopy stream transport used by session filesync and local exporter copy operations.

Important APIs, types, and functions: `Stream` abstracts gRPC stream send/recv. `newStreamWriter` creates a buffered writer over a client stream. `streamWriterCloser.Write` chunks messages at 3 MiB to stay below gRPC defaults and handles EOF remote errors. `Close` closes send and waits for receiver EOF. `recvDiffCopy` receives fsutil changes into a destination and updates cache/progress. `syncTargetDiffCopy` receives into a directory root with merge or delete behavior. `writeTargetFile` writes streamed `BytesMessage` data to an output writer.

Control flow and state: streaming functions are stateful over gRPC streams and filesystem destinations. `recvDiffCopy` marks cache support and closes send on clean completion. `syncTargetDiffCopy` creates destination dirs, opens an `os.Root`, maps received file ownership to current uid/gid, and changes differ/merge settings for delete mode.

Dependencies and integration: depends on `tonistiigi/fsutil`, gRPC streams, filesystem APIs, and BuildKit logging. Called from `filesync.go` protocols and exporter copy helpers.

Risks and test signals: stream close semantics are subtle and EOF can mask remote errors. Delete mode replaces merge behavior and must be gated by daemon support. Tests cover delete-mode support gating in `filesync_test.go`; more coverage should include chunked writes, cache updater callbacks, and metadata-only receive.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy.go -->
