# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/qdiscs.json

Purpose: 41 qdisc infrastructure/regression tests for class delete notifications, backlog/qlen accounting, reentrant enqueue/dequeue, invalid child attachment, and underflow/use-after-free/divide-by-zero regressions across DRR, ETS, HFSC, HTB, TBF, QFQ, CAKE, RED, SFB, CBS, dualpi2, fq/fq_codel/fq_pie, PIE, CODEL, HHF, SKBPRIO, ingress, clsact, blackhole, and netem.

APIs and control flow: Uses `$TC qdisc|class|filter`, `$IP link|addr`, `ping`, scapy packet injection, text regexes, and `matchJSON` checks for structured stats. Setups build multi-level qdisc/class trees, enqueue traffic, mutate classes/qdiscs, and verify counters or expected failures.

State/dependencies: Creates heavy kernel scheduler state: class trees, child qdiscs, backlog counters, delayed packets, `gso_skb`, and active-list membership. Requires `nsPlugin`, `scapyPlugin`, and many qdisc modules.

Risks/test signals: Very environment-sensitive due to modules, timing, and `tc -j` output. Twenty-eight cases expect success, eight exit `1`, five exit `2`. `matchJSON` asserts exact packet/byte/backlog counters for reentrant and underflow paths.
