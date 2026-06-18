# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xfrm_info.c

## Purpose

Integration test for BPF TC helpers that set and get XFRM interface metadata. It builds a three-namespace IPsec/XFRM topology and verifies ping responses use the requested if_id. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

TC hook attach APIs, iproute2 XFRM state/policy commands, raw NETLINK_ROUTE message construction for external xfrm interface creation, namespace helpers, `ping`, and `xfrm_info` skeleton BSS fields `req_if_id`/`resp_if_id`.

## Control Flow

The test deletes stale namespaces, creates underlay veth networks, configures XFRM states/policies and ipsec0 interfaces, creates an external-mode xfrm device through netlink, loads TC ingress/egress BPF programs on NS0 ipsec0, then pings two overlay destinations by setting different requested if_ids and checking the response if_id recorded by ingress BPF.

## State and Persistence Behavior

Temporary namespaces, veths, XFRM state/policy database entries, ipsec0 devices, TC hooks, and skeleton BSS if_id state. Cleanup deletes all namespaces.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires XFRM/IPsec support, route netlink, iproute2 xfrm commands, TC, ping, and namespace privileges.

## Risks and Edge Cases

XFRM command syntax and external-device support vary by kernel/iproute2. The raw netlink request uses a fixed-size buffer. Cleanup is essential because XFRM state lives in namespaces.

## Test Signals

Successful underlay/overlay setup, TC attach success, ping success to each destination, and `resp_if_id` exactly matching `IF_ID_0_TO_1` and `IF_ID_0_TO_2`.
