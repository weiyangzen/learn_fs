<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io.go -->
# sources/cloud-native/containerd/pkg/cio/io.go

Purpose: shared container IO abstractions and helpers for creating, attaching, logging, loading, and closing task standard streams.

Important APIs and types: `Config`, `IO`, `Creator`, `Attach`, `FIFOSet`, `Streams`, options `WithStdio`, `WithTerminal`, `WithStreams`, `WithFIFODir`, `NewCreator`, `NewAttach`, `NullIO`, `DirectIO`, `LogURI`, `BinaryIO`, `LogFile`, `LogURIGenerator`, `Load`, and `pipes`.

Control flow and state: `NewCreator` materializes FIFO/named-pipe paths then delegates to platform `copyIO`; absent user streams clear corresponding FIFO paths. `NewAttach` reuses an existing `FIFOSet`. `cio` tracks config, copy waitgroup, closers, and cancel function. `Close` joins closer errors; `Cancel` aborts active operations. Log URI creators return lightweight `logURI` instances without copy goroutines.

Dependencies and integration: used by task/process creation and attach flows. Depends on defaults for FIFO directory, URL/path encoding, and platform files for actual FIFO/named pipe behavior.

Risks and test signals: only one reader should attach to FIFO output. `LogURIGenerator` requires absolute paths and handles Windows drive URI details. Tests cover URI generation and platform FIFO behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io.go -->
