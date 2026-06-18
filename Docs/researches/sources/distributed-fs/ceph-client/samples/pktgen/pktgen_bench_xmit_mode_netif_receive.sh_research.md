# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_netif_receive.sh

Purpose: pktgen benchmark script for injecting generated packets into the receive path with `xmit_mode netif_receive`, useful for ingress qdisc path benchmarking.

Important APIs/functions: sources `functions.sh` and `parameters.sh`; uses `pg_ctrl reset/start`, `pg_thread rem_device_all/add_device`, `pg_set` for queue mapping, count, packet size, delay, destination, UDP destination range, `xmit_mode netif_receive`, and burst.

Control flow: runs as root, sets defaults for destination, MAC, burst, and count, validates addresses/ports, resets pktgen, configures one pktgen device per requested thread, starts pktgen, and prints result snippets for each device.

State and persistence: modifies pktgen procfs state and resets it through trap/explicit reset.

Dependencies and integration: pktgen kernel module, Bash, root/sudo, interface name, and optional qdisc setup described in comments.

Risks: default invalid MAC intentionally drops packets in RX path; using real destinations can inject traffic. Burst defaults to 1024 and can create heavy CPU load.

Test signals: configure ingress qdisc scenarios, run with `-i <dev>`, compare result throughput and qdisc behavior across scenarios.
