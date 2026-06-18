<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp_direct_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp_direct_packet_access.c

## Purpose
This large generated-style verifier suite validates direct XDP packet and metadata access bounds reasoning. It covers data/data_end and data_meta/data comparisons using all common relational operators, corner-case offsets, and intentionally good and bad loads.

## Important APIs, Types, and Functions
All tests are naked `SEC("xdp")` programs using inline assembly. They read `xdp_md.data`, `xdp_md.data_end`, and `xdp_md.data_meta` via `offsetof` immediates and then perform packet loads. `BPF_F_ANY_ALIGNMENT` appears because access alignment is not the focus.

## Control Flow
Each program loads a base pointer and bound pointer, adjusts the base by 6, 7, 8, or 9 bytes, branches with `>`, `<`, `>=`, `<=`, or reversed comparisons, and then performs a load from `base - N`. Good cases prove the accessed byte range is within `[data, data_end)` or `[data_meta, data)`. Bad cases either load too wide for the proven range or perform the load on an unproven branch. The first cases also reject arithmetic on `pkt_end` itself.

## State and Persistence
There is no persistent state. The verifier state under test is packet pointer range, fixed offset, known safe byte window, and separate tracking of packet data versus metadata regions.

## Dependencies and Integration Points
The file is part of the BPF verifier selftest corpus. It relies on exact `__success`/`__failure` annotations and expected messages such as pointer arithmetic on `pkt_end`, offset outside packet, or min/max outside allowed range.

## Risks
Any verifier range-analysis precision improvement or diagnostic rewrite may alter expected results. Because the suite uses many near-duplicate cases, accidental edits can create inconsistent coverage.

## Test Signals
The key signals are that exact corner cases at the proven boundary succeed, one-byte-short ranges fail, loads outside the checked branch fail, and pointer arithmetic on `data_end` is rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp_direct_packet_access.c -->
