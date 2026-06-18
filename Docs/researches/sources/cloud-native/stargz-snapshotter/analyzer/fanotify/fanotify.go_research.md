# sources/cloud-native/stargz-snapshotter/analyzer/fanotify/fanotify.go

Purpose: Spawns and controls the hidden `ctr-remote fanotify /` helper in a new mount namespace so the analyzer can observe file accesses inside a prepared root filesystem.

Important APIs: `SpawnFanotifier`, `Fanotifier.Start`, `Fanotifier.GetPath`, `Fanotifier.MountNamespacePath`, and `Fanotifier.Close`. `SpawnFanotifier` builds `exec.Command(fanotifierBin, "fanotify", "/")`, sets `CLONE_NEWNS`, wires stdin/stdout pipes, starts the process, and wraps those pipes with `conn.Client`.

Control flow: Callers create the process, use `MountNamespacePath` to join or bind work to the helper's mount namespace, call `Start` to trigger service-side marking, then repeatedly call `GetPath` for notified paths. `Close` kills the process and closes both pipes once.

State and persistence: Keeps process handle, client connection, and a `sync.Once` guarded close path. No persistent data is written here.

Dependencies and integration: Depends on Linux mount namespaces, `syscall.SysProcAttr`, and the fanotify service exposed by `cmd/ctr-remote/commands/notify.go`.

Risks: `Close` kills but does not `Wait`, so process reaping depends on surrounding code. Failure after one pipe is opened but before process start can leave cleanup responsibility with the caller. Requires privileges/capabilities for namespace and fanotify operations.

Test signals: No local unit tests; integration coverage would need privileged fanotify and namespace support.
