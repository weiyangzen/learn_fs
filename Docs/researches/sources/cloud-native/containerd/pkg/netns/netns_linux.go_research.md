# sources/cloud-native/containerd/pkg/netns/netns_linux.go

Purpose: Linux network namespace lifecycle helper for sandbox/container networking.

Important APIs/types/functions: `newNS(baseDir, pid)` creates a bind-mounted namespace file under `baseDir`, either from a new namespace (`unshare(CLONE_NEWNET)`) or an existing pid namespace. `unmountNS` detaches and removes the path. `getCurrentThreadNetNSPath` uses `/proc/<pid>/task/<tid>/ns/net`. `NetNS` exposes `NewNetNS`, `NewNetNSFromPID`, `LoadNetNS`, `Remove`, `Closed`, `GetPath`, and `Do`.

Control flow: new namespace creation locks an OS thread, records the original netns, unshares, bind-mounts the thread netns path to a temp file, restores the original namespace, and returns the bind path. `Closed` treats missing or non-namespace paths as closed and cleans up stale files.

State/persistence: persists namespace references as bind mounts/files under `baseDir`; removal unmounts and deletes them.

Dependencies/integration: uses CNI `ns`, containerd mount helpers, `golang.org/x/sys/unix`, and `/proc`. Sandbox code can pass `GetPath` to runtimes or call `Do` to execute in the namespace.

Risks: requires privileges for unshare, setns, bind mount, and unmount. Thread locking and restoration are critical; failure can affect the running thread's namespace. Cleanup must handle stale paths.

Test signals: no direct tests in subset; integration should cover create/load/remove, pid-based namespace, closed detection, and `Do` execution.
