# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_subprog_precision.c

## Purpose
`verifier_subprog_precision.c` is a comprehensive precision-backtracking test suite for BPF subprograms, callbacks, stack slots, global functions, and tail calls. It verifies where precision marks originate and how they propagate between callers, callees, callbacks, and spilled data.

## Important APIs, Types, and Functions
The file defines `vals[] SEC(".data.vals")` and a prog-array `map_array`. It uses many static subprograms, including `identity_subprog`, `callback_subprog`, frame-pointer leaking subprograms, `loop_callback_bad`, `subprog_with_precise_arg`, `subprog_spill_reg_precise`, and `identity_tail_call`. Helpers include `bpf_loop` and `bpf_tail_call`. Expected verifier logs heavily use `mark_precise` traces.

## Control Flow
The tests usually set a bounded or unknown index, call a subprogram or callback, multiply by element size, and add it to a map-value pointer. Some tests intentionally leak frame-pointer-derived scalars through subprograms to verify precision remains conservative. `bpf_loop` tests verify callback return range enforcement and the rule that loop callback parameters such as `r1` and `r4` become precise only to the helper call boundary. Later tests spill precise values, mutate stack/map slots, and verify precision propagation through tail-call failure paths.

## State and Persistence
Persistent state is limited to `.data.vals` and the prog array. The main state is verifier precision metadata across frames and stack slots. Stack slots can carry precise scalar requirements, and map-value pointers carry bounds that make precision failures visible as invalid pointer arithmetic.

## Dependencies and Integration Points
The source depends on verifier subprogram call graph analysis, callback modeling for `bpf_loop`, stack precision tracking, map-value bounds, and tail-call helper semantics. It integrates through raw tracepoint-like optional sections `SEC("?raw_tp")`, verbose log matching, and failure messages such as callback return range violations and `math between map_value pointer and register with unbounded min value`.

## Risks and Test Signals
Risks include either under-propagating precision, which can accept unsafe map-value access, or over-propagating precision, which can cause verifier complexity and false rejections. Test signals include detailed `mark_precise` paths across frame numbers, expected `bpf_loop` callback rejection when `R0` returns outside `[0, 1]`, success cases with bounded indices, and a tail-call failure case proving unbounded precision is still rejected.
