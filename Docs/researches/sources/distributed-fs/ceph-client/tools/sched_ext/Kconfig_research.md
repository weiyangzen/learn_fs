# sources/distributed-fs/ceph-client/tools/sched_ext/Kconfig

Purpose: documents a kernel configuration fragment for building and testing sched_ext schedulers and related tracing/debugging capabilities.

Important entries: mandatory scheduler and BPF options include `CONFIG_BPF`, `CONFIG_BPF_SYSCALL`, `CONFIG_BPF_JIT`, `CONFIG_DEBUG_INFO_BTF`, `CONFIG_BPF_JIT_ALWAYS_ON`, `CONFIG_BPF_JIT_DEFAULT_ON`, and `CONFIG_SCHED_CLASS_EXT`. Test coverage and debugging entries include `CONFIG_SCHED_DEBUG`, `CONFIG_SCHED_AUTOGROUP`, `CONFIG_SCHED_CORE`, `CONFIG_SCHED_MC`, `CONFIG_PREEMPT`, `CONFIG_PREEMPT_DYNAMIC`, lockdep/prove-locking options, ftrace/kprobe/uprobe/BPF event options, `CONFIG_IKHEADERS`, and IKCONFIG options.

Control flow: no executable control flow; this is consumed as a config checklist or fragment.

State and persistence: persistent state is kernel build configuration. It has no runtime state by itself.

Dependencies and integration: integrates with the sched_ext examples by ensuring BPF, BTF, struct_ops, tracing, sched core, and debug infrastructure exist. `CONFIG_KALLSYMS_ALL` is called out for Rust schedulers. `CONFIG_DEBUG_INFO_REDUCED` is explicitly disabled for arm64.

Risks: enabling debug lock and tracing options can add overhead and may not be desirable in production. It is a broad testing profile, not a minimal runtime profile. Comments reference LAVD and Rust schedulers beyond the C examples in this subset.

Test signals: use `scripts/kconfig/merge_config.sh` or equivalent to apply the fragment, then verify `/sys/kernel/sched_ext`, `/sys/kernel/btf/vmlinux`, BPF JIT, tracing, and sched_ext example load behavior.
