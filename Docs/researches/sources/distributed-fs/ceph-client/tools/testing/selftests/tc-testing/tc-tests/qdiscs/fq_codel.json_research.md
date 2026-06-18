# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq_codel.json

Purpose: 15 FQ_CODEL tests for defaults, limit, memory limit, target, interval, quantum, ECN/noecn, CE threshold, drop batch, combined settings, replace/change/delete, class display, and trimming.

APIs and control flow: Uses `$TC qdisc add|replace|change|del|show`, `$TC class show`, `nsPlugin`, and `scapyPlugin`. Creation cases verify full default output; trimming queues packets then checks `limit 1p`.

State/dependencies: State is qdisc parameter state, flow table sizing, ECN/drop flags, and queued packets. Requires sch_fq_codel and scapy.

Risks/test signals: Regexes are long and default-value-sensitive. All 15 cases expect exit `0`; class display expects no class match.
