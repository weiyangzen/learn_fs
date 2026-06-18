# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.c

Purpose: this file classifies AArch64 instructions for kprobes and uprobes. It decides whether an instruction can safely execute out-of-line in an XOL slot, must be simulated in the exception handler, or must be rejected.

Important APIs: `arm_probe_decode_insn()` is shared by kprobes and uprobes; it returns `INSN_GOOD`, `INSN_GOOD_NO_SLOT`, or `INSN_REJECTED` and fills `arch_probe_insn.handler` for simulated instructions. Under `CONFIG_KPROBES`, `arm_kprobe_decode_insn()` adds kernel-specific handling for literal loads and atomic exclusive sequences. `aarch64_insn_is_steppable()` encodes the safety policy for XOL execution.

Control flow: NOPs are simulated for speed. Branch/system-class instructions are rejected from XOL if they branch, touch MSR/MRS in unsafe ways, throw exceptions, return from exception, or are unsafe hints. Literal loads, exclusive operations, and memory copy/set sequences are also not XOL-safe. Known non-steppable instructions are mapped to simulator handlers for conditional branches, compare/test branches, ADR/ADRP, direct/indirect branches, returns, and literal loads. Kprobes additionally scans backward within the current symbol up to `MAX_ATOMIC_CONTEXT_SIZE` to reject probes between load-exclusive and store-exclusive.

Dependencies and integration: heavily depends on `asm/insn.h` decoders, `simulate-insn.h` handlers, kallsyms symbol size/offset lookup, and `decode-insn.h` enum contracts. `kprobes.c` and `uprobes.c` call into this before installing probes.

Risks: incorrect classification can corrupt PC-relative behavior, exclusive sequences, system register state, or exception control flow. Atomic scanning depends on kallsyms boundaries to avoid searching unrelated text or literals. New ARM64 instructions must be considered here before being probed safely.

Test signals: probe selftests registering on branches, literal loads, NOPs, exclusive sequences, MOPS, and system instructions. Failures show as rejected valid probes, accepted unsafe probes, wrong post-probe PC, or unexpected faults in XOL slots.
