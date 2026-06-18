# sources/cloud-native/moby/daemon/logger/plugin_unix.go

Purpose: Unix/FreeBSD FIFO stream creation for logging plugins.

Important APIs/types/functions: `openPluginStream`.

Control flow/state/persistence: opens the adapter FIFO path with read/write, create, nonblocking flags and mode 0700. Opening read/write avoids broken pipe errors if the plugin side has not opened the FIFO.

Dependencies/integration: uses `containerd/fifo`, `x/sys/unix`, and `pluginAdapter`.

Risks: FIFO semantics differ by platform; if plugin never reads, buffers can still fill and block the container path.

Test signals: plugin integration tests and Unix builds cover compilation and behavior.
