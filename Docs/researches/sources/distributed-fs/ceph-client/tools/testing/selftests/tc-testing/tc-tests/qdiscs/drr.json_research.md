# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/drr.json

Purpose: 4 DRR tests for root qdisc creation, deletion, class display, and rejection of classid `TC_H_ROOT`.

APIs and control flow: Uses `$TC qdisc add|del|show` and `$TC class add|show`. Positive cases verify qdisc/class output; the negative case attempts invalid root class creation.

State/dependencies: State is a classful DRR root and optional classes. Requires sch_drr and `nsPlugin`.

Risks/test signals: DRR output can be minimal/version-sensitive. Three cases expect exit `0`; invalid classid expects exit `2`.
