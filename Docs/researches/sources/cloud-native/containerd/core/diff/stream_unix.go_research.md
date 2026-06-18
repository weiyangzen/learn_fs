# sources/cloud-native/containerd/core/diff/stream_unix.go

Purpose: Unix implementation of external binary stream processors.

Important APIs/types: `NewBinaryProcessor` starts an external command that transforms a stream from input media type to return media type. `binaryProcessor` implements `StreamProcessor`, `RawProcessor`, `Err`, `Wait`, and cleanup methods.

Control flow and state: it constructs `exec.CommandContext`, inherits environment, appends custom env and `STREAM_PROCESSOR_MEDIATYPE`, optionally marshals typeurl payload into an extra file descriptor, connects input from either a raw file or stream, pipes stdout to the returned processor reader, captures stderr, starts the process, closes duplicated handles, and records exit errors asynchronously.

Dependencies and integration: os/exec, pipes, protobuf marshal of typeurl payloads, and the diff stream registry.

Risks: `Close` kills the process after closing the read pipe; consumers must call `Err` or `Wait` to observe processor failures. Payload delivery via extra file descriptor requires processor agreement. Stderr is fully buffered in memory. RawProcessor input file is closed after start.

Test signals: no direct unit tests. Integration should cover processor exit errors, payload fd, and cancellation.
