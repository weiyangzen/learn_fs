# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/hfsc.json

Purpose: 8 HFSC tests for default creation, service-curve class creation (`sc`, `rt`, `ls`, `ul`), umax/dmax conversion, delete, class display, and inner realtime-to-service-curve upgrade.

APIs and control flow: Uses `$TC qdisc add|del|show` and `$TC class add|show`. Class tests add HFSC classes and match converted service-curve output.

State/dependencies: State is an HFSC class tree with service-curve parameters. Requires sch_hfsc and `nsPlugin`.

Risks/test signals: Exact rate/unit conversions are regex-sensitive (`2464Kbit`, `5ms`, `8bit`). All cases expect exit `0`.
