# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/cbs.json

Purpose: 10 CBS qdisc tests for default creation, credit/slope parameters, combined settings, replace, change, delete, and class display.

APIs and control flow: Uses `$TC qdisc add|replace|change|del|show` and `$TC class show`. Options under test are `hicredit`, `locredit`, `sendslope`, and `idleslope`; replace/change mutate one parameter after setup.

State/dependencies: State is a root CBS qdisc on `$DUMMY`, removed after each case. Requires sch_cbs and namespace setup.

Risks/test signals: CBS module availability and parameter formatting are the main risks. All cases expect exit `0`; regexes confirm option values or absence after delete.
