# sources/distributed-fs/ceph-client/kernel/bpf/verifier.c lines 17314-20203

## Scope

This chunk covers the late verifier execution path in `sources/distributed-fs/ceph-client/kernel/bpf/verifier.c`, from pointer-type convergence checks through the top-level `bpf_check()` verifier entry point. It includes instruction dispatch, state exploration and pruning, pseudo-instruction and fd-array resolution, used-map/BTF lifetime tracking, global-subprogram verification, attach-target validation for tracing/LSM/struct_ops/extension programs, kfunc call specialization/fixup, and the final verification cleanup and rewrite pipeline.

The chunk begins in the tail of a pointer-type mismatch helper and ends at the return from `bpf_check()`. Earlier chunks define most register-state, memory-access, subprogram, kfunc, CFG, and liveness helpers that are called here; this chunk is where those pieces are sequenced into the verifier's main admission path.

## Purpose

The code in this chunk decides whether a loaded BPF program is valid, records the persistent objects it depends on, rewrites selected instructions into runtime-ready form, and releases all temporary verifier state. It is the boundary between individual verifier checks and the kernel-facing result: either reject the program with verifier diagnostics or return a program whose `bpf_prog_aux` has validated stack depth, used maps/BTFs, attach metadata, trampoline state, optimized instructions, and runtime/JIT selection.

Several themes run through the chunk:

- A single instruction must not be reached with incompatible pointer types unless the verifier can safely merge trusted/untrusted memory or BTF pointer attributes.
- The verifier explores control flow by repeatedly executing symbolic instruction checks, pushing alternative branches, pruning equivalent states, and popping pending states until all reachable states are proven safe.
- Pseudo `ldimm64` instructions are resolved from user-provided fds, fd-array indexes, BTF ids, map value offsets, or function references into verifier-usable pointers and aux metadata.
- Program attach metadata is validated before the main abstract interpretation so context argument typing and helper policy match the eventual target.
- Successful verification is followed by stack-depth checks, dead-code sanitization or optimization, context conversion, misc fixups, subregister optimization, call-argument fixups, object reference transfer into `bpf_prog_aux`, and runtime selection.

## Important APIs, Types, and Functions

- `save_aux_ptr_type()` records `env->insn_aux_data[env->insn_idx].ptr_type` for memory instructions and rejects reuse of the same instruction with incompatible pointer classes. When allowed, it merges `PTR_TO_MEM`/`PTR_TO_BTF_ID` trust and readonly attributes so probe-memory fixups can be selected conservatively.
- `process_bpf_exit_full()` handles `BPF_EXIT` and exceptional exits. It checks resource leaks before nested-frame unwinding, performs `prepare_func_exit()` for subprogram returns, and applies either global-subprogram return-code rules or program-type return-code rules.
- `check_indirect_jump()` validates `gotox *dst_reg` through `PTR_TO_INSN` and `BPF_MAP_TYPE_INSN_ARRAY`, derives a bounded map index interval, copies unique instruction targets, pushes all but one branch, and sets `env->insn_idx` to the remaining target.
- `do_check_insn()` dispatches one instruction by class to ALU, memory load/store, atomic, helper, subprogram, kfunc, unconditional/conditional jump, exit, ld_abs/ld_ind, or ldimm64 handlers.
- `do_check()` is the core symbolic-execution loop. It enforces `BPF_COMPLEXITY_LIMIT_INSNS`, handles state pruning and jump history, logs verifier state, invokes offload verifier hooks, checks precomputed constant-register invariants, handles speculative/nospec early exits, and pops pending verifier states.
- `find_btf_percpu_datasec()`, `__check_pseudo_btf_id()`, and `check_pseudo_btf_id()` resolve pseudo BTF-id loads into kernel symbol addresses and aux typing for readonly memory, percpu BTF pointers, struct BTF pointers, or functions.
- `check_map_prog_compatibility()`, `__add_used_map()`, and `add_used_map()` validate and retain maps referenced by the program, including exclusive program hash, list/rbtree/spin-lock restrictions, offload-device match, sleepable map allowlist, cgroup-storage uniqueness, arena restrictions, and instruction-array initialization.
- `check_alu_fields()`, `check_jmp_fields()`, and `check_insn_fields()` perform early reserved-field validation for instruction encodings before deeper verifier work.
- `check_and_resolve_insns()` calculates the program tag, validates register numbers and opcodes, resolves pseudo map/BTF/function loads, records aux map indexes and offsets, and rewrites immediate fields to kernel addresses for verifier use.
- `release_maps()`, `release_btfs()`, `convert_pseudo_ld_imm64()`, and `release_insn_arrays()` manage temporary or final object references around acceptance/rejection.
- `do_check_common()`, `do_check_main()`, and `do_check_subprogs()` allocate initial verifier state, type initial arguments from BTF metadata, run the core verifier, free all transient states, and lazily verify reachable global subprograms.
- `check_struct_ops_btf_id()`, `bpf_check_attach_target()`, `can_be_sleepable()`, and `check_attach_btf_id()` validate attach targets, attach sleepability, extension replacement constraints, trampoline setup, LSM/iterator support, struct_ops member metadata, and denylisted targets.
- `process_fd_array()` and `add_fd_from_fd_array()` implement the newer fd-array API by pre-scanning maps and BTF objects referenced through array indexes.
- `specialize_kfunc()`, `__fixup_collection_insert_kfunc()`, and `bpf_fixup_kfunc_call()` replace generic kfunc descriptors with runtime-appropriate targets and synthesize extra instructions for object allocation/drop, percpu objects, collection insertion, casts, fsession helpers, and optional program-aux arguments.
- `bpf_check()` is the exported verifier entry point. It initializes `struct bpf_verifier_env`, runs all prechecks, invokes the main and global-subprogram verifier passes, runs post-verification optimizations/fixups, transfers retained objects into `bpf_prog_aux`, finalizes logs and runtime selection, and frees temporary memory.

Key state carriers are `struct bpf_verifier_env`, `struct bpf_verifier_state`, `struct bpf_func_state`, `struct bpf_reg_state`, `struct bpf_insn_aux_data`, `struct bpf_prog`, `struct bpf_prog_aux`, `struct bpf_map`, `struct btf`, `struct bpf_attach_target_info`, `struct bpf_subprog_info`, `struct bpf_func_info_aux`, and `struct bpf_kfunc_desc`.

## Control Flow

Instruction verification starts in `do_check_common()`, which allocates a fresh verifier state, initializes frame zero, derives starting register types, and calls `do_check()`. For the main program, `R1` is a context pointer unless BTF metadata marks the main function signature unreliable. For global subprograms, BTF-prepared argument metadata populates scalar, context, dynptr, memory, BTF-id, and arena-compatible registers. Exception callbacks receive additional shape checks: they must return a scalar and accept exactly one scalar argument.

`do_check()` runs until no pending verifier states remain. On each instruction it updates `env->prev_insn_idx`, validates `env->insn_idx`, increments `env->insn_processed`, records state instruction indexes, checks whether a pruning point has an equivalent already-visited state, optionally records jump history, honors pending signals and rescheduling, emits verifier logs, asks offload backends to verify the instruction, marks the instruction as seen for sanitizer/fixup purposes, validates constant-register precomputation, and then dispatches to `do_check_insn()`.

`do_check_insn()` is intentionally narrow: instruction class determines the deeper checker. Calls are split among BPF-to-BPF subprogram calls, kfunc calls, and helper calls. Unconditional jumps either update the instruction index directly or, for indirect `BPF_JA|BPF_X`, delegate to the instruction-array jump-table path. Conditional jumps delegate to `check_cond_jmp_op()`, which can push branch states. Exit instructions return a sentinel so `do_check()` can pop the next pending branch.

The `process_bpf_exit` label in `do_check()` is the common branch-completion path. It marks verifier state as scratched, updates branch counts, and calls `pop_stack()` to restore another pending state. `-ENOENT` from `pop_stack()` means verification is complete. Speculative paths can also terminate early when a `nospec` marker is reached or when a recoverable unsafe operation can be converted into a nospec barrier for that instruction.

Before symbolic execution, `bpf_check()` runs structural passes in a fixed order: BTF info early check, subprogram/kfunc discovery, subprogram validation, BTF info validation, pseudo-instruction resolution, offload preparation, CFG validation, postorder computation, stack-liveness init, attach-target validation, constant-register computation, dead-branch pruning, subprogram topological sort, SCC computation, live-register computation, fastcall marking, main verification, and reachable global-subprogram verification.

After symbolic execution, `bpf_check()` frees explored states and runs only-if-success transforms in another fixed order: remove fastcall spills/fills, check max stack depth, optimize BPF loops, privileged dead-code hard-wiring/removal/nop removal or unprivileged dead-code sanitization, context access conversion, misc fixups, subregister zero-extension optimization for non-offload programs, and call-argument fixups.

## State and Persistence Behavior

Verifier state is mostly transient. `bpf_check()` allocates `env`, `env->insn_aux_data`, successor buffers, explored-state hash buckets, stack-liveness data, CFG postorder, SCC data, indirect-jump temp buffers, and per-pass verifier states. `free_states()` releases `env->cur_state`, pending stack entries, reusable state-list entries, SCC visit backedges, and explored-state lists. The final cleanup path clears aux data, frees all temporary arrays, unlocks the verifier mutex for unprivileged callers, and releases the verifier environment.

Some state intentionally persists on accepted programs:

- `env->prog->aux->used_maps` and `used_map_cnt` are allocated and filled from `env->used_maps` after successful verification. If this transfer does not happen, `release_maps()` drops the verifier-held references.
- `env->prog->aux->used_btfs` and `used_btf_cnt` are similarly transferred after success; otherwise `release_btfs()` drops BTF/module references.
- `prog->aux->attach_func_proto`, `attach_func_name`, `mod`, `dst_trampoline`, `saved_dst_prog_type`, `saved_dst_attach_type`, `st_ops`, `attach_st_ops_member_off`, `ctx_arg_info`, `arena`, `attach_btf_trace`, `stack_depth`, `verified_insns`, and `verifier_zext` are updated as verification discovers targets and properties.
- `check_map_prog_compatibility()` can set `env->prog->aux->arena` and increment `map->sleepable_refcnt` for sleepable programs. It also initializes instruction-array maps used by indirect jumps.
- For struct_ops programs, `do_check_common()` can acquire references for context arguments tagged `__ref`; corresponding leak checks are enforced by exit processing.
- `check_attach_btf_id()` may acquire a trampoline via `bpf_trampoline_get()` and retain a module reference through BTF attach metadata. The cleanup path calls `module_put(env->attach_btf_mod)`.

Rejected programs are scrubbed through the error path. Instruction-array maps are released on rejection, maps/BTFs are released unless already transferred into program aux storage, and pseudo `ldimm64` conversion is only performed after successful verification and object transfer.

## Dependencies and Integration Points

This chunk integrates with most major BPF verifier subsystems:

- Register and abstract-state helpers: `reg_state()`, `cur_regs()`, `cur_func()`, `mark_reg_known_zero()`, `mark_reg_unknown()`, `mark_reg_scratched()`, `mark_verifier_state_scratched()`, `mark_verifier_state_clean()`, and `verifier_state_scratched()`.
- Instruction validators and analyzers from earlier chunks: `check_alu_op()`, `check_load_mem()`, `check_store_reg()`, `check_atomic()`, `check_mem_access()`, `check_func_call()`, `check_kfunc_call()`, `check_helper_call()`, `check_ld_abs()`, `check_ld_imm()`, `check_cond_jmp_op()`, `check_resource_leak()`, `check_return_code()`, and `check_global_subprog_return_code()`.
- CFG and data-flow passes: `bpf_check_cfg()`, `bpf_compute_postorder()`, `bpf_stack_liveness_init()`, `bpf_compute_const_regs()`, `bpf_prune_dead_branches()`, `sort_subprogs_topo()`, `bpf_compute_scc()`, `bpf_compute_live_registers()`, and `mark_fastcall_patterns()`.
- BTF integration: `btf_vmlinux`, `btf_parse_vmlinux()`, `btf_get_by_fd()`, `__btf_get_by_fd()`, BTF type lookup helpers, BTF func-prototype distillation, module BTF refcounting, struct_ops descriptors, and BTF id sets for attach denylisting.
- Map integration: `__bpf_map_get()`, `bpf_map_inc()`, `__bpf_free_used_maps()`, map ops such as `map_direct_value_addr`, offload matching, cgroup-storage assignment, arena metadata, and instruction-array map helpers.
- Attach and trampoline integration: `bpf_check_attach_target()`, `bpf_trampoline_compute_key()`, `bpf_trampoline_get()`, raw tracepoint lookup, kallsyms, LSM validation, iterator support checks, extension-program replacement checks, and JIT capability probes.
- Kfunc integration: kfunc descriptors, special-kfunc id lists, device-bound kfunc resolution, dynptr variants, LSM dentry xattr locked variants, arena non-sleepable variants, collection metadata, object lifetime helpers, and far-call JIT support.
- User ABI integration: `union bpf_attr` supplies log options, program flags, fd arrays, and optional `log_true_size`; `bpfptr_t` abstracts kernel/user pointer copies for fd-array and log-size updates.
- Offload integration: offloaded programs receive verifier preparation, per-instruction verification, and finalization callbacks.

## Risks and Edge Cases

- Pointer-type convergence is security-sensitive. If `save_aux_ptr_type()` allows incompatible pointer classes for the same instruction, a path-safe access could become unsafe on another branch. The trust-mismatch exception is intentionally restricted to memory/BTF pointers and degrades to untrusted/readonly-conservative behavior.
- `check_indirect_jump()` depends on accurate scalar bounds in `PTR_TO_INSN` registers. Overflow checks before dividing by the 8-byte instruction-array element size prevent large `umin/umax` values from wrapping into apparently valid indexes.
- The indirect-jump temp buffer is resized from verifier-controlled bounds, and all unique jump targets are pushed or selected. Missing target validation in the instruction-array map layer would directly affect verifier control-flow coverage.
- The core loop's `env->insn_processed` complexity limit and state pruning are DoS controls. Bugs that miss pruning points, fail to pop branches, or miscount branches can reject valid programs or allow excessive verifier work.
- The `process_bpf_exit` path intentionally runs leak checks before nested function unwinding. Moving leak checks after frame cleanup would miss callback/reference-state mismatches.
- Speculative-path handling relies on `nospec`, `nospec_result`, and `error_recoverable_with_nospec()` being used only for instruction shapes that cannot skip the inserted barrier. The verifier bug check documents this assumption for future changes.
- Pseudo `ldimm64` resolution mutates instruction immediates to kernel addresses before final conversion. Error paths must release any maps/BTFs already retained, and successful paths must transfer refs before converting pseudo sources to generic loads.
- `process_fd_array()` treats every fd in a non-empty fd array as a map or BTF. Mixed or stale fds reject the load even if a particular index is never used later.
- Sleepable program map compatibility is an allowlist. New map types used by sleepable programs must be added deliberately, or they will be rejected. Conversely, adding an unsafe map type to the list could allow sleepable-context misuse.
- Arena maps require privilege, pointer-leak allowance, JIT request, JIT arena support, a single arena per program, and a configured user VM start. Any mismatch rejects the program.
- Attach validation has many target-specific constraints: fentry/fexit/fsession JIT support, no tracing attach nesting beyond one level, no extension cycles, no extension of fentry/fexit/fsession, no modifying BPF program returns, sleepability checks, denylisted kernel functions, and noreturn target rejection.
- Module BTF and kallsyms lookup paths must balance module refs on failure. `bpf_check_attach_target()` explicitly drops `mod` for many failure exits after address resolution.
- Struct_ops verification depends on GPL-compatible license, supported struct/member, function-pointer prototype, member-specific checks, private-stack JIT support, and tail-call prohibition when refcounted arguments are present.
- Kfunc fixups assume aux metadata was populated consistently by earlier kfunc verification. Missing `kptr_struct_meta`, unexpected percpu object metadata, or unresolved kfunc descriptors are treated as verifier bugs and return `-EFAULT`.
- The final `bpf_check()` error path preserves verifier-log finalization errors over earlier errors. This is intentional in code, but it can change the returned error after verification has otherwise failed.
- Extension programs temporarily inherit target verifier ops and expected attach type, then reset `expected_attach_type` to zero before return. Any early-return path that bypassed this cleanup would leak target-specific state.

## Test Signals

- Verifier selftests should cover the diagnostic `"same insn cannot be used with different pointers"` by reaching a shared load/store instruction with incompatible pointer types, plus trusted/untrusted memory/BTF merge cases that should pass with probe-memory behavior.
- Exit-path tests should cover main program return-code rejection, global subprogram return-code checks, nested BPF-to-BPF return unwinding, exception callback exits, reference leaks, and callback reference-state mismatches.
- Indirect jump tests should cover non-`PTR_TO_INSN` registers, missing/incorrect map pointers, out-of-range min/max indexes, empty target ranges, duplicate target entries, multiple pushed branches, and valid instruction-array dispatch.
- Core verifier tests should exercise complexity-limit rejection, state pruning logs, speculative-path nospec termination, recoverable speculative errors, constant-register invariant checking, signal interruption, and offload per-instruction failures.
- Pseudo-instruction tests should cover generic `ldimm64`, map fd loads, map fd-array index loads, map value direct-address loads with valid and invalid offsets, BTF-id loads for functions, variables, percpu data, structs, non-struct readonly data, invalid BTF ids, and missing vmlinux BTF.
- fd-array tests should cover zero `fd_array_cnt`, fd-array integer overflow, bad user pointers, map fds, BTF fds, non-map/non-BTF fds, duplicate objects, and index-based pseudo loads without a supplied fd array.
- Map compatibility tests should cover exclusive program hash mismatch, tracing programs with list/rbtree/spin-lock map records, socket-filter spin-lock rejection, offload device mismatch, struct_ops map rejection, sleepable map allowlist rejection, cgroup-storage duplicate rejection, arena privilege/JIT/user-VM-start constraints, and instruction-array initialization failure.
- Instruction field tests should assert rejection for reserved `dst_reg`, `src_reg`, `off`, `imm`, class, mode, and opcode combinations for ALU, jump, load, store, and `ldimm64` pairs.
- Global subprogram tests should verify lazy verification: only reachable global functions are checked, newly discovered global calls trigger another pass, exception callbacks are presumed called, and successful logs mark functions safe for prototype-compatible arguments.
- Attach-target tests should cover missing `btf_id`, invalid BTF type/name, attaching to non-JITed target programs, extension replacement type mismatch, conservative/static function replacement rejection, packet-data and sleepability mismatch for extensions, raw tracepoint typedef handling, iterator support, LSM validation, denylisted tracing targets, noreturn fexit/fsession/fmod_ret targets, and trampoline allocation failure.
- Struct_ops tests should cover non-GPL rejection, invalid attach id/member index/member type, unsupported members, custom `check_member()` failure, private-stack JIT absence, refcounted-argument tail-call rejection, context arg-info allocation failure, and successful verifier-op replacement.
- Kfunc fixup tests should cover device-bound specialization fallback, readonly skb dynptr specialization without permanently mutating `seen_direct_write`, locked dentry xattr variants, sleepable/non-sleepable dynptr/file and arena variants, object new/drop/percpu/refcount metadata checks, list/rbtree insertion metadata, cast inlining, fsession helper inlining, far-call support, and `arg_prog` aux injection.
- Top-level `bpf_check()` tests should verify resource cleanup on each major failure stage, successful transfer of used maps/BTFs, pseudo-load conversion only after acceptance, dead-code sanitization for unprivileged programs, privileged dead-code optimization, context conversion ordering before misc fixups, zext flag behavior, log true-size copyout, and final runtime selection.

## Chunk Boundary Notes

This chunk is the final control-plane portion of `verifier.c` for the verifier entry point, but it depends on earlier chunks for the implementation of register typing, memory access validation, helper/kfunc argument checking, branch-state comparison, CFG analysis, liveness, dead-code optimization, and misc instruction fixups. The final per-file research document should merge this chunk with those earlier analyses so `bpf_check()` is presented as the orchestrator rather than as standalone verifier logic.
