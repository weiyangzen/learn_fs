# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_scalar_ids.c

## Purpose
`verifier_scalar_ids.c` is a focused BPF verifier precision and state-equivalence test suite for scalar IDs. It checks when copied scalar registers share IDs, how range information and precision marks propagate across linked scalar values, how stack-spilled scalar IDs are tracked, and how verifier state pruning compares scalar IDs safely.

## Important APIs, Types, and Functions
The file uses raw socket-section BPF programs, mostly `__naked` inline assembly, with expected verifier log fragments captured by `__msg`. Helper calls to `bpf_ktime_get_ns` and `bpf_get_prandom_u32` create unknown scalars and unpredictable branches. Static subprograms such as `precision_many_frames__foo`, `precision_many_frames__bar`, and `precision_stack__foo` create multi-frame call graphs for precision backtracking. Macros from `bpf_misc.h` provide `__log_level(2)`, `BPF_F_TEST_STATE_FREQ`, `BPF_F_TEST_RND_HI32`, `__xlated`, and success/failure annotations.

## Control Flow
The tests copy helper-returned scalars among registers, perform conditional jumps that propagate bounds, then force precision by using a scalar as a pointer offset from `r10`. Multi-frame tests pass linked IDs through subprogram calls and stack slots, then force precision in callees to verify backtracking into caller frames. Other cases intentionally break ID links, create too many linked registers, test conditional jumps that should not trigger linked precision propagation, and check whether cached verifier states compare unique and nil IDs correctly.

## State and Persistence
No persistent runtime state is stored outside verifier state. The meaningful state is abstract verifier metadata: scalar ID, range bounds, subregister definition, stack slot ID, parent-state chain, and liveness. Stack writes and reads are deliberately used as verifier state carriers.

## Dependencies and Integration Points
The file depends on the verifier's scalar ID implementation, precision backtracking, state pruning, and subregister zero-extension tracking. It integrates with the BPF selftest harness via verifier log matching and translated-instruction expectations. Architecture-sensitive subregister behavior is guarded through `__xlated` expectations.

## Risks and Test Signals
Regression risks include unsound pruning of states with incompatible scalar IDs, lost precision across calls or stack spills, false propagation after broken links, and loss of `subreg_def` metadata under range propagation. Test signals include expected `mark_precise` log paths, deliberate failures such as `div by zero` and `register with unbounded min value`, processed-instruction counts showing pruning behavior, and `BPF_F_TEST_RND_HI32` checks that upper-half randomization is not inserted incorrectly.
