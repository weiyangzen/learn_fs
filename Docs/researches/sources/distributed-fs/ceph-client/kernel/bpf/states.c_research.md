# sources/distributed-fs/ceph-client/kernel/bpf/states.c

## Purpose
`states.c` implements BPF verifier state pruning, equivalence, liveness cleanup, precision propagation, and loop/SCC bookkeeping. It decides when a verifier path can be stopped because a previously explored state is at least as conservative, while preserving scalar ID relationships, reference ownership, stack metadata, iterator convergence rules, and precision/read marks needed for later safety checks.

## Important APIs, Types, and Functions
The exported entry points are `bpf_is_state_visited()` and `bpf_update_branch_counts()`. `bpf_is_state_visited()` is called at verifier checkpoints to clean the current state, compare it against states stored for the current instruction, detect loops, propagate precision, add SCC backedges, evict unhelpful states, or store a new checkpoint. `bpf_update_branch_counts()` decrements parent branch counts as paths finish, exits SCC visits, and frees eligible verifier states.

SCC helpers include `compute_scc_callchain()`, `scc_visit_lookup()`, `scc_visit_alloc()`, `maybe_enter_scc()`, `maybe_exit_scc()`, `add_scc_backedge()`, `incomplete_read_marks()`, and `propagate_backedges()`. State comparison helpers include `range_within()`, `check_ids()`, `check_scalar_ids()`, `regsafe()`, `stacksafe()`, `refsafe()`, `func_states_equal()`, and `states_equal()`. Cleanup and precision helpers include `clean_verifier_state()`, `__clean_func_state()`, `propagate_precision()`, `mark_all_scalars_imprecise()`, and the late-init `unbound_reg_init()`.

## Control Flow
At each checkpoint, `bpf_is_state_visited()` decides whether adding a new state is worthwhile based on force-checkpoint flags, jump history, and processed instruction/jump deltas. It first calls `clean_verifier_state()` to mark dead registers uninitialized and poison dead stack halves, while preserving special stack slots such as dynptrs, iterators, and IRQ flags. It then scans the explored-state list for the instruction.

If it finds an in-progress state with remaining branches, it performs loop handling rather than normal pruning. Iterator `next` calls, `may_goto`, and callback calls use specialized equivalence checks to prove convergence without declaring valid iterator loops infinite. Otherwise, exact same-state loops with unchanged iterator depths, may-goto depth, and callback unroll depth are rejected as infinite loops. If the path is not pruned, heuristics may suppress adding another checkpoint inside tight loops.

If it finds a completed state, it compares old and current state. When old state has incomplete read marks because an SCC visit still has pending backedges, comparison is stricter (`RANGE_WITHIN`) and a copy of the current state is attached as a backedge. On a hit, precision from the old equivalent state is propagated into the current state and the function returns `1` to tell the verifier this path can stop. On misses, hit/miss counters drive eviction to `env->free_list`, where states are freed only when not referenced, branchless, and not needed for incomplete SCC read marks.

When no equivalent state is found and heuristics allow it, a new `bpf_verifier_state_list` is allocated, singular IDs are cleared, scalar precision may be reset for capable users, the current state is copied, SCC entry is recorded if the instruction is inside a strongly connected component, and the current state points back to the new checkpoint as parent.

## State and Persistence Behavior
State is entirely verifier-runtime memory. `env->explored_states` holds checkpoint states by instruction, `env->free_list` holds evicted but still possibly referenced states, and `env->scc_info` stores per-SCC/per-callchain visit records and backedges for one `do_check_common()` run. Parent links, branch counts, `hit_cnt`/`miss_cnt`, `num_backedges`, and `peak_states` drive memory lifecycle and accounting. No verifier state persists beyond the program verification attempt.

## Dependencies and Integration Points
The file depends on `linux/bpf_verifier.h` definitions for register, stack, reference, iterator, callback, and SCC metadata. It calls verifier helpers for liveness queries, stack-slot liveness, precision marking, state copy/free, jump history, explored-state lookup, logging, force checkpoints, callbacks, and instruction classification. It directly affects verifier behavior for loops, callbacks, open-coded iterators, resilient lock references, IRQ flags, dynptrs, packet/map pointers, arena pointers, and scalar precision.

## Risks and Test Signals
Incorrect pruning can accept unsafe programs or reject safe ones. Specific risks include broken scalar ID remapping, mishandled `BPF_ADD_CONST` relationships, stack half-slot cleanup destroying metadata needed by dynptr/iterator/IRQ logic, premature freeing of states still needed by SCC backedges, under-propagated precision/read marks in cyclic control flow, and false infinite-loop detection around iterators or async callbacks. Test signals include verifier selftests for scalar linked IDs, pointer range pruning, stack spill equivalence, uninitialized stack mode, dynptr and iterator stack slots, resilient lock reference matching, callback recursion/async callbacks, `may_goto`, bounded and unbounded loops, SCC precision propagation, and memory-accounting limits for non-capable users.
