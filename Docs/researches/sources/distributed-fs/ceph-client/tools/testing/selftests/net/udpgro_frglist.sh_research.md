# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro_frglist.sh

Purpose: UDP GRO fraglist benchmark/test variant that enables `rx-gro-list` and uses BPF NAT helpers to exercise IPv6-to-IPv4 transformed traffic through GRO fraglist paths.

Important APIs/functions: resembles `udpgro_bench.sh` but additionally enables `ethtool -K veth1 rx-gro-list on`, attaches `lib/xdp_dummy.bpf.o`, installs clsact qdisc and `nat6to4.bpf.o` ingress/egress tc BPF filters, and runs receivers/transmitters with verbose IPv4 receive arguments after IPv6 transmission.

Control flow: validates both BPF objects exist, then no-arg `run_all()` builds IPv6 sender arguments and executes TCP and UDP benchmark cases through `in_netns.sh`. `run_one()` creates namespace/veth topology, attaches XDP and tc filters, starts receiver, waits for port readiness, and runs TX.

State and persistence: temporary namespace, veth, XDP, tc qdisc/filter state, and background jobs. Cleaned by trap. No files are persisted.

Dependencies and integration: requires built `lib/xdp_dummy.bpf.o` and `nat6to4.bpf.o`, tc BPF direct-action support, ethtool rx-gro-list support, compiled benchmark helpers, and root.

Risks: contains debug `echo ${rx_args}`/`echo ${args}` output and spacing quirks, so output is less polished than pure kselftest TAP. Functional result depends on BPF helper behavior and kernel fraglist offload support.

Test signals: command exit status and benchmark/helper output. Missing BPF artifacts produce immediate failure with "Run make first".
