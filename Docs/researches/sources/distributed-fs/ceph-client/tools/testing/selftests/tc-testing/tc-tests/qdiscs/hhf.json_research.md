# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hhf.json

Purpose: 10 HHF tests for defaults, limit, quantum, reset timeout, admit bytes, evict timeout, non-heavy-hitter weight, change, class display, and trimming.

APIs and control flow: Uses `$TC qdisc add|change|show`, `$TC class show`, `nsPlugin`, and `scapyPlugin`. Creation cases verify option/default output; trimming injects packets and lowers limit to one.

State/dependencies: State is HHF scheduler configuration, heavy-hitter tracking parameters, and queued packets. Requires sch_hhf and scapy.

Risks/test signals: Regexes depend on HHF defaults and unit rendering. All 10 cases expect exit `0`; class display expects zero class matches and trimming expects `limit 1p`.
