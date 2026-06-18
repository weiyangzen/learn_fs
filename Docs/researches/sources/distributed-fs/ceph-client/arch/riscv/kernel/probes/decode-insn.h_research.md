# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.h

Purpose: Declares RISC-V kprobe instruction decode results and the decoder entry point.

Important APIs/types/functions: Defines `enum probe_insn` classification values and declares `riscv_probe_decode_insn()`.

Control flow: Header-only; it establishes the contract between decode, kprobe preparation, and instruction simulation.

State and persistence: No state.

Dependencies and integration points: Used by kprobes and simulator code in the same directory.

Risks and test signals: Enum meaning must stay synchronized with kprobe control flow. Test build coverage and kprobe decode paths for every enum case.
