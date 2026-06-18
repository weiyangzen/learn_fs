# Research: sources/distributed-fs/ceph-client/kernel/bpf/verifier.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006019`: lines 1-8669, `Docs/researches/chunks/subset-b-006019_research.md`
- `subset-b-006020`: lines 8670-17313, `Docs/researches/chunks/subset-b-006020_research.md`
- `subset-b-006021`: lines 17314-20203, `Docs/researches/chunks/subset-b-006021_research.md`

## Chunk Research

### subset-b-006019: lines 1-8669

# sources/distributed-fs/ceph-client/kernel/bpf/verifier.c lines 1-8669

## Purpose

This chunk is the opening half of the Linux eBPF verifier implementation in `kernel/bpf/verifier.c`. It establishes verifier-wide metadata, register and stack-state primitives, reference/lock tracking, subprogram and kfunc discovery, scalar range analysis, stack spill/fill tracking, memory-access validation, BTF pointer access rules, atomic access checks, and the beginning of helper argument validation.

The verifier is a static analyzer for BPF bytecode. The introductory comment describes its two major passes: first rejecting malformed control flow, unreachable instructions, and forbidden cycles; then walking all feasible execution paths with symbolic register and stack state. This range implements many of the lower-level routines that make that second pass sound: it classifies register types, tracks pointer provenance and nullability, checks helper/kfunc argument contracts, verifies memory bounds and initialization, and maintains state snapshots for branch exploration.

This is not Ceph-specific code despite the local path prefix. It is kernel BPF verifier logic mirrored under the `ceph-client` source tree.

## Important APIs, Types, And Functions

Key data structures introduced or manipulated in this chunk:

- `bpf_verifier_ops[]`: per-program-type verifier operation table generated from `linux/bpf_types.h`.
- `struct bpf_verifier_stack_elem`: branch-exploration stack node containing a copied `bpf_verifier_state`, target instruction, previous instruction, next pointer, and verifier-log cursor.
- `struct bpf_call_arg_meta`: helper-call metadata for map pointers, raw memory mode, packet access, release registers, memory sizes, dynptr IDs, BTF/kfunc IDs, kptr fields, and constant map keys.
- `struct bpf_kfunc_meta`, `struct bpf_kfunc_btf`, and `struct bpf_kfunc_btf_tab`: kfunc prototype, BTF, module, and descriptor discovery state.
- `struct linked_reg` and `struct linked_regs`: compact history encoding used by precision backtracking to link scalar register/stack-slot precision.
- `struct bpf_reg_types` and `compatible_reg_types[]`: helper argument type compatibility tables mapping `enum bpf_arg_type` to accepted verifier register types.
- Global verifier state such as `btf_vmlinux`, `bpf_verifier_lock`, `bpf_percpu_ma_lock`, `bpf_global_percpu_ma`, and `bpf_global_percpu_ma_set`.

Major function groups:

- Logging and identity helpers: `verbose()`, `verbose_invalid_scalar()`, `btf_type_name()`, `subprog_name()`, `bpf_verbose_insn()`.
- Register classification: `reg_not_null()`, `reg_btf_record()`, `is_trusted_reg()`, `is_rcu_reg()`, `type_is_rdonly_mem()`, `is_spillable_regtype()`, `is_pointer_value()`, `is_ctx_reg()`, `is_pkt_reg()`, `is_sk_reg()`, `is_arena_reg()`.
- Dynptr state handling: `dynptr_get_spi()`, `mark_stack_slots_dynptr()`, `unmark_stack_slots_dynptr()`, `destroy_if_dynptr_stack_slot()`, `is_dynptr_reg_valid_uninit()`, `is_dynptr_reg_valid_init()`, `process_dynptr_func()`, `dynptr_id()`, `dynptr_ref_obj_id()`, `dynptr_get_type()`.
- Iterator and IRQ-flag stack objects: `mark_stack_slots_iter()`, `unmark_stack_slots_iter()`, `is_iter_reg_valid_*()`, `process_iter_arg()`, `process_iter_next_call()`, `mark_stack_slot_irq_flag()`, `unmark_stack_slot_irq_flag()`, `is_irq_flag_reg_valid_*()`.
- Reference and lock lifetime tracking: `acquire_reference()`, `acquire_lock_state()`, `acquire_irq_state()`, `release_reference_state()`, `release_lock_state()`, `release_irq_state()`, `find_reference_state()`, `find_lock_state()`, `process_spin_lock()`.
- Verifier-state allocation and branching: `copy_array()`, `realloc_array()`, `copy_reference_state()`, `copy_stack_state()`, `grow_stack_state()`, `bpf_copy_verifier_state()`, `bpf_free_verifier_state()`, `push_stack()`, `pop_stack()`, `bpf_explored_state()`, `same_callsites()`.
- Scalar/range machinery: `__mark_reg_known()`, `__mark_reg_const_zero()`, `bpf_mark_reg_unknown_imprecise()`, `bpf_mark_reg_not_init()`, `__update_reg*_bounds()`, `deduce_bounds_*()`, `reg_bounds_sync()`, `reg_bounds_sanity_check()`, `zext_32_to_64()`, `coerce_reg_to_size()`, `coerce_reg_to_size_sx()`, `coerce_subreg_to_size_sx()`.
- Subprogram/kfunc discovery: `add_subprog()`, `bpf_find_subprog()`, `bpf_find_containing_subprog()`, `bpf_find_exception_callback_insn_off()`, `fetch_kfunc_meta()`, `bpf_add_kfunc_call()`, `add_subprog_and_kfunc()`, `check_subprogs()`, `sort_subprogs_topo()`.
- Stack and memory access validation: `check_stack_write_fixed_off()`, `check_stack_write_var_off()`, `check_stack_read_fixed_off()`, `check_stack_read_var_off()`, `check_stack_access_within_bounds()`, `check_mem_region_access()`, `check_mem_access()`, `check_helper_mem_access()`, `check_stack_range_initialized()`.
- Map, context, packet, socket, BTF, and buffer access: `check_map_access_type()`, `check_map_access()`, `check_map_kptr_access()`, `check_ctx_access()`, `check_packet_access()`, `check_sock_access()`, `check_ptr_to_btf_access()`, `check_ptr_to_map_access()`, `check_buffer_access()`.
- Helper argument validation start: `resolve_map_arg_type()`, `check_reg_type()`, `check_func_arg_reg_off()`, `check_reg_const_str()`, `get_constant_map_key()`, and the beginning of `check_func_arg()`.

## Control Flow

The chunk provides building blocks used by the later main verification loop rather than a single top-level flow. The typical verification flow supported by these functions is:

1. Initialize verifier operations and starting function/register state. `init_reg_state()` marks all registers unreadable except `R10` as stack frame pointer; program-type callbacks provide context-access policy through `env->ops`.
2. Discover callable units. `add_subprog_and_kfunc()` adds subprogram entry points, resolves BPF-to-BPF calls, pseudo function references, kfunc calls, and optional exception callback declarations from BTF metadata.
3. Validate subprogram boundaries and ordering. `check_subprogs()` prevents jumps across subprogram boundaries and records tail-call and `ld_abs` properties. `sort_subprogs_topo()` topologically orders reachable subprograms and rejects recursive ordinary calls.
4. Track state through branch exploration. `push_stack()` clones the current symbolic state for later paths; `pop_stack()` restores it. `bpf_explored_state()` hashes explored states by instruction and callsite to support pruning and loop detection.
5. Process instructions by checking register operands and memory operands. `check_reg_arg()` enforces read/write register validity, caller-saved clobbering, frame-pointer immutability, subregister definitions, and zero-extension annotations. Load/store helpers call `check_mem_access()` to dispatch by pointer class.
6. Maintain symbolic state. Loads update destination register type and bounds; stores update stack slot state, map/value side conditions, or memory access maxima. Pointer loads from context, BTF objects, map values, or readonly maps can create typed pointer states or constant scalar states.
7. Validate helper and kfunc arguments. `check_func_arg()` begins per-argument verification by checking source-readability, pointer-leak rules, expected register types, fixed-offset requirements, map/key/value memory validity, lock/timer/kptr/dynptr/iterator contracts, and reference-release metadata.

Loop handling for iterator kfuncs is explicitly modeled in this chunk. `process_iter_next_call()` forks verifier state: one path assumes `iter_next()` returned non-NULL and queues another active iteration, while the current path marks the iterator drained and `R0 == 0`. It can widen imprecise scalars against a previous loop-entry state to prove convergence for common iterator loops.

## State And Persistence Behavior

The verifier state is entirely in-memory and scoped to program verification, but it persists across many symbolic branches:

- `bpf_verifier_state` owns current stack frames, acquired reference array, lock counters, active IRQ/lock IDs, branch counters, parent state, DFS depth, callback and may-goto depths, sleepable-context state, and jump history.
- `bpf_func_state` owns per-frame registers and allocated stack slots. `grow_stack_state()` lazily expands tracked stack depth and records high-water stack depth in `env->subprog_info`.
- Stack slots store byte-level `slot_type[]` plus a `spilled_ptr` register snapshot. Special slot types include `STACK_SPILL`, `STACK_DYNPTR`, `STACK_ITER`, `STACK_IRQ_FLAG`, `STACK_ZERO`, `STACK_MISC`, `STACK_INVALID`, and `STACK_POISON`.
- References are tracked in `state->refs` with typed IDs for ordinary pointer references, locks, resource spin locks, IRQ state, and related lifetime constraints. The chunk allocates, copies, resizes, and releases this state.
- Scalar state persists through `tnum` bit uncertainty and signed/unsigned min/max bounds for both 64-bit and 32-bit views. `reg_bounds_sync()` keeps those domains synchronized and `reg_bounds_sanity_check()` defends invariants.
- Kfunc descriptor state persists in `prog->aux->kfunc_tab` and `prog->aux->kfunc_btf_tab`, including module BTF references and module references that are later freed by `bpf_free_kfunc_btf_tab()`.
- Program auxiliary maxima such as `max_pkt_offset`, `max_ctx_offset`, `max_tp_access`, `max_rdonly_access`, and `max_rdwr_access` are updated during access checks for later JIT/runtime use.

The chunk avoids persistent on-disk data. Its durable outputs are verifier accept/reject decisions, transformed auxiliary metadata, and retained references to maps, BTFs, modules, and kfunc descriptors inside `bpf_prog->aux`.

## Dependencies And Integration Points

This code depends heavily on kernel BPF and BTF infrastructure:

- BPF core types and helper metadata from `linux/bpf.h`, `linux/bpf_verifier.h`, `linux/filter.h`, and UAPI BPF/BTF headers.
- Program-type verifier callbacks through `struct bpf_verifier_ops`, especially `is_valid_access`, `convert_ctx_access`, and `btf_struct_access`.
- BTF helpers such as `btf_type_by_id()`, `btf_name_by_offset()`, `btf_struct_access()`, `btf_struct_ids_match()`, `btf_kfunc_flags()`, `btf_check_iter_arg()`, `btf_find_struct_meta()`, and trusted-field tag helpers.
- Map implementation hooks and metadata: `map_direct_value_addr`, `map_btf_id`, `map->record`, `bpf_map_flags_to_cap()`, `bpf_map_write_active()`, map key/value sizes, and special map types such as sockmap, sockhash, bloom filter, insn array, and XSK map.
- Program-type and networking access validators: packet direct access policy, socket access checks, flow-key access, syscall context variable-offset allowance, LSM return-value ranges, and XDP/skb dynptr types.
- JIT support probes for kfunc calls, private stack, arena atomics, and architecture-specific atomic width support.
- Module/BTF lifetime management through module BTF fds, `btf_get_by_fd()`, `btf_try_get_module()`, `module_put()`, and `btf_put()`.
- Verifier precision and pruning infrastructure outside this chunk, including `bpf_push_jmp_history()`, `bpf_mark_chain_precision()`, `mark_verifier_state_scratched()`, `mark_reg_scratched()`, and related backtracking helpers.

The chunk also exports or provides non-static helpers used elsewhere in the verifier/kernel BPF path, including `bpf_subprog_is_global()`, `bpf_mark_subprog_exc_cb()`, `bpf_is_sync_callback_calling_insn()`, `bpf_is_async_callback_calling_insn()`, `bpf_is_may_goto_insn()`, `bpf_clear_jmp_history()`, `bpf_free_verifier_state()`, `bpf_copy_verifier_state()`, `bpf_explored_state()`, `bpf_free_backedges()`, `bpf_mark_reg_unknown_imprecise()`, `bpf_verbose_insn()`, `bpf_bt_sync_linked_regs()`, `mark_chain_precision()`, `bpf_map_is_rdonly()`, `bpf_map_direct_read()`, and `bpf_prog_has_kfunc_call()`.

## Risks And Edge Cases

- Stack-object aliasing is high risk. Dynptrs, iterators, IRQ flags, and spilled pointers occupy stack slots with special invariants; partial writes, variable-offset writes, or helper raw-mode writes can destroy or alias them. The chunk explicitly rejects or scrubs many such cases.
- Reference tracking must be exact. Lost `ref_obj_id`, out-of-order IRQ restore, missing release, incorrect dynptr clone handling, or lock-state mismatch can either reject valid programs or permit resource leaks.
- Bounds analysis is subtle. The verifier maintains four scalar ranges plus `tnum`; incorrect synchronization can make unsafe pointer arithmetic appear safe or make valid code unverifiable. `reg_bounds_sanity_check()` is a key internal guard.
- Variable offsets are restricted differently for privileged and unprivileged programs. Stack variable-offset accesses interact with Spectre mitigations and uninitialized-stack leak prevention, so privilege flags such as `allow_uninit_stack`, `bypass_spec_v1`, and `allow_ptr_leaks` materially change behavior.
- BTF trust and RCU annotations are conservative and compatibility-sensitive. Walking trusted, RCU, untrusted, nullable, percpu, user, or allocated BTF pointers changes flags; mistakes can expose unsafe dereferences or reject existing programs.
- Kfunc resolution depends on BTF, GPL compatibility, JIT support, module fd arrays, module lifetime, kallsyms lookup, and kfunc flag sets. Invalid or stale module BTF state can fail verification.
- Map kptr fields and special map fields require exact offsets, sizes, and BTF records. Direct loads/stores touching any part of kptr/timer/workqueue/task-work fields are tightly restricted.
- Stack-depth validation must account for bpf2bpf calls, tail calls, async callbacks, exception callbacks, private stack support, and architecture/JIT stack rounding. Bad accounting can allow excessive stack use or reject valid call graphs.
- The requested range ends inside `check_func_arg()` after the `ARG_PTR_TO_SPIN_LOCK` case begins. Later cases and final helper-call control flow belong to the next chunk, so this document should not be read as complete helper validation coverage.

## Test Signals

Useful validation signals for this chunk include:

- Kernel BPF verifier selftests covering stack spills/fills, partial stack accesses, variable-offset stack reads/writes, uninitialized stack behavior, `STACK_ZERO`, poisoned stack slots, and Spectre-related stack restrictions.
- Dynptr selftests for local, ringbuf, skb, xdp, skb metadata, and file dynptrs: initialization, readonly vs mutable arguments, release paths, clone/refcount behavior, slice invalidation, and overwrite rejection.
- Iterator kfunc selftests for `iter_new`, `iter_next`, and `iter_destroy`, including convergence, nested/alternate loop shapes, RCU-protected iterators, and missing destroy/reference leak cases.
- Reference and lock tests for socket/ringbuf/kptr references, resource spin locks, bpf spin locks, nested locks, out-of-order unlocks, IRQ flag save/restore order, and callbacks where locking is forbidden.
- BTF pointer tests for trusted, untrusted, RCU, nullable, percpu, user, and allocated object pointer walks; map kptr load/store rules; kptr exchange type matching; and program-allocated object writes.
- Map access tests for read-only direct-value constant folding, insn-array special pointer loads, map key/value bounds, helper indirect access to BTF fields, sockmap/sockhash argument rewriting, bloom-filter peek value handling, and constant-map-key extraction.
- Context/packet/socket/buffer tests across program types: direct packet read/write permissions, `max_pkt_offset`, ctx field rewrites and `max_ctx_offset`, syscall variable ctx offsets, socket access validation, tracepoint buffer maxima, and rdonly/rdwr buffer maxima.
- Atomic instruction tests for invalid sizes/opcodes, pointer leaks through atomic operands, unsupported pointer base types, arena atomic JIT support, and 64-bit acquire/release availability on 32-bit architectures.
- Kfunc tests for missing vmlinux BTF, non-GPL programs, JIT-disabled programs, module BTF fd lookup, invalid offsets, duplicated descriptors, implicit-argument `_impl` prototype lookup, and device-bound kfunc checks.
- Internal invariant testing with `env->test_reg_invariants` enabled should catch const/range/tnum mismatches after scalar arithmetic, loads, sign extension, zero extension, and subregister operations.

## Cross-Chunk Notes

This is chunk 1 of 3 for `sources/distributed-fs/ceph-client/kernel/bpf/verifier.c`. It covers the verifier's foundational machinery and stops at line 8669 in the middle of `check_func_arg()`. The next chunk should continue helper argument cases, release/reference cleanup, callback handling, kfunc-specific argument mapping, and the main instruction verification paths before the final per-file document makes complete claims about the verifier as a whole.

### subset-b-006020: lines 8670-17313

# sources/distributed-fs/ceph-client/kernel/bpf/verifier.c lines 8670-17313

## Scope

This chunk covers the middle verifier implementation for Linux eBPF programs in the Ceph client kernel source snapshot. The range starts in helper-argument validation, then covers helper call verification, BPF-to-BPF and callback frame setup, reference and lock resource tracking, kfunc argument and return-type handling, pointer/scalar ALU range propagation, conditional branch refinement, `LD_IMM64` and `LD_ABS/IND` checks, return-code validation, and fastcall pattern discovery.

The code is not CephFS-specific. It is part of the imported kernel BPF verifier and is security-critical because it decides whether untrusted or privileged BPF bytecode is safe to load, what register and stack states are possible at each instruction, and what later JIT/fixup phases may rewrite.

## Purpose

The central purpose of this chunk is to preserve verifier invariants while modeling complex BPF control flow and kernel API calls:

- Helpers and kfuncs are checked against declared prototypes, program type, GPL restrictions, sleepability, map compatibility, memory-size pairs, reference ownership, dynptr/iterator state, callback subprograms, and return types.
- BPF-to-BPF calls and helper/kfunc callbacks are expanded into verifier frames or queued states, with call/return state transfer and callback return-range enforcement.
- References, locks, RCU/preempt/IRQ-disabled regions, timers, workqueues, graph nodes, and kptrs are tracked so programs cannot leak resources or use invalid pointers.
- ALU and branch instructions refine scalar ranges, packet pointer ranges, nullable pointer states, and linked scalar IDs, while installing Spectre-v1 sanitation metadata for JIT fixups.
- Program exits and global subprogram exits enforce return value type/range policies based on program and attach type.
- Fastcall spill/fill patterns are detected so later fixups can remove redundant stack traffic only when the compiler contract is proven.

## Important APIs, Types, And Functions

Helper-call validation:

- `bpf_get_helper_proto()` obtains a helper prototype from verifier ops.
- `check_func_proto()` validates helper prototype consistency by delegating to `check_raw_mode_ok()`, `check_arg_pair_ok()`, `check_mem_arg_rw_flag_ok()`, and `check_btf_id_ok()`.
- `check_helper_call()` is the main helper verifier path. It checks program-type availability, GPL-only status, sleepability, argument types through `check_func_arg()`, memory access, reference release/acquisition, callback helpers, return register typing, map compatibility, callchain buffers, packet-data invalidation, and tail-call behavior.
- `check_map_func_compatibility()` enforces two-way compatibility between helper IDs and map types, including prog arrays, perf/ring/user ring buffers, cgroup maps, dev/cpu/xsk maps, map-in-map, sockmap/sockhash, queues/stacks, storage maps, and bloom filters.
- `record_func_map()` and `record_func_key()` store call-site map/key metadata in `env->insn_aux_data[]`, including tail-call prog-array key precision.
- `bpf_helper_stack_access_bytes()` reports stack read/write size for helper arguments for later initialization analysis.

BPF-to-BPF calls and callbacks:

- `setup_func_entry()` allocates and initializes a new `bpf_func_state` frame, enforces `MAX_CALL_FRAMES`, and invokes a callee-state setup callback.
- `btf_check_func_arg_match()` and `btf_check_subprog_call()` compare subprogram BTF argument metadata against current register states and mark unreliable BTF when compiler optimization or mismatch invalidates assumptions.
- `check_func_call()` handles static and global subprogram calls. Global subprograms are assumed valid after argument checks and are verified separately; static calls enter a new frame immediately.
- `push_callback_call()` enqueues synchronous callback verification or creates an async callback state for timer/workqueue/task-work-style callbacks.
- Callback argument setup functions include `map_set_for_each_callback_args()`, `set_map_elem_callback_state()`, `set_loop_callback_state()`, `set_timer_callback_state()`, `set_find_vma_callback_state()`, `set_user_ringbuf_callback_state()`, `set_rbtree_add_callback_state()`, and `set_task_work_schedule_callback_state()`.
- `prepare_func_exit()` returns from subprogram frames, enforces callback return ranges, copies callee `R0` to caller for normal calls, unwinds frames, and widens callback loop scalars when needed.

Reference, lock, and resource handling:

- `release_reference_nomark()`, `release_reference()`, `invalidate_non_owning_refs()`, `check_reference_leak()`, and `check_resource_leak()` manage acquired pointer references and reject leaks on tail calls, `LD_ABS/IND`, and exits.
- `clear_all_pkt_pointers()` invalidates packet pointers and packet dynptr slices after helpers/kfuncs can move packet data.
- `mark_pkt_end()`, `find_good_pkt_pointers()`, and `try_match_pkt_pointers()` encode packet range proofs from comparisons with `data_end` or packet metadata/data pointers.
- `ref_set_non_owning()` and `ref_convert_owning_non_owning()` convert graph-node references from owning to non-owning form under lock protection.
- `check_reg_allocation_locked()` proves a graph root/list/rbtree operation is protected by a spin lock in the same allocation.
- `process_irq_flag()` validates stack-resident IRQ flags for save/restore kfuncs and marks or unmarks stack slots as initialized IRQ flags.

Kfunc validation:

- `bpf_fetch_kfunc_arg_meta()` loads kfunc BTF metadata, flags, prototype, and name after checking allowlists.
- The `special_kfunc_list` BTF ID table and helpers such as `is_bpf_obj_new_kfunc()`, `is_bpf_obj_drop_kfunc()`, `is_bpf_refcount_acquire_kfunc()`, `is_bpf_list_push_kfunc()`, `is_bpf_rbtree_add_kfunc()`, `is_bpf_throw_kfunc()`, `is_bpf_wq_set_callback_kfunc()`, and `is_task_work_add_kfunc()` classify special verifier semantics.
- `get_kfunc_ptr_arg_type()` maps BTF argument shape and suffixes such as `__sz`, `__szk`, `__k`, `__map`, `__alloc`, `__uninit`, `__nullable`, `__str`, and `__irq_flag` to verifier argument categories.
- `check_kfunc_args()` is the main kfunc argument validator. It handles scalars, constants, context pointers, BTF IDs, trusted/RCU pointers, maps, allocated objects, refcounted kptrs, dynptrs, iterators, graph roots/nodes, callbacks, const strings, timers, workqueues, task work, IRQ flags, resource spin locks, and memory/size pairs.
- `check_special_kfunc()` sets special return-state behavior for object allocation, refcount acquire, list/rbtree node APIs, casts, readonly casts, dynptr slices, and allocator metadata.
- `check_kfunc_call()` orchestrates kfunc verification, including destructive and sleepable restrictions, RCU/preempt state transitions, callback kfuncs, release/acquire handling, graph insertion conversion, `bpf_throw`, return register typing, packet pointer invalidation, iterator next handling, and session-cookie flags.
- `bpf_kfunc_stack_access_bytes()` reports stack access size for kfunc pointer arguments.

ALU and branch analysis:

- `adjust_ptr_min_max_vals()` handles pointer plus/minus scalar arithmetic, including pointer-type restrictions, nullable pointer rejection, packet range invalidation, bounds synchronization, and Spectre-v1 sanitation setup.
- `sanitize_ptr_alu()`, `sanitize_val_alu()`, `sanitize_speculative_path()`, `sanitize_check_bounds()`, and related helpers populate sanitation metadata and explore speculative paths when pointer/scalar ALU could otherwise feed unsafe memory accesses.
- `scalar*_min_max_*()` helpers update 32-bit and 64-bit signed/unsigned ranges and `tnum` values for add, sub, mul, div, mod, bitwise ops, shifts, arithmetic shifts, and byte swaps.
- `adjust_scalar_min_max_vals()` applies scalar ALU semantics and zero-extension for ALU32 operations.
- `adjust_reg_min_max_vals()` chooses pointer arithmetic versus scalar arithmetic, tracks linked scalar IDs and constant deltas, and supports arena-pointer arithmetic.
- `check_alu_op()` validates ALU instruction operands, immediate div/mod by zero, invalid shifts, pointer partial copies/sign-extension, MOV semantics, arena address-space casts, and final bounds sanity.
- `is_branch_taken()`, `is_scalar_branch_taken()`, `is_pkt_ptr_branch_taken()`, `simulate_both_branches_taken()`, `regs_refine_cond_op()`, and `check_cond_jmp_op()` predict branches when possible, split states when not, refine scalar ranges/tnums on true and false branches, mark nullable pointers as null/non-null, synchronize linked scalar registers, and maintain jump history.

Other verifier entry points in this chunk:

- `check_ld_imm()` validates `BPF_LD_IMM64` forms for raw constants, map pointers, map values, BTF IDs, arena values, and pseudo function pointers used for callbacks.
- `check_ld_abs()` validates legacy `BPF_LD_ABS`/`BPF_LD_IND` skb loads, including program type, `R6` context, resource-leak safety, caller-saved clobbers, and hidden subprogram exit behavior.
- `return_retval_range()`, `program_returns_void()`, `check_return_code()`, and `check_global_subprog_return_code()` enforce program/subprogram return contracts.
- `bpf_verifier_inlines_helper_call()`, `bpf_get_call_summary()`, `mark_fastcall_pattern_for_call()`, and `mark_fastcall_patterns()` detect compiler-generated fastcall spill/fill patterns.
- `adjust_btf_func()` updates function-info instruction offsets after subprogram discovery.
- `bpf_clear_singular_ids()` clears scalar IDs that have no matching peer in the verifier state.

## Control Flow

Helper call control flow starts in `check_helper_call()`. The verifier resolves the helper prototype, checks program type and GPL constraints, validates the prototype itself, rejects sleepable helpers in non-sleepable regions, records non-sleepable call-site metadata, and iterates through up to five arguments with `check_func_arg()`. The argument loop fills `bpf_call_arg_meta`, which later drives map recording, tail-call key tracking, memory initialization checks, reference release, callback scheduling, dynptr special cases, return register typing, and packet pointer invalidation.

For helper callbacks, the call does not simply continue linearly. `push_callback_call()` checks BTF argument compatibility for the callback subprogram and then either pushes a normal callback state or creates an async callback state. Normal callbacks re-enter the callback subprogram as another queued verifier path; async callbacks start from a special async state and mark callback frames as async. Each callback setup function synthesizes callback argument registers from the helper/kfunc call arguments and constrains callback `R0` with `callback_ret_range`.

BPF-to-BPF calls use two paths. Static subprogram calls allocate a new frame with `setup_func_entry()`, copy `R1` through `R5`, clear caller-saved registers in the caller, and jump verifier instruction flow to the callee start. Global subprogram calls check BTF and context restrictions but are treated as separately verified: the current state clears caller-saved registers, marks packet pointers invalid if the callee can change packet data, and produces an unknown scalar return for non-void globals.

Kfunc call control flow mirrors helpers but is BTF-driven. `check_kfunc_call()` fetches metadata, handles special forked failure paths for resource spin-lock acquisition, rejects disallowed destructive/sleepable calls, validates each argument with `check_kfunc_args()`, schedules callbacks for rbtree/workqueue/task-work kfuncs, updates RCU/preempt counters, handles release/conversion of references, clobbers caller-saved registers, and then builds `R0` based on scalar, pointer, struct pointer, void pointer, or special kfunc semantics. If the kfunc is `bpf_throw`, it delegates to the full exit path as an exception exit.

Return flow through `prepare_func_exit()` is conservative. A callee cannot return stack pointers. Normal callees copy `R0` back to the caller. Callback callees must return a scalar within their declared range and are sent back to the callsite so the callback iteration can be unrolled until state pruning converges. The callee frame is freed and `curframe` is decremented.

ALU flow starts in `check_alu_op()`. MOV and unary operations are handled specially; all other ALU operations delegate to `adjust_reg_min_max_vals()`. That function decides whether operands are scalars, pointers, or arena pointers. Pointer arithmetic goes to `adjust_ptr_min_max_vals()` and scalar arithmetic goes to `adjust_scalar_min_max_vals()`. Both update abstract register ranges and `tnum` state, and pointer/scalar add/sub additionally records sanitation information for JIT fixups when Spectre-v1 mitigation is needed.

Conditional jumps first check operands and build `true_reg*`/`false_reg*` scratch states. If `is_branch_taken()` proves a direction, the verifier follows only that side and may push the untaken side as a speculative path. Otherwise it pushes the taken branch as `other_branch`, refines both branches with `regs_refine_cond_op()`, copies refined states back into current and queued states, synchronizes linked scalar IDs, lifts nullable pointers on null checks, and learns packet access ranges from packet pointer comparisons.

`LD_IMM64` flow decodes `src_reg` pseudo modes. Plain loads create scalar constants. Pseudo BTF IDs restore pre-decoded BTF variable state. Pseudo function pointers require BTF func info and static linkage, then become `PTR_TO_FUNC`. Map pseudo loads produce `CONST_PTR_TO_MAP` or `PTR_TO_MAP_VALUE`, with arena maps treated as unknown map-backed values.

`LD_ABS/IND` is treated as an implicit helper-like skb access. It is allowed only for socket-filter, sched-cls, and sched-act program types, requires `R6` to be a context pointer, rejects outstanding references/locks because generated code can exit early, clobbers caller-saved registers, writes an unknown 32-bit-ish value into `R0`, and in subprograms explores the generated hidden exit path.

## State And Persistence Behavior

The persistent verifier state is primarily `env->cur_state`, its call frames, `env->insn_aux_data[]`, `env->subprog_info[]`, and fields of `env->prog`/`env->prog->aux`. This chunk mutates all of them.

Register state persists across instruction analysis in `bpf_reg_state`: type, ID, ref object ID, BTF type, map pointer, map UID, offset/range bounds, `tnum`, dynptr ID, memory size, precision, and subregister definition. Calls deliberately clear caller-saved registers and rebuild `R0` so stale argument knowledge does not survive a helper, kfunc, or subprogram call.

Reference state persists in `bpf_verifier_state.refs[]`. Acquiring helpers and kfuncs allocate IDs with `acquire_reference()`. Release helpers/kfuncs remove those IDs and invalidate or transform every register copy with the same `ref_obj_id`. Null checks on nullable acquired references release the reference state in the null branch because the pointer was not actually acquired at runtime.

Lock and critical-section state persists in `env->cur_state`: active spin locks, active resource locks, active IRQ flags, active RCU locks, and active preempt-disable count. This state gates sleepable helpers/kfuncs, graph APIs, tail calls, `LD_ABS/IND`, resource-leak checks, and return paths. RCU unlock also downgrades spilled/register MEM_RCU pointers to untrusted non-RCU pointers when the outermost RCU region ends.

Callback state persists through queued verifier states. `callback_depth`, `callback_unroll_depth`, `in_callback_fn`, `in_async_callback_fn`, `async_entry_cnt`, and `callback_ret_range` constrain callback recursion/unrolling and return values. `update_loop_inline_state()` records whether a `bpf_loop()` callsite is suitable for inlining by tracking zero flags and a stable callback subprogram.

Instruction auxiliary state persists in `env->insn_aux_data[]`. This chunk records map pointer state, constant map keys, non-sleepable callsites, kfunc iterator-next markers, object allocation sizes, kptr struct metadata, insert offsets for graph operations, ALU sanitation state and limits, fastcall spill/fill pattern markers, `arg_prog` registers, and subprogram fastcall stack offsets. Later fixup and JIT phases depend on these side effects.

Scalar ID state persists to propagate facts across copied or offset-related scalar registers. ALU add/sub may record constant deltas under `BPF_ADD_CONST32` or `BPF_ADD_CONST64`; branch refinement then uses `collect_linked_regs()` and `sync_linked_regs()` to update all live linked registers and spilled scalar copies. `bpf_clear_singular_ids()` later removes IDs that no longer link multiple values.

Packet pointer state is intentionally invalidated by helpers and kfuncs that may move packet data. Range proofs learned by packet comparisons persist in `reg->range` for all registers with the same packet pointer ID, but arithmetic with unknown offsets or data-changing calls clears those proofs.

Program-level state is also updated: callchain buffer allocation flags, `call_get_stack`, `call_get_func_ip`, `call_session_cookie`, `seen_exception`, and `enforce_expected_attach_type` are set as the verifier sees relevant helpers, kfuncs, and return ranges.

## Dependencies And Integration Points

This code depends on the broader kernel BPF verifier infrastructure defined earlier and later in `verifier.c` and related headers: register-state helpers, stack-state helpers, BTF APIs, map metadata, dynptr and iterator helpers, reference tracking, log/verbose helpers, subprogram discovery, state queue/pruning, JIT capability probes, and BPF instruction decoding macros.

Kernel subsystem dependencies include:

- BTF and vmlinux BTF: kfunc metadata, typed pointers, argument suffix conventions, struct identity matching, and special BTF ID tables.
- BPF maps: map type compatibility, direct value addresses for const strings, map UID tracking for inner maps, key/value sizes, storage maps, ring/user-ring buffers, queues/stacks, socket maps, and arena maps.
- Networking: packet pointer types, skb/XDP dynptrs, `LD_ABS/IND` skb access, packet-data-changing helpers/kfuncs, and program types that can access skb data.
- Tracing, LSM, struct_ops, cgroup, netfilter, kprobe, raw tracepoint, and extension program attach types: return range and helper/kfunc availability vary by these modes.
- Memory allocators and global BPF object allocators for `bpf_obj_new` and `bpf_percpu_obj_new`.
- JIT support: subprogram tail calls, exception support, inline helper availability, Spectre ALU fixups, and fastcall spill/fill removal.
- Kernel capabilities and config options: destructive kfuncs require `CAP_SYS_BOOT`; callchain helpers depend on `CONFIG_PERF_EVENTS`; some special kfunc IDs are conditionally present.

The main integration point outside verification is the fixup/JIT lane. Sanitization metadata, map/key metadata, call summaries, fastcall pattern markers, object allocation metadata, and kfunc call annotations are all consumed later to patch instructions, inline helpers, enforce fastcall stack contracts, specialize map accesses, and generate safe machine code.

## Risks And Edge Cases

This range is security-sensitive. Any unsound register type, range, nullness, or reference transition can allow invalid memory access, use-after-free, pointer leaks, resource leaks, or unsafe JIT rewrites.

Helper and kfunc prototype drift is a major risk. The verifier trusts helper prototypes and kfunc BTF annotations to describe memory access, mutability, constant sizes, reference semantics, and callback behavior. Incorrect `MEM_UNINIT`, `__sz`, `__k`, `__nullable`, `KF_ACQUIRE`, `KF_RELEASE`, `KF_RCU`, `KF_SLEEPABLE`, or callback markings can make safe programs fail or unsafe programs pass.

Map compatibility is easy to break when adding new map types or helpers. `check_map_func_compatibility()` is intentionally two-way; adding a helper to a map-type switch but not to the helper switch, or forgetting readonly map restrictions in `record_func_map()`, can produce inconsistent verifier behavior.

Reference handling has subtle branch behavior. Nullable acquired references must be released in null branches, kptr exchange under RCU can convert allocated percpu references into MEM_RCU instead of invalidating them, and graph insertion first converts owning refs to non-owning refs before releasing the owning reference. A missed copy in registers or spilled state can leave dangling aliases.

Critical-section state must stay balanced. Unmatched RCU unlock, preempt enable, IRQ restore, resource-spin unlock, or helper/kfunc calls that can sleep inside lock/RCU/preempt/IRQ-disabled regions must be rejected. False negatives can deadlock or sleep in atomic context; false positives reject valid BPF programs.

Callback verification can explode state if callback unrolling and pruning do not converge. `bpf_loop()` and map iteration rely on callback depth, return ranges, precision marking, and scalar widening. A change that loses widening or callback-depth reset can cause verifier complexity regressions.

Graph APIs require same-allocation locking and exact BTF field offsets. List/rbtree roots and nodes are accepted only at constant offsets and only when root/node BTF records match. Incorrect `graph_root` metadata or lock ID tracking can allow mutation of a graph structure outside its protecting spin lock.

ALU range math must handle undefined, overflowing, and BPF-specific arithmetic precisely. Division or modulo by zero has BPF-defined behavior for register divisors but immediate zero is rejected; signed division of `S{32,64}_MIN / -1` is special-cased; shifts require constant in-range shift counts for precise analysis; byte swaps may scramble ranges and must clear scalar IDs. Mistakes here affect both safety proofs and verifier precision.

Spectre sanitation is path-sensitive. `sanitize_ptr_alu()` must reject unsupported pointer types, mixed signed bounds, out-of-range pointer movement, and incompatible sanitation metadata merged from different paths. If sanitation metadata is too weak, speculative execution could reach unsafe memory; if too strong or inconsistent, valid unprivileged programs fail.

Pointer comparisons are intentionally narrow. Comparing arbitrary pointers is rejected except for null checks and known packet pointer patterns. PTR_TO_BTF_ID nullability is not propagated the same way as some other pointer types because kernel struct pointers may be nullable without explicit `PTR_MAYBE_NULL` semantics.

Global subprogram handling assumes separate verification. Incorrectly marking global subprograms as valid, missing `changes_pkt_data`, or accepting invalid BTF arguments can let callers retain stale packet pointers or use wrong return assumptions.

Fastcall pattern removal is only safe if every spill/fill stack slot is exclusively part of recognized patterns. The detection logic marks patterns but leaves unsupported calls' spill counts unset for forward compatibility. Any later contract checker must honor `keep_fastcall_stack` and `fastcall_stack_off` precisely.

## Test Signals

Useful validation signals for this chunk include:

- Run upstream-style verifier selftests for helpers, kfuncs, callbacks, dynptrs, iterators, kptrs, graph APIs, spin locks, resource locks, RCU, preempt disable/enable, IRQ save/restore, tail calls, and exception kfuncs.
- Exercise map/helper compatibility tests for every map type handled here, including readonly program maps, sockmap/sockhash update restrictions by program type, prog-array tail calls with and without subprograms, ringbuf/user-ringbuf dynptr helpers, and storage-map `kptr_xchg`.
- Test helper and kfunc memory access with fixed sizes, runtime sizes, zero sizes, `MEM_UNINIT`, const strings, stack buffers, map values, dynptrs, iterators, and nullable memory/size pairs.
- Test callback helpers and kfuncs: `bpf_for_each_map_elem`, `bpf_loop`, timers, workqueues, task work, `bpf_find_vma`, user ringbuf drain, and rbtree add. Include invalid callback signatures, non-static pseudo functions, bad return ranges, callback recursion/unroll depth, and async callback return handling.
- Test reference lifetime paths: acquire/release success, release without acquire, null branch of acquire-returning helper, `kptr_xchg`, object drop, percpu object drop, refcount acquire, list/rbtree insertion conversion, exception exit, tail call, `LD_ABS/IND`, and normal program exit.
- Test lock and critical-section rejection: sleepable helper/kfunc under spin lock, RCU, preempt-disabled, IRQ-disabled, and resource-spin regions; unmatched unlock/restore; graph API without same-allocation lock; rbtree callback restrictions.
- Test kfunc BTF argument suffixes and flags with valid and invalid BTF: `__sz`, `__szk`, `__k`, `__ign`, `__map`, `__alloc`, `__uninit`, `__refcounted_kptr`, `__nullable`, `__str`, `__irq_flag`, implicit args, and `bpf_prog_aux` args.
- Test return typing for kfuncs: scalar sizes, void, void pointers as scalars, non-struct pointers as `PTR_TO_MEM`, struct pointers as `PTR_TO_BTF_ID`, nullable returns, acquired refs, RCU-protected returns, iter-next returns, object allocation metadata, dynptr slices, readonly casts, and kernel-context casts.
- Run ALU verifier tests for pointer arithmetic, packet pointer range invalidation, stack/map pointer bounds, scalar range propagation, ALU32 zero-extension, signed/unsigned div/mod edge cases, shift bounds, byte swaps, linked scalar IDs with constant deltas, and arena pointer arithmetic.
- Run unprivileged/Spectre tests that force ALU sanitation: unknown scalar add/sub to stack/map pointers, mixed signed bounds, different paths/maps/scalars merging at one instruction, and speculative side-path exploration.
- Test conditional branch refinement for scalar equality/inequality, signed/unsigned ordering, `JSET` true/false branches, 32-bit jumps, null checks of maybe-null pointers, pointer-vs-zero comparisons, packet pointer versus `data_end`, and linked scalar synchronization through branches.
- Test `LD_IMM64` pseudo modes: constants, map FD/index, map value, arena map value, BTF ID variables, pseudo function pointers with missing func info, non-static callback functions, and invalid source register values.
- Test `LD_ABS/IND` in allowed and disallowed program types, with wrong `R6`, outstanding refs/locks, nonzero offsets, explicit `IND` source checks, and subprogram hidden-exit behavior.
- Test return-code enforcement across program types: cgroup skb/sock/sockaddr/device/sysctl/sockopt, tracing attach types, raw tracepoint with/without attach BTF ID, kprobe session versus regular kprobe, sk lookup, LSM cgroup and non-cgroup hooks, netfilter, struct_ops pointer returns, extension programs, async callbacks, and global subprograms.
- Test fastcall pattern detection with supported inline helpers/kfuncs, unsupported forward-compatible patterns, wrong offsets, wrong registers, extra stack accesses to fastcall slots, multiple subprograms, and later fixup removal disabled by `keep_fastcall_stack`.

## Cross-Chunk Notes

This chunk starts in the middle of argument validation and ends just before later state-equivalence logic beginning with `reg_type_mismatch_ok()`. Earlier chunks should cover base register, stack, dynptr, iterator, and helper argument primitives referenced here. Later chunks should cover state pruning/equivalence, main instruction dispatch, final verification passes, fixups, and cleanup. The merge lane should combine this document with adjacent `verifier.c` chunks into the final per-file research report.

### subset-b-006021: lines 17314-20203

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
