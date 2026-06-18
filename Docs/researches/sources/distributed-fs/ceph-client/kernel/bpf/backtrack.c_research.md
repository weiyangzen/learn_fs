# sources/distributed-fs/ceph-client/kernel/bpf/backtrack.c

Purpose: implements verifier backtracking for scalar precision, allowing BPF state pruning while preserving exact scalar ranges only where later instructions require them.

Important APIs/types/functions: `bpf_push_jmp_history` records branch/call/exit history and stack access flags; `bpf_mark_chain_precision` is the main exported precision propagation routine; `bpf_mark_all_scalars_precise` is the conservative fallback; `backtrack_insn` interprets instructions in reverse; mask helpers manage per-frame register and stack-slot dependency sets; `bpf_fmt_stack_mask` formats debug output.

Control flow: verifier records jump history as it explores states. When precision is required for a register, `bpf_mark_chain_precision` initializes a backtrack mask at the current frame and walks instructions backward through the current and parent verifier states. `backtrack_insn` propagates dependencies through ALU moves, loads from stack spills, stores to stack, conditional jumps, helper/kfunc calls, static/global subprogram calls, callbacks, exits, and ldimm instructions. Unsupported or ambiguous patterns fall back to marking all scalar registers and spilled scalars in parent states precise.

State and persistence: state is stored in `bpf_verifier_state` parent chains, `jmp_history`, register `precise` bits, and spilled stack slot metadata. Backtracking state is transient in `env->bt`.

Dependencies and integration: depends on verifier instruction flags, subprogram discovery, callback detection, register/stack metadata, verifier logging, BPF instruction encoding, and state equivalence/pruning logic.

Risks: under-marking precision can make unsafe state pruning possible; over-marking reduces verifier performance and program acceptance. Subprogram/callback frame transitions are subtle. Pointer arithmetic or stack access through unsupported patterns intentionally triggers conservative fallback. Jump history consistency bugs produce verifier errors.

Test signals: verifier selftests involving scalar precision, callbacks, subprograms, tail calls, atomic fetch/load, stack spills, bounded loops, and log-level replay are relevant. Unexpected `backtracking misuse`, `unexpected regs`, or fallback explosions indicate regressions.
