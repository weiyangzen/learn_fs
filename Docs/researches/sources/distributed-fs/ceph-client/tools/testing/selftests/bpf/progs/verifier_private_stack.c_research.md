# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_private_stack.c

## Purpose
This file tests private-stack JIT/verifier behavior on supported architectures, including single programs, nested calls, callbacks, exceptions, and async timer callbacks. It includes a fallback dummy test where private stack is unsupported.

## Important APIs, Types, And Functions
It includes `vmlinux.h`, `bpf_experimental.h`, defines `MAX_BPF_STACK`, `struct elem` with `bpf_timer`, and an array map. It uses `bpf_get_smp_processor_id`, `bpf_throw`, `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, and `bpf_timer_start`. It also uses `__jited` annotations for x86_64 and arm64 expected code patterns.

## Control Flow
Tests write deep stack slots to trigger private stack allocation, call subprograms that make cumulative stack depth exceed `MAX_BPF_STACK`, run callbacks through `bpf_loop`, throw exceptions in main or subprograms, and set timer callbacks that may or may not be nested.

## State And Persistence
The array map and timer objects are runtime fixtures, but the key state is verifier/JIT stack-depth accounting, private-stack eligibility, callback nesting, and exception unwind handling.

## Dependencies And Integration Points
It integrates with architecture-specific JIT output checks, private-stack support, timer kfunc/helper semantics, and experimental exception support.

## Risks
Incorrect private-stack selection can corrupt per-CPU stack storage or generate wrong unwind code. Async callbacks are especially sensitive because potential nesting changes stack safety.

## Test Signals
Signals include `__success`, expected JIT instruction regexes, return values for fentry tests, and fallback dummy success on unsupported architectures.
