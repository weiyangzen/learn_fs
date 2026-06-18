<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_windows.go

Purpose: supplies Windows-specific behavior for the remote containerd/runhcs client: bundle directories, named pipe names, runhcs debug options, stats summary conversion, and unsupported resource update stubs.

Important APIs and types: `summaryFromInterface`, `WithBundle`, `withLogLevel`, `pipeName`, `newFIFOSet`, `newDirectIO`, `UpdateResources`, and `getSpecUser`.

Control flow: `WithBundle` creates a bundle directory and writes its path to the Docker bundle label. `newFIFOSet` derives deterministic pipe names from container ID, process ID, and stream name. `newDirectIO` creates named-pipe listeners via `newStdioPipes` and wraps them in `cio.DirectIO`. `summaryFromInterface` maps runhcs `options.ProcessDetails` into daemon `Summary` fields.

State and persistence: creates bundle directories; stdio state exists as Windows named pipes. Resource updates and user mapping intentionally do not mutate state.

Dependencies and integration: depends on hcsshim runhcs options, containerd containers/cio, Docker libcontainerd types, and `log`. It complements `client_io_windows.go`.

Risks: `UpdateResources` and `getSpecUser` silently no-op, so callers must not assume Windows resource updates are applied. Unknown summary payload types produce errors. Named pipe names include IDs and must stay within Windows pipe naming constraints.

Test signals: no direct tests in this subset; docker top/process summary and runhcs I/O require Windows integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_windows.go -->
