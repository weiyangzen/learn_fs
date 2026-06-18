# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_qdisc.c

## Purpose
This selftest validates BPF qdisc struct_ops attachment and behavior for FIFO and FQ qdiscs, attachment constraints under classful/multiqueue qdiscs, incomplete operation rejection, and default-qdisc integration.

## Important APIs, Types, And Functions
Core helpers are `do_test()`, `test_fifo()`, `test_fq()`, `test_qdisc_attach_to_mq()`, `test_qdisc_attach_to_non_root()`, `test_incompl_ops()`, `get_default_qdisc()`, `test_default_qdisc_attach_to_mq()`, `test_ns_bpf_qdisc()`, and `serial_test_bpf_qdisc_default()`. It uses `bpf_tc_hook_create()`, `bpf_tc_hook_destroy()`, `bpf_map__attach_struct_ops()`, selftest network helpers, `tc`/`ip` shell commands, and `/proc/sys/net/core/default_qdisc`.

## Control Flow
FIFO and FQ tests load and attach their qdisc skeletons, create a BPF TC qdisc hook on loopback root, transfer 10 MiB over a TCP connection, and destroy the hook. Multiqueue tests attach `bpf_fifo`, create veth devices, add `mq`, and attach BPF qdisc to a child queue. Non-root attachment creates HTB on loopback and asserts BPF qdisc attachment below a class fails. The default-qdisc test temporarily writes `bpf_fifo` to the sysctl, creates a netns and veth, adds `mq`, and checks the BPF qdisc init callback ran.

## State And Persistence Behavior
State includes temporary qdiscs on loopback or veth devices, temporary veth devices, struct_ops links, a private netns object, TCP sockets, and a temporary sysctl override. Cleanup removes qdiscs, frees netns, restores the saved default qdisc, and destroys skeletons.

## Dependencies And Integration Points
It depends on `tc`, `ip`, rtnetlink/qdisc support, loopback ifindex 1, veth support, network helper utilities, BPF TC hook APIs, and BPF qdisc skeletons. It integrates BPF struct_ops qdiscs with normal Linux traffic-control configuration.

## Risks And Edge Cases
The test mutates network configuration and `/proc/sys/net/core/default_qdisc`, so cleanup and namespace isolation are important. Fixed interface names and loopback ifindex assumptions can collide with external state. Missing privileges or qdisc support will fail setup.

## Test Signals
Passing signals include successful traffic through `bpf_fifo` and `bpf_fq`, success attaching to an `mq` child, failure attaching to a non-root HTB class, failure attaching incomplete qdisc ops, and `init_called == true` when `bpf_fifo` is selected as the default qdisc under `mq`.
