<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/fifosync/fifo_unix.go -->
# sources/cloud-native/containerd/pkg/fifosync/fifo_unix.go

Purpose: Unix FIFO-based interprocess synchronization primitive.

Important APIs and types: `Trigger`, `Waiter`, `NewTrigger`, `NewWaiter`, internal `fifo`, `new`, `Name`, `AsTrigger`, `Trigger`, `AsWaiter`, and `Wait`.

Control flow and state: `new` validates existing path or creates a FIFO with `unix.Mkfifo`. In this implementation `Trigger` opens the FIFO read-only and drains it with `io.ReadAll`, while `Wait` opens it write-only and writes a single byte. The synchronization effect comes from FIFO open/read/write blocking between the two processes.

Dependencies and integration: uses Unix named pipes through `x/sys/unix` and standard file I/O. Useful for coordinating shim/process startup.

Risks and test signals: FIFO open semantics can block depending on reader/writer order. Cleanup is caller-owned; this file does not remove FIFO paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/fifosync/fifo_unix.go -->
