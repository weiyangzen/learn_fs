<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp.go -->
# sources/cloud-native/containerd/core/mount/temp.go

Purpose: temporary mount lifecycle helpers and option filtering for temporary/read-only access to mount arrays.

Important APIs/types/functions: package variable `tempMountLocation`; `WithTempMount`, `RemoveVolatileOption`, `RemoveIDMapOption`, `copyMounts`, `WithReadonlyTempMount`, and `getTempDir`.

Control flow: `WithTempMount` creates a temp directory under `tempMountLocation`, defers `os.Remove` and reverse unmount, mounts all input mounts after removing overlay volatile options, runs the callback, and combines callback/unmount errors carefully. `RemoveVolatileOption` and `RemoveIDMapOption` lazily copy mounts only when a matching option is removed. `WithReadonlyTempMount` first converts mounts to read-only.

State and persistence: creates and removes a temporary directory; performs real mounts through `All` and unmounts through `UnmountMounts`. It deliberately uses `os.Remove` instead of `RemoveAll` to avoid deleting mounted data if unmount fails.

Dependencies and integration points: used by image unpack/inspection and temporary access flows. `SetTempMountLocation` in platform files changes the base location; Linux idmapped overlay helpers also use `tempMountLocation`.

Risks: temp dirs can leak when unmount fails, by design. `RemoveIDMapOption` removes while ranging and may skip adjacent idmap options after slice mutation. `RemoveVolatileOption` removes only the first volatile-like option per overlay mount.

Test signals: `mount_test.go` covers volatile removal and input preservation; read-only conversion tests cover `WithReadonlyTempMount` preprocessing. Runtime mount/unmount behavior is exercised through Linux tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp.go -->
