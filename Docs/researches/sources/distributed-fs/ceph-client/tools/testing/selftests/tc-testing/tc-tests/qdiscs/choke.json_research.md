# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/choke.json

Purpose: 8 CHOKE qdisc tests covering default creation, `min`, `max`, `ecn`, `burst`, delete, replace, and change.

APIs and control flow: Uses `$TC qdisc add|del|replace|change|show`; add cases verify configured output, replace/change mutate thresholds, and delete verifies absence.

State/dependencies: State is a root CHOKE scheduler on `$DUMMY`. Requires sch_choke and `nsPlugin`.

Risks/test signals: CHOKE is not always enabled, and output wording for thresholds/ECN can vary. All tests expect exit `0` with one match for presence or zero after delete.
