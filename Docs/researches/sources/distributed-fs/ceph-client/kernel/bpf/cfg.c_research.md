# sources/distributed-fs/ceph-client/kernel/bpf/cfg.c

## Purpose
`cfg.c` implements verifier control-flow graph support for eBPF programs. It checks reachability and illegal loops, records jump and prune points used by state pruning, builds jump-table metadata for indirect `gotox` branches, models hidden abnormal exits for `tail_call` and `LD_ABS`/`LD_IND`, and computes postorder plus strongly connected components for later verifier analyses.

## Important APIs, types, and functions
The file uses `env->cfg.insn_state`, `env->cfg.insn_stack`, `env->cfg.insn_postorder`, `env->insn_aux_data[*].jt`, `env->subprog_info`, and `env->scc_info`. `bpf_check_cfg()` is the main validation pass. `visit_insn()`, `push_insn()`, `visit_func_call_insn()`, `visit_gotox_insn()`, and `visit_abnormal_return_insn()` encode successor discovery. `bpf_iarray_realloc()` and `bpf_copy_insn_array_uniq()` support dynamic successor arrays. `bpf_compute_postorder()` fills instruction postorder ranges per subprogram, and `bpf_compute_scc()` assigns nonzero SCC IDs to real or implicit loops.

## Control flow
`bpf_check_cfg()` allocates arrays sized to `env->prog->len`, starts DFS at instruction 0, and optionally walks the exception callback subprogram if it was not reached from main. `push_insn()` validates branch targets, labels fall-through and branch edges, rejects back edges for unprivileged programs, and records branch targets as prune and jump points. `visit_insn()` routes by opcode class: non-branch instructions fall through, subprogram calls add a callee edge plus a return edge, helper/kfunc calls may mark sleep or packet-data side effects, tail calls and packet absolute loads get an abnormal exit edge, direct jumps have one successor, conditional jumps have two successors, and `BPF_JA | BPF_X` expands through a verifier-discovered jump table.

## State and persistence
All state is verifier-lifetime state. Temporary DFS arrays are freed before `bpf_check_cfg()` returns. Jump-table arrays stored in `insn_aux_data[t].jt` persist for later verifier passes. The pass also persists derived flags into `prog->aux->changes_pkt_data`, `prog->aux->might_sleep`, subprogram side-effect flags, `insn_postorder`, and SCC IDs. There is no on-disk or runtime persistence outside the loaded BPF program metadata.

## Dependencies and integration points
This file depends on verifier helpers such as `mark_prune_point`, `mark_jmp_point`, `bpf_insn_successors`, `bpf_find_containing_subprog`, helper/kfunc metadata lookup, BPF instruction decoding macros, and BPF array maps used as instruction arrays. It feeds later verifier phases including constant folding, liveness, state convergence, iterator loop handling, and `may_goto` timed-loop analysis.

## Risks and test signals
Key risks are off-by-one branch targets, jumps into the second half of `ldimm64`, inaccurate subprogram side-effect propagation, treating all instruction-array maps as jump tables, stale jump table bounds across subprograms, abnormal exit modeling mismatches, DFS stack overflow, and SCC mislabeling around callbacks or self edges. Test signals include verifier tests for unreachable instructions, backward branches with and without privilege, indirect `gotox` tables, tail call hidden exits, `LD_ABS` in subprograms, callbacks requiring convergence checkpoints, exception callback reachability, branch pruning point coverage, and SCC IDs on loops, self loops, and acyclic code.
