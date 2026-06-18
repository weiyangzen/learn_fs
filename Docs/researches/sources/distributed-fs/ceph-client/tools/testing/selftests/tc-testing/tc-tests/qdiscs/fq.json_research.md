# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fq.json

Purpose: 19 FQ tests for defaults, limits, flow limits, quantum, initial quantum, maxrate, pacing, refill delay, low-rate threshold, orphan mask, timer slack, CE threshold, horizon options, delete, replace/change, and trimming.

APIs and control flow: Uses `$TC qdisc add|del|replace|change|show`, `nsPlugin`, and `scapyPlugin`. Most cases install with one option; one invalid `initial_quantum` expects failure; trimming injects packets and lowers limit to one.

State/dependencies: State is root FQ scheduler configuration, pacing parameters, and queued packet state. Requires sch_fq and scapy.

Risks/test signals: Unit conversions and packet timing are sensitive. Eighteen cases expect exit `0`; invalid `initial_quantum 0x80000000` expects exit `2`.
