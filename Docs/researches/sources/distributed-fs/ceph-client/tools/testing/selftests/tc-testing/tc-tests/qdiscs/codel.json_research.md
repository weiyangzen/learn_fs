# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/codel.json

Purpose: 10 CODEL qdisc tests for default creation, limit, target, interval, ECN, CE threshold, delete, replace/change, and queue-limit trimming.

APIs and control flow: Uses `$TC qdisc add|del|replace|change|show`, `nsPlugin`, and `scapyPlugin` for trimming. The scapy case injects ten TCP packets, changes limit to one, and verifies `limit 1p`.

State/dependencies: State is root CODEL configuration and queued packet state. Requires sch_codel, namespace devices, and scapy.

Risks/test signals: Packet timing and output unit formatting can affect results. All cases expect exit `0`.
