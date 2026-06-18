# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/precise.c

## Purpose

This BPF verifier fixture defines targeted instruction-array tests for the verifier precision-marking machinery. The tests cover scalar precision propagation through map-value pointer subtraction, forced state checkpoints, cross-frame pruning, stack stores and spills, constant allocation sizes for ringbuf reserve, and a branch-pruning case that must reject an unbounded map-value offset.

## Important APIs, Types, and Functions

The file is declarative verifier-test data rather than standalone C logic. It uses BPF instruction macros such as `BPF_MOV64_IMM`, `BPF_LD_MAP_FD`, `BPF_EMIT_CALL`, `BPF_JMP_IMM`, `BPF_STX_MEM`, `BPF_LDX_MEM`, and raw helper calls for `bpf_get_prandom_u32`, `bpf_map_lookup_elem`, `bpf_probe_read_kernel`, `bpf_ringbuf_reserve`, and `bpf_ringbuf_submit`. Per-test metadata uses `.prog_type`, `.flags`, `.fixup_map_array_48b`, `.fixup_map_ringbuf`, `.result`, `.retval`, and `.errstr`.

## Control Flow

The harness includes this file into a larger verifier test table. Each entry provides a synthetic BPF program. Runtime flow is verifier-driven: the harness loads the program, applies map fixups, passes selected flags such as `BPF_F_TEST_STATE_FREQ`, and compares accept/reject plus verbose log substrings. The precision tests deliberately create branch points, helper calls, and stack accesses that force `mark_precise` to walk earlier verifier states.

## State and Persistence Behavior

No persistent state is owned by the file. State exists inside the verifier during one program load: register bounds, stack slots, parent states, and map/ringbuf fixups are allocated by the harness and discarded after the test case.

## Dependencies and Integration Points

It depends on the selftests verifier table format, BPF instruction macros, map-fixup support, verifier verbose-log matching, and kernel helper semantics. It integrates with BPF verifier regression testing for precision propagation and state-pruning safety.

## Risks and Test Signals

Risks include brittle verbose log substrings, architecture-specific unaligned-access handling, and false confidence if expected rejection strings are too broad. Strong signals are exact accept/reject outcomes, stable `mark_precise` log chains under checkpoint frequency, ringbuf allocation-size rejection, and rejecting the unbounded-min-value branch-pruning case.
