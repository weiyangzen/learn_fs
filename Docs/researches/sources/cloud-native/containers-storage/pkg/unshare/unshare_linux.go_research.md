# sources/cloud-native/containers-storage/pkg/unshare/unshare_linux.go

Purpose: Linux process wrapper and rootless/user-namespace support for containers/storage.

Important APIs/types/functions: `Cmd` with namespace flags, newuidmap/newgidmap controls, UID/GID mappings, session options, OOM score, and hook; `Command`, `Start`, `Run`, `MaybeReexecUsingUserNamespace`, `ExecRunnable`, `GetHostIDMappings`, `GetSubIDMappings`, `ParseIDMappings`, `IsRootless`, `HasCapSysAdmin`, and `IsSetID`.

Control flow: `Cmd.Start` locks the OS thread, encodes namespace instructions in env vars, starts a reexec child, reads the child PID from the C constructor, writes setgroups/uid_map/gid_map through `/proc` or `newuidmap/newgidmap`, writes `oom_score_adj`, runs a hook, and releases the continue pipe. `MaybeReexecUsingUserNamespace` decides whether a new userns is needed, constructs mappings from `/etc/subuid`/`subgid` or current maps, sets rootless environment, forwards signals, sets `Pdeathsig`, and exits with the child status through `ExecRunnable`.

State/persistence: starts and controls child processes, mutates `/proc/<pid>` mapping files and OOM score, changes process environment, caches rootless/capability checks, and uses subuid/subgid configuration.

Dependencies/integration: tightly integrated with `pkg/reexec`, the C constructor in `unshare.c`, `idtools`, OCI `LinuxIDMapping`, Linux capabilities, `/proc`, and rootless Buildah/Podman environment conventions.

Risks: security-sensitive and race-sensitive. Mapping setup must happen while the child is paused; failures kill/wait the child. Fallback from `newuidmap/newgidmap` to single mapping can reduce namespace range. `IsRootless`/`HasCapSysAdmin` cache results and may not reflect later environment/capability changes. Some warnings are logged rather than returned in rootless reexec setup.

Test signals: `unshare_test.go` exercises namespace changes, process group/session changes, OOM score, and UID/GID map round trips under Linux.
