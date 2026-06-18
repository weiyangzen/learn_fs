# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_bench_xmit_mode_queue_xmit.sh

Purpose: pktgen benchmark script for egress qdisc path measurement using `xmit_mode queue_xmit`.

Important APIs/functions: sources shared helpers, rejects `BURST`, configures pktgen threads/devices, sets queue CPU mapping, packet count/size/delay/destination, optional UDP destination range, and `xmit_mode queue_xmit`.

Control flow: runs as root, parses parameters, sets defaults, validates address/ports, resets pktgen, configures each thread device, starts run, and prints result snippets.

State and persistence: modifies `/proc/net/pktgen`; reset occurs before configuration and via sourced trap behavior.

Dependencies and integration: pktgen, egress qdisc stack, root privileges, and selected network device.

Risks: can generate heavy traffic through egress path. Burst is explicitly unsupported because queue_xmit mode rejects burst greater than one.

Test signals: run against a test interface with egress qdisc configurations and compare pktgen result output.
