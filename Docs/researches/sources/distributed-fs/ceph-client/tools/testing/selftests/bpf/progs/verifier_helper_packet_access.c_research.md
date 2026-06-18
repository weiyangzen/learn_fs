# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_packet_access.c

## Purpose

`verifier_helper_packet_access.c` tests helper-mediated packet access. It ensures helpers that read or write packet memory receive packet pointers with proven ranges, rejects unchecked or undersized ranges, and verifies helper allowlist behavior for XDP and tc packet contexts.

## Important APIs, Types, and Functions

The file defines `map_hash_8b` for selected helper cases and 21 programs across `SEC("xdp")` and `SEC("tc")`. Inline assembly passes packet pointers, packet_end, stack pointers, and sizes to helper calls. Expected diagnostics include `invalid access to packet`, `helper access to the packet`, negative minimum values, and `R1 type=pkt_end expected=fp`.

## Control Flow

XDP tests start with packet data/data_end and try valid, unchecked, variable, bad-range, and too-short packet helper accesses. TC tests repeat the matrix and add unsuitable-helper checks, helper-ok subprogram calls, helper-fail subprogram calls, range-zero handling, packet_end used as a wrong input pointer, and incorrect register placement.

## State and Persistence Behavior

Persistent state is only the hash map. Runtime packet state is transient. The verifier tracks packet pointer ids, checked ranges, pointer base type, minimum size, helper read/write capability, and subprogram transfer of packet proof state.

## Dependencies and Integration Points

The file integrates with XDP and tc verifier packet-access logic plus helper prototypes that accept packet memory. It complements direct packet access tests by validating the same safety properties at helper call boundaries.

## Risks and Test Signals

Risks include helpers reading past packet_end, accepting packet_end as a data pointer, losing packet range proof in subprograms, or rejecting valid bounded helper access. Test signals are success for valid ranges and exact failures for unchecked packets, bad ranges, unsuitable helpers, negative sizes, and wrong pointer base types.
