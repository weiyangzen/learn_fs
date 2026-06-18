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
