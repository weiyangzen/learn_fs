<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix.go -->
# sources/cloud-native/containerd/pkg/cio/io_unix.go

Purpose: Unix implementation of container IO through filesystem FIFOs.

Important APIs and functions: `NewFIFOSetInDir`, `copyIO`, `openFifos`, `NewDirectIO`, `TerminalLogURI`, and `TerminalBinaryIO`.

Control flow and state: `NewFIFOSetInDir` creates a temp directory under the FIFO root and configures stdin/stdout/stderr paths. `openFifos` creates/opens requested FIFOs with nonblocking flags and cleans up on error. `copyIO` starts goroutines to copy stdin into FIFO and stdout/stderr out to writers, omitting stderr when terminal mode is active. Direct IO exposes FIFO pipes to callers.

Dependencies and integration: uses `github.com/containerd/fifo`, `syscall` flags, and common `cio` buffer pool. Used by shim task IO setup on Unix.

Risks and test signals: FIFO open order and cancellation are deadlock-sensitive. Terminal mode must suppress stderr. Tests cover missing-path errors, terminal stderr omission, temp path layout, and copy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix.go -->
