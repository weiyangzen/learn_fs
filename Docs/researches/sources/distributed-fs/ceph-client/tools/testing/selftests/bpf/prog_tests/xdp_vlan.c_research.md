# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_vlan.c

## Purpose

Network namespace selftest for XDP VLAN tag change/removal behavior with a TC companion program. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_vlan` skeleton, `bpf_xdp_attach()`, TC attach helpers through network commands, namespace/veth setup, `ping`, VLAN id/proto constants, and XDP attach flags.

## Control Flow

Setup creates two namespaces connected by veth, assigns IP addresses, and brings links up. `xdp_vlan()` attaches XDP and TC programs, sends traffic, and validates either VLAN change or removal behavior. Exported tests run change and remove variants.

## State and Persistence Behavior

Temporary namespaces, veth, XDP/TC attachments, and skeleton state. Cleanup deletes namespaces.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires namespace, veth, VLAN handling, XDP, TC, and ping.

## Risks and Edge Cases

Traffic and VLAN behavior depend on correct namespace cleanup and no interface-name collisions. Offload or kernel VLAN parsing changes can affect expectations.

## Test Signals

Successful ping/traffic with expected XDP VLAN transformation, and no assertion failures in change/remove subtests.
