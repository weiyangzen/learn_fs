# sources/distributed-fs/ceph-client/kernel/bpf/liveness.c

## Purpose

`liveness.c` implements verifier dataflow analyses for BPF register and stack-slot liveness. The results let the verifier know which registers and stack slots are live before instructions, supporting state pruning and correctness around subprograms, callbacks, helper/kfunc stack accesses, and frame-pointer-derived pointer flows.

The file has two major analyses: stack liveness across function instances and call chains, and whole-program register liveness over the control-flow graph.

## Important APIs, Types, And Functions

`struct per_frame_masks` stores `may_read`, `must_write`, and computed `live_before` stack-slot masks per instruction and frame. `struct func_instance` identifies a subprogram instance by callsite and depth and owns lazily allocated per-frame mask arrays. `struct bpf_liveness` owns the function-instance hash table, cached live-stack query, and complexity counter.

Initialization and lookup functions include `bpf_stack_liveness_init()`, `bpf_stack_liveness_free()`, `call_instance()`, `find_instance()`, `lookup_instance()`, `mark_stack_read()`, and `mark_stack_write()`.

CFG successor handling is centralized in `bpf_jmp_offset()` and `bpf_insn_successors()`. The latter accounts for normal fallthrough, jumps, exits, `ldimm64` two-instruction width, and precomputed jump tables in `insn_aux_data[idx].jt`.

Stack fixed-point functions include `update_insn()`, `update_instance()`, `bpf_live_stack_query_init()`, and `bpf_stack_slot_alive()`.

Argument/frame-pointer tracking uses `struct arg_track`, `enum arg_track_state`, `arg_track_join()`, `arg_track_alu64()`, `fill_from_stack()`, `spill_to_stack()`, `clear_stack_for_all_offs()`, and `arg_track_xfer()`.

Access recording functions include `record_stack_access_off()`, `record_stack_access()`, `record_imprecise()`, `record_load_store_access()`, `record_call_access()`, and `find_callback_subprog()`.

Recursive subprogram analysis uses `compute_subprog_args()`, `analyze_subprog()`, `merge_instances()`, `fresh_instance()`, and public `bpf_compute_subprog_arg_access()`.

Register liveness uses `struct insn_live_regs`, `compute_insn_live_regs()`, and public `bpf_compute_live_registers()`.

## Control Flow

Stack analysis starts with `bpf_compute_subprog_arg_access()`, which allocates temporary per-subprogram state and callsite stack snapshots. It walks subprograms in reverse topological order, creates or reuses `func_instance` objects, and calls `analyze_subprog()`.

`analyze_subprog()` first computes local argument/frame-pointer dataflow for one subprogram instance. It then recurses into pseudo-call callees or known callback subprograms when frame-pointer-derived arguments are passed. After analyzing a callee, it pulls the callee's entry liveness back to the caller callsite so parent stack slots stay live when the callee reads them.

`compute_subprog_args()` performs a forward fixed-point pass over the subprogram in reverse postorder. It tracks how registers and stack spill slots derive from frame pointers, propagates states to CFG successors with a lattice join, then performs a second pass to record stack reads/writes implied by loads, stores, helper calls, and kfunc calls.

After reads and writes are recorded, `update_instance()` computes stack `live_before` masks by repeatedly applying `live_before = (successor_live & ~must_write) | may_read` until no instruction changes.

Register liveness is computed by `bpf_compute_live_registers()`. It first computes instruction-level `use` and `def` masks, invokes stack/subprogram access analysis, then iterates over CFG postorder until `in` and `out` register sets reach a fixed point. Final results are stored in `env->insn_aux_data[i].live_regs_before`.

## State And Persistence Behavior

All state is verifier-run scoped. `env->liveness` persists for the lifetime of verification and is freed by `bpf_stack_liveness_free()`. Per-instance frame mask arrays are lazily allocated only for frames and instructions that observe stack accesses.

Temporary analysis arrays (`at_in`, stack snapshots, callsite stack maps, register live state) are allocated with kernel-accounted memory and freed before returning. The persistent outputs are stack liveness masks in `env->liveness` and register masks in `env->insn_aux_data`.

The query cache in `struct live_stack_query` stores the current verifier state's instances, callsites, current frame, and instruction index to avoid repeated hash lookups during stack-slot alive queries.

## Dependencies And Integration Points

This file depends on verifier structures in `linux/bpf_verifier.h`, BPF instruction encoding, verifier CFG postorder data, subprogram metadata, helper/kfunc stack access summaries, callback detection, jump table metadata, `spis_t` stack-slot bit operations, BTF-aware call summaries, and verifier logging.

It integrates directly with verifier state pruning through `bpf_stack_slot_alive()` and register liveness through `live_regs_before`. It also supports verifier debug output when `BPF_LOG_LEVEL2` is enabled.

## Risks And Edge Cases

The analysis is conservative when frame-pointer identity becomes imprecise, when callbacks are ambiguous, when helper/kfunc stack access size is unknown, or when parent-frame stack can be accessed. Conservative marking can reduce pruning efficiency but avoids unsoundness.

Function instances are keyed by callsite and depth. Incorrect keying or merging can conflate different call chains and either miss stack reads or overstate writes. `must_write` is especially subtle because repeated analysis of an instance intersects writes across passes.

Callback handling is specialized for helpers such as `bpf_loop`, `bpf_for_each_map_elem`, `bpf_find_vma`, and `bpf_user_ringbuf_drain`. Adding callback-capable helpers without updating `find_callback_subprog()` can make stack liveness inaccurate.

Complexity is bounded by `subprog_calls > 10000`; very complex call/callback graphs can fail verification with `-E2BIG`. Allocation pressure can fail verification with `-ENOMEM`.

CFG successor correctness is foundational. Incorrect handling of jump tables, `ldimm64`, exits, or conditional jumps would affect both stack and register fixed points.

## Test Signals

Relevant tests include verifier selftests for register liveness, dead register pruning, stack slot pruning, helper and kfunc stack read/write summaries, callbacks receiving stack pointers, nested subprograms, global and async callback subprograms, jump-table control flow, imprecise pointer arithmetic, partial stack writes, atomic stack operations, and BPF_LOG_LEVEL2 diagnostic output.

Stress tests should include deep call chains, repeated callsite instances, ambiguous callbacks, parent-stack access through spilled frame pointers, and large CFGs approaching the complexity limit.
