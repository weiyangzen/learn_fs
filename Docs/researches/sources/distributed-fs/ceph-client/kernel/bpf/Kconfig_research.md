# sources/distributed-fs/ceph-client/kernel/bpf/Kconfig

Purpose: declares core BPF subsystem configuration symbols, including interpreter availability, architecture JIT capability flags, the `bpf()` syscall, JIT policy, unprivileged defaults, preload inclusion, and BPF LSM enablement.

Important APIs/types/functions: key symbols are `BPF`, `HAVE_CBPF_JIT`, `HAVE_EBPF_JIT`, `ARCH_WANT_DEFAULT_BPF_JIT`, `BPF_SYSCALL`, `BPF_JIT`, `BPF_JIT_ALWAYS_ON`, `BPF_JIT_DEFAULT_ON`, `BPF_UNPRIV_DEFAULT_OFF`, and `BPF_LSM`.

Control flow: Kconfig selects foundational dependencies when `BPF_SYSCALL` is enabled, gates JIT on architecture support, makes `BPF_JIT_ALWAYS_ON` remove interpreter fallback, defaults unprivileged BPF to disabled, sources preload Kconfig, and requires security/JIT/event support for BPF LSM.

State and persistence: persists as compile-time `.config` decisions and runtime sysctl defaults such as unprivileged BPF and JIT behavior.

Dependencies and integration: selects crypto SHA-256, IRQ work, Tasks RCU flavors, binary printf, networking support symbols when enabled, EXECMEM for JIT, and security/BPF events for LSM hooks.

Risks: changing defaults can affect kernel attack surface, performance, and compatibility. JIT-always-on changes interpreter availability and speculative execution posture. BPF LSM depends on BTF/JIT/prototype ordering elsewhere.

Test signals: allmodconfig/defconfig matrix builds, unprivileged BPF sysctl behavior, JIT sysctl tests, BPF LSM selftests, and preload builds are relevant.
