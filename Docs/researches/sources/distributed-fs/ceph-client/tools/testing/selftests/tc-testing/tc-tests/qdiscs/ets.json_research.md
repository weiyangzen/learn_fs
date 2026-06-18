# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/ets.json

Purpose: 49 ETS tests for bands, quanta, strict bands, priomap validation/defaulting, class display/change, invalid boundaries, and offload arithmetic wrap handling.

APIs and control flow: Uses `$TC qdisc add|show` and `$TC class show|change` with `ets`. Positive cases verify valid combinations; negative cases exceed limits, omit values, use zero quanta, or map priorities outside configured bands.

State/dependencies: State is the ETS band table, strict/quanta arrays, priority map, and per-class quantum. Requires sch_ets; one offload case uses `$ETH`.

Risks/test signals: Boundary validation and output formatting are sensitive. Exit distribution is 29 success, 16 exit `1`, 3 exit `2`, and 1 exit `255`. Regexes check priomap defaults, class quantum changes, and u32 quanta wrap behavior.
