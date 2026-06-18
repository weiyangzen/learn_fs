<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_cls_bpf.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/test_cls_bpf.sh

## Purpose
`test_cls_bpf.sh` is a simple tc classifier smoke test for sample packet parsers. It attaches three BPF parser objects to a veth ingress hook and uses pktgen to confirm packets are filtered/dropped.

## Important APIs, Types, And Functions
Shell functions are `pktgen()` and `test()`. It uses `ip link`, `tc qdisc`, `tc filter`, `tc -s`, `awk`, and `../pktgen/pktgen_bench_xmit_mode_netif_receive.sh`.

## Control Flow
The script creates a veth pair, brings both ends up, attaches each object/section pair (`parse_simple.o:simple`, `parse_varlen.o:varlen`, `parse_ldabs.o:ldabs`) to ingress clsact, runs pktgen, inspects qdisc drop counters, deletes clsact, and finally deletes the veth.

## State And Persistence
State is temporary network device and qdisc state. No BPF map data is persisted.

## Dependencies And Integration Points
It depends on root privileges, pktgen sample scripts, tc clsact, parser object files built beforehand, and a kernel with cls_bpf support.

## Risks And Edge Cases
No trap is installed, so failures can leave the veth or qdisc behind. The drop counter parsing relies on `tc -s` output layout. It assumes generated traffic reaches the ingress path of the test veth.

## Test Signals
For each parser, attach should print `ok`, pktgen should run, and qdisc drop counters should be nonzero. A zero drop count prints `FAIL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_cls_bpf.sh -->
