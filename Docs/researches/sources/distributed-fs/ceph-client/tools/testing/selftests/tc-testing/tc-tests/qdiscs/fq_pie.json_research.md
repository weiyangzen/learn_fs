# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_pie.json

Purpose: 2 FQ_PIE tests: create with `flows 65536` and trim queued packets by changing limit to one.

APIs and control flow: Uses `$TC qdisc add|change|show`, `nsPlugin`, and `scapyPlugin`. The trim case injects ten TCP packets, changes `limit 1`, and verifies output.

State/dependencies: State is root FQ_PIE configuration and queued packet state. Requires sch_fq_pie and scapy.

Risks/test signals: The first test name says invalid flow count but expects success and output with `flows 65536`; this likely captures compatibility behavior. Both tests expect exit `0`.
