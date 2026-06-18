# sources/cloud-native/containerd/contrib/seccomp/seccomp_default.go

Purpose: Linux implementation of containerd's default seccomp allowlist.

Important APIs/functions: `arches()` maps `runtime.GOARCH` to OCI seccomp architectures, including compatible sub-architectures. `DefaultProfile(sp *specs.Spec)` returns a `*specs.LinuxSeccomp` with `DefaultAction: ActErrno`, architecture list, broad safe syscall allowlist, socket-domain filters that block `AF_ALG` and `AF_VSOCK`, restricted `personality` values, kernel-version gated ptrace/process-vm syscalls, arch-specific syscalls, and capability-gated syscalls.

Control flow and state: the function constructs an in-memory profile each call. It consults the running kernel version for a `>=4.8` gate, switches on GOARCH, then scans `sp.Process.Capabilities.Bounding`. `CAP_SYS_ADMIN` enables broad namespace/mount/bpf/perf and sets an `admin` flag; if admin is absent, it allows only masked namespace `clone` and explicitly returns `ENOSYS` for `clone3`.

Dependencies and integration: uses `golang.org/x/sys/unix`, containerd `kernelversion`, and OCI runtime-spec seccomp types. It feeds `WithDefaultProfile` in OCI generation and ultimately runtime engines such as runc/crun/libseccomp.

Risks: `sp.Process.Capabilities` must be non-nil or this panics. The allowlist includes very new syscall names, so runtime/libseccomp handling of unknown syscalls matters. Socket filtering is intentionally split into three rules due to runc/libseccomp semantics; modifying it risks reopening blocked domains. Capability-derived allowances must stay aligned with kernel security expectations.

Test signals: `seccomp_default_test.go` verifies io_uring syscalls remain disallowed. There is no exhaustive golden test for the syscall list, architectures, or capability gates.
