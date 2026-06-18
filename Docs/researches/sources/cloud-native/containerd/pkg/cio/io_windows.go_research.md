<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows.go -->
# sources/cloud-native/containerd/pkg/cio/io_windows.go

Purpose: Windows named-pipe implementation of container IO plus Windows-specific direct IO and terminal logging creators.

Important APIs and functions: `NewFIFOSetInDir`, `copyIO`, `NewDirectIO`, `NewDirectIOFromFIFOSet`, `TerminalLogURI`, and `TerminalBinaryIO`.

Control flow and state: named pipe paths are built under `\\.\pipe`. `copyIO` creates `winio.ListenPipe` listeners for requested streams and launches accept/copy goroutines. Terminal FIFO sets omit stderr, and terminal log creators set stderr to empty because HCSShim requires it.

Dependencies and integration: depends on Microsoft `go-winio` and containerd logging. Used by Windows shims/HCS integration.

Risks and test signals: listener accept errors are logged from goroutines, and cleanup depends on closing listener closers. Windows tests cover FIFOSet path shape and terminal stderr requirements.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows.go -->
