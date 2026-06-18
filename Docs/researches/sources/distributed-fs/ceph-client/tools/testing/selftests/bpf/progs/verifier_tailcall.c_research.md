# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_tailcall.c

## Purpose
`verifier_tailcall.c` is a narrow negative verifier test for `bpf_tail_call`. It confirms that the helper rejects non-prog-array maps.

## Important APIs, Types, and Functions
The file declares a regular `BPF_MAP_TYPE_ARRAY` named `map_array`, then a single `SEC("socket")` naked test program `invalid_map_for_tail_call`. The program loads `map_array` into `r2`, sets key register `r3` to zero, calls `bpf_tail_call`, and exits.

## Control Flow
Control flow is straight-line and intentionally invalid at helper-check time. There is no fallback return value because the verifier should reject the program before runtime execution.

## State and Persistence
The only persistent state is the array map declaration. No map contents are needed. The state under test is verifier helper argument type checking for `ARG_CONST_MAP_PTR` pointing to a prog-array map.

## Dependencies and Integration Points
The source depends on `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `bpf_misc.h`, and the selftest runner's expected failure matching. It integrates with socket program verification and helper prototype validation.

## Risks and Test Signals
The risk is accepting a non-prog-array map as a tail-call map, which would be unsafe helper dispatch behavior. The test signal is the exact failure `expected prog array map for tail call`, with unprivileged failure also expected.
