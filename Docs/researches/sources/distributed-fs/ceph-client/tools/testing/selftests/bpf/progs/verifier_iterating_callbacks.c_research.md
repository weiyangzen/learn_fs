# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_iterating_callbacks.c

## Purpose

`verifier_iterating_callbacks.c` is a large regression suite for verifier reasoning across iterating callbacks and bounded loop constructs. It covers `bpf_loop`, `bpf_for_each_map_elem`, `bpf_user_ringbuf_drain`, `bpf_find_vma`, numeric open-coded iterators, `may_goto`, loop detection, widening, state pruning, and constant-addition range propagation.

## Important APIs, Types, and Functions

The file includes `bpf_misc.h` and `bpf_experimental.h`. It declares small maps, a ringbuf, and several `.data` arrays. Helpers and kfunc-like iterator APIs include `bpf_loop`, `bpf_for_each_map_elem`, `bpf_user_ringbuf_drain`, `bpf_find_vma`, `bpf_get_current_task_btf`, `bpf_probe_read_user`, `bpf_iter_num_new`, `bpf_iter_num_next`, and `bpf_iter_num_destroy`. Some tests use `BPF_F_TEST_STATE_FREQ` to stress state exploration.

## Control Flow

Callback tests deliberately make memory safe on the first iteration but unsafe on later iterations, unsafe at zero iterations, or widening-sensitive. Other tests verify loop detection through helper callbacks and `may_goto`. Numeric iterator tests create nested iteration limits, validate successful bounded summations, and exercise known corner cases. Later programs check that adding constants to map-value pointers through several registers remains bounded or is rejected when range proofs are insufficient.

## State and Persistence Behavior

Persistent state is map/ringbuf/global data. Verifier state includes callback entry snapshots, iteration count bounds, loop convergence, map-value ranges across repeated callback invocations, iterator lifetime state, and register equivalence after constant additions.

## Dependencies and Integration Points

The file integrates with helper callback verification, open-coded iterator support, ringbuf callbacks, VMA callbacks, may-goto instruction support, and state-pruning heuristics. It is sensitive to verifier complexity limits and state-frequency test flags.

## Risks and Test Signals

Risks include accepting programs safe only on the first callback iteration, false infinite-loop detection, iterator lifetime leaks, or imprecise range widening that hides out-of-bounds map access. Test signals include expected failures for invalid map-value access and infinite loops, plus successful bounded iterator and may-goto cases with declared return values.
