# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.h

Purpose: this private header defines the ARM64 probe instruction decoding contract shared by kprobes and uprobes.

Important APIs and types: `MAX_ATOMIC_CONTEXT_SIZE` is fixed at 128 bytes divided by instruction size, matching Arm guidance for load-exclusive/store-exclusive sequences. `enum probe_insn` defines `INSN_REJECTED`, `INSN_GOOD_NO_SLOT`, and `INSN_GOOD`. It declares `arm_probe_decode_insn()` for shared decode/simulation decisions and `arm_kprobe_decode_insn()` under `CONFIG_KPROBES` for kernel-specific checks.

Control flow and state: the header has no runtime state. Its enum values drive allocation and execution paths in `kprobes.c` and `uprobes.c`: rejected instructions fail registration, good-no-slot instructions run via simulator handlers, and good instructions use XOL slots.

Dependencies and integration: includes `asm/kprobes.h` for architecture probe structures and `__kprobes` annotations. It integrates with `decode-insn.c`, `kprobes.c`, and `uprobes.c`.

Risks: changing enum semantics requires coordinated changes in both kprobe and uprobe users. The atomic context size is a policy boundary; shrinking or expanding it changes which kernel instructions can be instrumented.

Test signals: compile coverage with `CONFIG_KPROBES` enabled/disabled and functional probes on instruction classes whose decode result should differ.
