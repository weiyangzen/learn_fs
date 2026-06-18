# sources/distributed-fs/ceph-client/kernel/bpf/const_fold.c

## Purpose
`const_fold.c` performs a verifier dataflow analysis that discovers constant register values at instruction boundaries and uses them to rewrite conditional branches with known outcomes. This removes dead CFG edges before liveness analysis and improves later verifier precision.

## Important APIs, types, and functions
The central type is `struct const_arg_info`, whose state can be unvisited, unknown, known constant, map pointer, map value pointer, or subprogram pointer. `const_reg_xfer()` is the instruction transfer function, `const_reg_join()` merges predecessor outputs into successor inputs, `bpf_compute_const_regs()` runs the fixed-point pass and records results in `insn_aux_data`, `eval_const_branch()` evaluates conditional predicates, and `bpf_prune_dead_branches()` rewrites constant conditional jumps to `BPF_JMP_A`.

## Control flow
`bpf_compute_const_regs()` allocates an input state array per instruction and initializes every subprogram entry register to unknown. It iterates over reverse postorder until no successor state changes. The transfer function handles constant moves, sign-extending moves, simple add/sub/and operations, 64-bit immediates, map pointer and map-value pseudo loads, subprogram pseudo loads, read-only direct map-value loads, call clobbering of R0-R5, and selected atomic side effects. After convergence it saves only 32-bit constants plus map pointer and subprogram identifiers into each instruction aux record. `bpf_prune_dead_branches()` then scans conditional jumps, skips `may_goto`, fetches recorded constant operands, applies 32-bit signed casts for `BPF_JMP32`, evaluates the branch, rewrites it into an unconditional jump to either the taken target or fall-through, and recomputes postorder if anything changed.

## State and persistence
The analysis workspace is temporary and freed after the pass. Persisted state is per-instruction aux metadata: `const_reg_mask`, `const_reg_map_mask`, `const_reg_subprog_mask`, and `const_reg_vals[]`. Branch rewrites persist by modifying `env->prog->insnsi` and replacing `env->cfg.insn_postorder` with a recomputed order after CFG changes. No runtime state is introduced.

## Dependencies and integration points
This pass depends on postorder computed by `cfg.c`, successor information from `bpf_insn_successors()`, verifier map metadata, direct-read support for read-only maps, and subprogram lookup. It feeds liveness and later verifier optimization paths that use `insn_aux_data` constants. It also depends on the verifier having already resolved pseudo map references into `env->used_maps` indices.

## Risks and test signals
Risks include unsound constant propagation across calls, incomplete handling of ALU operations, map value direct-read races if a map is not truly read-only, losing 64-bit constants because only 32-bit values are saved for branch pruning, signed/unsigned comparison mistakes for `BPF_JMP32`, and failing to recompute dependent CFG metadata after rewrites. Test signals include constant branches with K and X sources, 32-bit signed comparisons, read-only map value loads, non-read-only map loads remaining unknown, subprogram entry isolation, call clobbers, atomic fetch/CMPXCHG behavior, `may_goto` not pruned, and liveness not propagating through pruned edges.
