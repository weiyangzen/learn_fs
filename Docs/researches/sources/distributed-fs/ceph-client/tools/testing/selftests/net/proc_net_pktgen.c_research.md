<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/proc_net_pktgen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/proc_net_pktgen.c

## Purpose

`proc_net_pktgen.c` is a kselftest harness for the `/proc/net/pktgen` control ABI. It validates accepted and rejected write commands against the global controller, per-thread control file, and per-device pktgen file, focusing on parser behavior, command length handling, accepted aliases, and expected errno values.

## Important APIs, Types, and Functions

The file uses `kselftest_harness.h` fixtures. `FIXTURE_SETUP(proc_net_pktgen)` loads `pktgen`, opens `/proc/net/pktgen/pgctrl` and `/proc/net/pktgen/kpktgend_0`, writes `add_device lo@0`, then opens `/proc/net/pktgen/lo@0`. `FIXTURE_TEARDOWN` closes files and writes `rem_device_all`. Test cases write command strings such as `start`, `stop`, `reset`, `max_before_softirq`, packet-size commands, IMIX weights, debug, rate/ratep, UDP port ranges, clone/count/burst/node, xmit mode, flags, IPv4/IPv6 destination/source, MAC addresses, MPLS stacks, VLAN/SVLAN fields, TOS, traffic class, and skb priority.

## Control Flow

Each test writes one or more strings to the opened proc file and checks the return length or `-1` with a specific errno. The setup runs before every fixture test, so parser state starts with a fresh `lo@0` pktgen device. Negative tests iterate all prefix lengths of invalid command strings to verify incomplete and unknown commands fail. Positive tests check that both NUL-terminated and non-NUL command strings are accepted where intended.

## State and Persistence Behavior

State exists in the kernel pktgen module and procfs files. Each fixture registers `lo@0` and removes all devices in teardown, so test state should not persist beyond a case. Commands mutate pktgen device configuration, counters, and per-thread state but do not start durable packet generation beyond tested `start`/`stop` control writes.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are `CONFIG_NET_PKTGEN` or a loadable `pktgen` module, `/proc/net/pktgen`, loopback registration, and optional XFRM/MPLS/VLAN parser support reflected by errno expectations. It integrates with the pktgen procfs ABI and command parser. Risks are exact errno drift (`EINVAL`, `E2BIG`, `EOPNOTSUPP`), module auto-load availability, pktgen command syntax changes, and fixture setup failing if `lo@0` is already registered by another process. Test signals are successful fixture setup/teardown and exact write lengths or errno for every command family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/proc_net_pktgen.c -->
