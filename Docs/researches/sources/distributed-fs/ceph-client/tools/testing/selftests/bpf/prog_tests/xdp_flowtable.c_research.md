# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_flowtable.c

## Purpose

Integration test for XDP interaction with nftables flowtable forwarding. It builds a routed namespace topology, configures nft flowtable offload, attaches an XDP program, sends UDP traffic, and checks BPF stats. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`nft` command availability, iproute2 namespace/veth/dummy setup, `bpf_program__attach_xdp()`, `bpf_map_lookup_elem()`, UDP `sendto()`, and `xdp_flowtable` skeleton stats map.

## Control Flow

The test skips if `nft` is missing, creates TX/RX namespaces and forwarding/dummy devices, configures forwarding and nft flowtable rules, attaches the XDP program to the forwarding interface, sends repeated UDP packets to a routed destination, then reads a stats map key to validate flowtable/XDP observation.

## State and Persistence Behavior

Temporary namespaces, nft table/flowtable/rules, veth/dummy devices, XDP link, and stats map entries. Cleanup deletes namespaces and destroys skeleton/link.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires nftables, flowtable support, namespace privileges, and UDP routing between the constructed devices.

## Risks and Edge Cases

Highly environment-sensitive: nft missing, flowtable unsupported, or route/neigh differences can skip/fail. Traffic timing uses short sleeps to give flowtable state time to update.

## Test Signals

Signals are successful nft setup, UDP send completion, XDP attach success, and nonzero/expected stats map values after traffic.
