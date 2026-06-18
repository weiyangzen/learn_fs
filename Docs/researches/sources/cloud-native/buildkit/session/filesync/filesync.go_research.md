<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.go -->
# sources/cloud-native/buildkit/session/filesync/filesync.go

Purpose: main session file synchronization implementation for sending local sources to the daemon and copying daemon output back to callers.

Important APIs, types, and functions: constants define metadata keys for filters, dir names, exporter metadata, exporter ids, and multi-platform transfer support. `NewFSSyncProvider`, `DirSource`, `StaticDirSource`, and `fsSyncProvider` expose client local directories to sessions. `FSSync` requests a supported protocol, sends include/exclude/follow metadata, opens a stream, and receives into a destination. `WithFSSync`, `WithFSSyncDir`, `WithFSSyncDirDelete`, `NewFSSyncTarget`, and `SyncTarget` define local exporter receive targets. `CopyToCaller` streams an fsutil FS to the caller. `CopyFileWriter` returns a streaming writer. `encodeOpts` and `decodeOpts` preserve non-ASCII metadata values for gRPC headers.

Control flow and state: providers maintain local directory sources plus one-shot progress callback/done channel. SyncTarget maintains maps from exporter id to file callbacks or output directories. `FSSync` discovers supported methods through session method URLs, injects outgoing metadata, then delegates receive to the protocol. `SyncTarget.DiffCopy` chooses a target by metadata id, gates delete mode on multi-platform support metadata, and either receives into a directory or writes a single output stream.

Dependencies and integration: heavily integrates with BuildKit session callers, generated FileSync/FileSend gRPC services, `tonistiigi/fsutil`, gRPC metadata, and BuildKit logging. Used by local source transfer and local exporter transfer paths.

Risks and test signals: one-shot callback fields on `fsSyncProvider` are not protected by a mutex. Metadata overwrites are logged but still mutate caller-provided metadata. Non-ASCII header encoding only encodes non-ASCII characters, relying on gRPC header tolerance for other ASCII. Existing tests cover include patterns and delete-mode support gating. Additional tests should cover encoded metadata round trips, multiple exporter ids, callback races, and copy-to-caller error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.go -->
