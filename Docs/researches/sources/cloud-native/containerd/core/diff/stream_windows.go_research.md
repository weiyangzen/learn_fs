# sources/cloud-native/containerd/core/diff/stream_windows.go

Purpose: Windows implementation of external binary stream processors.

Important APIs/types: same processor surface as Unix, but payload delivery uses a named pipe path exposed through `STREAM_PROCESSOR_PIPE`. `getUiqPath` creates and removes a temp directory to get a unique path component.

Control flow and state: when payload exists, it creates a winio named pipe, starts a goroutine to accept a connection and copy marshaled payload bytes, sets media type env, connects stdin/stdout/stderr, starts the process, and returns a `binaryProcessor` that reads stdout and tracks process completion.

Dependencies and integration: `github.com/Microsoft/go-winio`, os/exec, typeurl/protobuf marshal, containerd logging, and diff stream registry.

Risks: payload goroutine logs but does not propagate accept/copy errors to processor construction. Named pipe cleanup is listener close only. Like Unix, stderr is buffered and errors require `Err`/`Wait`. `Close` kills the process.

Test signals: no direct tests. Windows integration tests are needed for named pipe payload compatibility and cancellation behavior.
