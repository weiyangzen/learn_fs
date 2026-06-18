# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/config

Purpose: kernel configuration fragment for enabling BPF selftest coverage and related networking, tracing, security, crypto, and filesystem features.

Important settings: enables core BPF (`CONFIG_BPF`, `BPF_SYSCALL`, `BPF_JIT`, `BPF_EVENTS`, `CGROUP_BPF`, `BPF_LSM`), debug/BTF (`DEBUG_INFO_BTF`), tracing (`FUNCTION_TRACER`, `DYNAMIC_FTRACE`, `FPROBE`, `FTRACE_SYSCALLS`), networking features for XDP/tunnels/netfilter/MPLS/MPTCP/SMC, IMA/fsverity/keys, modules, and test/sample support.

Control flow: not executable; consumed by kernel/selftest build or VM setup workflows.

State and persistence: persistent desired kernel config state when merged into a build.

Dependencies and integration points: aligns kernel feature availability with the selftests in this tree.

Risks: config can drift behind tests requiring newer options; enabling many subsystems increases build/runtime surface; `CONFIG_BPF_UNPRIV_DEFAULT_OFF` is explicitly not set, which matters for privilege assumptions.

Test signals: kernels built with this fragment should satisfy feature gates for broad BPF selftest execution.
