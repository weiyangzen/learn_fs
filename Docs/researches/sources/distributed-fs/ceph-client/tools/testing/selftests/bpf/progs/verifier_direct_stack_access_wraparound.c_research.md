# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_stack_access_wraparound.c

## Purpose

`verifier_direct_stack_access_wraparound.c` tests stack pointer arithmetic near 32-bit wraparound boundaries. It ensures the verifier rejects frame-pointer offsets that would overflow or escape the valid BPF stack range even when arithmetic appears to wrap.

## Important APIs, Types, and Functions

The file has three `SEC("socket")` naked assembly programs. All use frame-pointer arithmetic with large positive constants such as `2147483647` and `1073741823`. Metadata expects verifier diagnostics about frame-pointer arithmetic and stack pointer range violations.

## Control Flow

Each test moves `r10` into a general register, adds or subtracts large constants, and attempts a direct stack access. The variants isolate immediate wraparound, intermediate offset tracking, and final out-of-range access.

## State and Persistence Behavior

There are no maps or external state. The relevant state is verifier stack pointer offset arithmetic, including signed and unsigned overflow avoidance. The frame pointer must remain bounded to the fixed 512-byte BPF stack.

## Dependencies and Integration Points

This file integrates with verifier pointer arithmetic checks and stack access validation. It is a regression guard against integer overflow in verifier offset calculations.

## Risks and Test Signals

Risks are arithmetic overflow allowing invalid stack access or overly broad rejection of legitimate small offsets. Test signals are three failures with diagnostics mentioning impossible frame-pointer arithmetic, large offsets, or stack pointer arithmetic out of range.
