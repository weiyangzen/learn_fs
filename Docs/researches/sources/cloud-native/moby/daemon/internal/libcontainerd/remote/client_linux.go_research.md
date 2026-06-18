<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_linux.go

Purpose: supplies Linux-specific behavior for the remote libcontainerd client: bundle ownership under user namespaces, FIFO paths, resource updates, and user ID mapping for runc I/O ownership.

Important APIs and types: `summaryFromInterface`, `UpdateResources`, `hostIDFromMap`, `getSpecUser`, `WithBundle`, `withLogLevel`, `newFIFOSet`, and `newDirectIO`.

Control flow: `getSpecUser` detects user namespace mappings and maps container root UID/GID to host IDs. `WithBundle` sets the Docker bundle path label and creates bundle directories, using suffixes like `.uid.gid` when intermediate paths are not accessible to mapped root. `newFIFOSet` builds stdin/stdout/stderr FIFO paths under the bundle and supplies a closer that removes them. `UpdateResources` calls containerd `Task.Update`.

State and persistence: creates bundle directories and FIFO files under the state directory. The bundle path actually used may differ from the requested path when user namespace ownership requires a suffixed directory.

Dependencies and integration: depends on containerd containers/cio, runc specs, Docker user helpers, and `log`. It is compiled into the remote client on Linux.

Risks: directory accessibility checks are path-component based and sensitive to existing permissions. `summaryFromInterface` is a no-op because Linux process summary is not used, so callers expecting docker-top details must use other paths. `withLogLevel` panics if called on Linux, relying on `remote/client.go` to call it only on Windows.

Test signals: no direct tests here; user namespace bundle behavior depends on integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client_linux.go -->
