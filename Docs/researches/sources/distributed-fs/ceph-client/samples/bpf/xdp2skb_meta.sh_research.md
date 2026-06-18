<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta.sh

## Purpose
`xdp2skb_meta.sh` is a wrapper that attaches a pair of cooperating XDP and tc BPF programs used to transfer metadata from XDP `data_meta` to `skb->mark`.

## Important APIs, Types, And Functions
Shell helpers include `usage()`, `err()`, `info()`, `_call_cmd()`, `call_tc()`, `call_tc_allow_fail()`, `call_ip()`, `list_tc()`, `list_xdp()`, `flush_tc()`, `flush_xdp()`, `attach_tc_mark()`, and `attach_xdp_mark()`. It uses `getopt`, `tc`, and `ip`.

## Control Flow
The script parses `--dev`, `--flush`, `--list`, `--dry-run`, and verbosity flags, checks for `xdp2skb_meta_kern.o`, and requires a device. Flush mode removes tc and XDP programs. List mode displays current tc/XDP state. Default mode attaches `tc_mark` to ingress clsact and `xdp_mark` to the device.

## State And Persistence
State is kernel attachment state on the selected network device: tc clsact/filter and XDP link. No maps are managed by the script.

## Dependencies And Integration Points
It depends on iproute2, root privileges, the companion BPF object, XDP-capable device support, and tc clsact. It integrates two hook points that share metadata through packet metadata rather than maps.

## Risks And Edge Cases
The script deletes existing clsact qdisc and XDP programs on the device when attaching. Dry-run avoids changes but still requires argument parsing. Drivers without XDP metadata support cause the XDP program to abort packets.

## Test Signals
`--list` should show attached tc and XDP programs; packet tests with iptables marks should distinguish mark `42` when XDP metadata is present and `41` when absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta.sh -->
