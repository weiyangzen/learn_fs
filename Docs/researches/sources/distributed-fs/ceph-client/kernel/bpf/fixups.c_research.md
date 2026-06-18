# sources/distributed-fs/ceph-client/kernel/bpf/fixups.c

## Purpose
`fixups.c` is the verifier/JIT rewrite engine for BPF programs after verification. It patches instructions, maintains verifier metadata while program length changes, converts context accesses, removes dead code and nops, prepares BPF-to-BPF calls for JIT or interpreter fallback, rewrites helper and kfunc calls, adds security/speculation guards, inlines selected helpers and loops, and finalizes tail-call poke tracking.

## Important APIs, types, and functions
Key exported functions include `bpf_patch_insn_data()`, `bpf_clear_insn_aux_data()`, `bpf_insn_is_cond_jump()`, `bpf_opt_hard_wire_dead_code_branches()`, `bpf_opt_remove_dead_code()`, `bpf_opt_remove_nops()`, `bpf_opt_subreg_zext_lo32_rnd_hi32()`, `bpf_convert_ctx_accesses()`, `bpf_dup_insn_aux_data()`, `bpf_restore_insn_aux_data()`, `bpf_jit_subprogs()`, `bpf_fixup_call_args()`, `bpf_do_misc_fixups()`, `bpf_optimize_bpf_loop()`, and `bpf_remove_fastcall_spills_fills()`. Internals adjust subprogram starts, line info, poke descriptors, instruction-array maps, kfunc descriptors, and jump offsets.

## Control flow
Instruction patching expands or replaces one instruction and then keeps all side metadata aligned: aux data is moved/zeroed, subprogram starts are shifted, instruction-array maps and poke descriptors are adjusted, and range errors are logged. Removal performs the inverse, clearing dynamic aux fields, shrinking insns, adjusting subprograms and line info, and shifting aux records.

Optimization passes first hard-wire branches whose verified taken/untaken side is unreachable, remove unseen instruction ranges, remove nop/may_goto-zero instructions, and optionally add JIT-required zero extension or randomized high 32 bits for test mode. Context conversion injects program-type prologues/epilogues, nospec barriers, probe-memory loads for untrusted BTF/mem pointers, arena probe modes, program-specific ctx access sequences, narrow-load masks, and sign extension.

BPF-to-BPF JIT handling splits the program into subprogram `bpf_prog` objects, temporarily rewrites pseudo-call/pseudo-func immediates, compiles each function, patches final call addresses, locks subprograms read-only, registers kallsyms, and restores dump-friendly interpreter instructions. On non-fatal JIT failure it restores state for interpreter fallback; on unsupported interpreter features it rejects.

`bpf_do_misc_fixups()` is the dense final pass. It creates a hidden exception callback if needed, rewrites address-space casts, converts marked ALU64 operations to ALU32, makes div/mod exceptional cases deterministic, guards probe-memory against user addresses, expands LD_ABS/LD_IND, sanitizes pointer arithmetic for speculation, expands `may_goto`, rewrites kfunc calls, rewrites or inlines helper calls, converts map ops to direct map op calls or generated lookup sequences, sets program flags for route realm/random/override/tail calls, adds tail-call poke descriptors, handles timer callback aux, per-CPU allocation pointer calls, tracing arg/ret/ip helpers, branch snapshot, jiffies, current task/cpu helpers, and kptr xchg. It then initializes extra may_goto stack slots, publishes poke tracking, and sorts kfunc descriptors by final call immediate/offset.

## State and persistence behavior
The file mutates `env->prog`, `env->insn_aux_data`, `env->subprog_info`, line info, map poke tables, kfunc tables, and program aux fields. Many rewrites are persistent changes to the loaded program image; some temporary JIT changes are restored for interpreter/dump consistency. Memory state includes vmalloc aux copies, subprogram arrays, JIT images, exception tables, and kfunc descriptor sorting.

## Dependencies and integration points
It integrates with the verifier environment, BPF JIT core, BTF/kfunc tables, map ops, tail-call poke tracking, offload hooks, XDP/socket/ctx access converters, perf branch snapshot static calls, architecture support flags, disassembler helper names for errors, and BPF instruction array maps.

## Risks and test signals
Risks are metadata drift after patch/remove, jump offset overflow, incorrect line/subprogram info, unsafe fallback after failed JIT, helper rewrite ABI mismatches, verifier-approved access becoming unsafe after conversion, tail-call poke mis-tracking, and architecture feature condition bugs. Tests should include dead-code/nop removal with BTF line info, ctx narrow loads, nospec insertion, untrusted BTF probe loads, arena loads/stores, all div/mod edge cases, LD_ABS/IND rewrite, pointer arithmetic sanitization, timed and untimed may_goto, BPF-to-BPF JIT success/failure/fallback, kfunc far/near calls, map lookup inlining, tail-call poke setup, tracing helpers, branch snapshot, loop inlining, and fastcall spill/fill removal.
