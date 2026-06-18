# sources/cloud-native/cri-o/internal/config/nsmgr/test/utils.go

Purpose: supplies lightweight namespace and container fixtures for tests outside `nsmgr`.

Important APIs/types/functions: `SpoofedNamespace` implements `nsmgr.Namespace` plus `Close`; `AllSpoofedNamespaces` provides net, ipc, uts, user, and pid namespace instances; `ContainerWithPid(pid int)` returns an `oci.Container` with a Linux spec containing the requested process PID.

Control flow: `SpoofedNamespace` methods return stored type/path, and `Remove`/`Close` are no-ops. `ContainerWithPid` constructs a new `oci.Container`, sets its spec to `rspec.Spec{Linux: &rspec.Linux{Namespaces: []rspec.LinuxNamespace{}}, Process: &rspec.Process{}}`, and writes `State().Pid`.

State and persistence behavior: all fixtures are in-memory. No namespace files or mounts are created.

Dependencies/integration points: used by container namespace tests and other packages that need namespace-shaped values without actual kernel namespace operations. Depends on CRI-O `oci` and runtime-spec types.

Risks: no-op removal means tests using these fixtures cannot catch cleanup failures. The spoofed paths are plain strings and are not validated.

Test signals: helper only; coverage appears in consumers.
