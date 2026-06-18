# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/config

## Purpose
Lists kernel networking configuration needed for tc-testing coverage.

## Important APIs, Types, And Functions
Requests dummy/veth devices, netfilter and conntrack pieces, nft/nat/flow table modules, a broad set of qdiscs, classifiers, ematches, tc actions (`gact`, `bpf`, `connmark`, `ctinfo`, `ife`, `ct`, `gate`, and more), and supporting test devices such as `NETDEVSIM` and mock PTP.

## Control Flow
No runtime control flow. The config is consumed by kselftest config tooling and by humans preparing a kernel for tc-testing.

## State And Persistence
No state.

## Dependencies And Integration Points
Directly supports the JSON action suites in `tc-tests/actions`, namespace setup in `nsPlugin.py`, and scapy packet tests requiring veth/dummy devices.

## Risks
This file is broad but individual tests may still require userspace dependencies such as `ip`, `tc`, `pyroute2`, `scapy`, BPF tooling, or root privileges. Missing module autoload can cause test failures even when options are set to `m`.

## Test Signals
A prepared kernel has the requested qdisc/classifier/action modules available and can create veth/dummy devices and conntrack state in a namespace.
