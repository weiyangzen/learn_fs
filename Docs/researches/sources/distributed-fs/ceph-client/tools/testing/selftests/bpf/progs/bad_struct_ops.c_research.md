# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bad_struct_ops.c

## Purpose

Negative/edge struct_ops object defining callbacks for two different test module ops structures, used to validate struct_ops attachment/type checking. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`SEC("struct_ops/test_1")`, `SEC("struct_ops/test_2")`, `BPF_PROG()` callbacks, `.struct_ops.link` maps `testmod_1` and `testmod_2`, and test module headers.

## Control Flow

Two callbacks return 0. The object declares two struct_ops link instances referencing those callbacks, intentionally mixing different ops structures for loader/verifier validation.

## State and Persistence Behavior

Struct_ops link map definitions are the relevant state; there is no runtime mutable state.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on the BPF test module's struct_ops BTF types.

## Risks and Edge Cases

Availability of `bpf_testmod` and exact struct_ops type definitions controls load behavior. The file is intentionally named bad, so success/failure expectations live in the harness.

## Test Signals

Expected loader/verifier behavior for invalid or mixed struct_ops link definitions.
