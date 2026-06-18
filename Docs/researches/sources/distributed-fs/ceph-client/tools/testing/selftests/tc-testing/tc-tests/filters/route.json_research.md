# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/route.json

Purpose: 9 route-filter tests covering `from`, `to`, `fromif`, classid selection, gact/skbedit action chains, listing, deletion, and class-reference protection after replacement.

APIs and control flow: Uses `$TC filter add|show|ls|del`, `$TC qdisc add|del`, and `$TC class add|delete|show`. Setups prepare ingress or DRR state, commands install/delete route filters, and verification lists filters or classes under expected parents.

State/dependencies: State is route classifier configuration on `$DEV1` and DRR class references under handle `10:`. Requires `nsPlugin`, route classifier, ingress, DRR, gact, and skbedit support.

Risks/test signals: Route output formatting is legacy and regex-sensitive. Eight cases expect exit `0`; the class-reference case expects class deletion to fail with exit `2` and `class drr 10:1` to remain.
