# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_direct_packet_access.c

## Purpose

`verifier_direct_packet_access.c` is an extensive verifier suite for direct packet access. It checks data/data_end arithmetic, range proofs, packet writes, pruning, alignment, pointer spilling, pointer arithmetic restrictions, subprogram propagation, and error reporting for tc and socket program types.

## Important APIs, Types, and Functions

The file includes Ethernet constants, BPF helpers, and `bpf_misc.h`. It defines 34 programs, mostly `SEC("tc")`, plus one socket program. They use inline assembly to read `__sk_buff` packet metadata offsets, compare packet pointers to data_end, and perform byte/word/dword/qword packet accesses. Expected messages cover invalid context access, invalid packet access, scalar memory access, packet-end arithmetic, and misaligned packet access.

## Control Flow

The early tests establish core rules: `pkt_end - pkt_start` is accepted, accesses after sufficient bounds checks pass, and unchecked or too-wide accesses fail. Middle tests combine comparisons, shifts, AND masks, branch joins, zero additions, xadd/spill interactions, and arithmetic on data_end. Later tests exercise packet pointer marking on good and bad accesses, subprogram handoff of packet/data_end registers, and access ranges near packet boundaries.

## State and Persistence Behavior

No persistent maps are declared. Runtime packet bytes are transient. The verifier state under test includes packet pointer id, fixed and variable offsets, proven range `r`, alignment, stack spills retaining pointer type, and branch-pruned state equivalence.

## Dependencies and Integration Points

The file integrates with tc classifier program loading, direct packet access verifier logic, and subprogram verifier state propagation. It is important for networking because accepted tc programs can read and write packet data directly without helper calls.

## Risks and Test Signals

Risks are accepting out-of-bounds packet reads/writes, rejecting safe access after complex but valid range checks, or losing pointer identity through spills and subprogram calls. Test signals include successful load for well-bounded variants and exact failures for invalid access to packet, bad ctx offset, pkt_end arithmetic, scalar memory access, and misalignment.
