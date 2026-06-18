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
