<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/Makefile -->
# sources/distributed-fs/ceph-client/net/bpf/Makefile

Purpose: builds the kernel networking BPF test-run support objects when BPF syscall support is enabled.

Important APIs, types, and functions: this Makefile has no runtime APIs. It assigns `test_run.o` to `obj-$(CONFIG_BPF_SYSCALL)` and adds `bpf_dummy_struct_ops.o` only when `CONFIG_BPF_JIT=y`.

Control flow: Kbuild includes `test_run.c` whenever the BPF syscall is compiled so `BPF_PROG_TEST_RUN` support and related test kfunc registrations are present. The dummy struct-ops provider is JIT-gated because struct-ops test execution prepares BPF trampolines and executable images.

State and persistence: none directly. The selected objects register late-init callbacks and BTF/kfunc metadata at runtime.

Dependencies and integration points: depends on Kbuild symbols `CONFIG_BPF_SYSCALL` and `CONFIG_BPF_JIT`. It integrates with the networking tree by placing BPF test-run code under `net/bpf`.

Risks: an incorrect config gate would either omit required syscall test support or compile trampoline-dependent dummy struct ops where JIT infrastructure is unavailable. Since the file uses `:=` for the first assignment, additional unconditional objects would need care not to overwrite `test_run.o`.

Test signals: build matrix coverage for BPF enabled/disabled and BPF JIT enabled/disabled. BPF selftests that use `BPF_PROG_TEST_RUN`, fentry/fexit, modify-return, and struct-ops dummy programs signal whether this object selection is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/Makefile -->
