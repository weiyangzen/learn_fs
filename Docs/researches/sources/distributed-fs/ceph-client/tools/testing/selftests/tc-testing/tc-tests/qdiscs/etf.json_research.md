# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/etf.json

Purpose: 5 ETF tests covering default creation, `delta` nanoseconds, `deadline_mode`, `skip_sock_check`, and deletion.

APIs and control flow: Uses `$TC qdisc add|del|show`; creation cases verify `etf` output and delete verifies absence.

State/dependencies: State is root ETF qdisc configuration, with no runtime packet scheduling workload. Requires sch_etf and `nsPlugin`.

Risks/test signals: ETF clock/socket semantics and module availability vary. All cases expect exit `0`; these are configuration/display tests rather than packet-deadline behavior tests.
