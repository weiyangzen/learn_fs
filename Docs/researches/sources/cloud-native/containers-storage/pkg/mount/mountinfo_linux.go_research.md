# sources/cloud-native/containers-storage/pkg/mount/mountinfo_linux.go

Purpose: reads mountinfo for an arbitrary Linux process ID.

Important APIs, types, and functions: `PidMountInfo(pid int) ([]*Info, error)`.

Control flow: opens `/proc/<pid>/mountinfo`, defers close, and parses it with `mountinfo.GetMountsFromReader`.

State and persistence: reads another process's mount namespace view as exposed by procfs; no mutation.

Dependencies and integration points: depends on `fmt`, `os`, and `github.com/moby/sys/mountinfo`. Useful for inspecting container or process mount namespaces.

Risks and edge cases: fails if procfs is unavailable, pid exits, or permissions prevent reading. It does not validate pid beyond path formatting.

Test signals: no direct requested tests; mountinfo parser coverage comes indirectly from current-process mount tests.
