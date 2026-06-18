# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_metadata.c

## Purpose

End-to-end XDP metadata and AF_XDP test. It verifies RX timestamp/hash/VLAN metadata, TX timestamp/checksum metadata, dev-bound XDP restrictions, AF_XDP UMEM metadata layout, and freplace attachment to a dev-bound program. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

AF_XDP APIs (`xsk_umem__create`, `xsk_socket__create`, ring reserve/submit/peek/release helpers), `bpf_xdp_attach()`, `bpf_map_update_elem()`, devmap/prog-array update checks, BPF program ifindex/flags setters, VLAN/veth namespace setup, UDP generation, `poll()`, and `xdp_metadata`/`xdp_metadata2` skeletons.

## Control Flow

The test creates TX/RX namespaces with a VLAN over veth, opens RX and TX AF_XDP sockets with metadata-enabled UMEM, loads dev-bound RX/redirect programs, verifies dev-bound programs cannot be inserted into prog arrays/devmaps, attaches RX XDP, sends an AF_XDP packet and validates TX/RX metadata, sends a normal UDP packet and validates RSS/VLAN metadata, then loads and attaches a freplace program targeting RX and sends another packet to prove invocation.

## State and Persistence Behavior

State includes namespaces, VLAN/veth devices, AF_XDP UMEM mappings/rings/sockets, XSK map entry, skeleton maps/BSS, dev-bound program fds, and freplace link state. Cleanup closes XSKs, destroys skeletons, closes namespace token, and deletes namespaces.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires AF_XDP, XDP metadata kfunc/support, VLAN, veth, dev-bound XDP, and freplace support.

## Risks and Edge Cases

Very environment-sensitive. Metadata availability depends on driver/veth support; ring index/address arithmetic must preserve metadata headroom; the retry loop for freplace has a likely inverted condition (`while (!retries--)`) that may not wait as intended.

## Test Signals

Expected metadata includes nonzero RX/TX timestamps, nonzero RX hash, L4 RSS type and VLAN id/proto for stack-generated packets, zero hash type and expected UDP checksum for AF_XDP-generated packets, rejected dev-bound program map insertions, and freplace `called > 0`.
