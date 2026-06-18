<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp.c

## Purpose
This small verifier file checks basic XDP context access and use of `bpf_xdp_store_bytes` with data sourced from a read-only map.

## Important APIs, Types, and Functions
It declares `map_array_ro`, an array map with `BPF_F_RDONLY_PROG`, and uses `bpf_map_lookup_elem` and `bpf_xdp_store_bytes`. Programs read `struct xdp_md` fields including `ingress_ifindex`.

## Control Flow
`xdp_using_ifindex_from_netdev` reads `xdp_md.ingress_ifindex` and returns 1 if it is positive. `xdp_store_bytes_from_ro_map` looks up key 0 in the read-only map and, if present, writes 8 bytes from that map value into the packet at offset 0 using the XDP store helper.

## State and Persistence
The map stores the source bytes for `bpf_xdp_store_bytes`, but the programs do not update persistent state. Packet mutation through the helper is the runtime effect.

## Dependencies and Integration Points
The file is loaded by verifier tests for the XDP program type and depends on helper support for `bpf_xdp_store_bytes`.

## Risks
Helper availability and read-only map semantics are kernel-version dependent. Packet store bounds are enforced by the helper rather than explicit packet pointer checks.

## Test Signals
Both programs are annotated successful, with return values 1 and 0 respectively. Successful load validates ifindex field access and read-only map value use as helper input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_xdp.c -->
