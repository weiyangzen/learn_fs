# sources/distributed-fs/ceph-client/arch/arc/net/Makefile

Purpose: selects ARC networking architecture objects for eBPF JIT support.

Important entries: when `CONFIG_ISA_ARCV2=y`, `CONFIG_BPF_JIT` builds `bpf_jit_core.o` and `bpf_jit_arcv2.o`.

Control flow: build-time only. It restricts this JIT backend to ARCv2.

State and persistence: no runtime state.

Dependencies and integration: integrates with generic BPF JIT core and the ARCv2 backend defined by `bpf_jit.h`/`bpf_jit_arcv2.c`.

Risks: enabling the backend for non-ARCv2 would emit unsupported instructions. Disabling it falls back to the interpreter or generic behavior depending on kernel configuration.

Test signals: build matrix for ARCv2 with `CONFIG_BPF_JIT=y/n`, ARCompact builds confirming no backend object is selected, and BPF selftests on ARCv2.
