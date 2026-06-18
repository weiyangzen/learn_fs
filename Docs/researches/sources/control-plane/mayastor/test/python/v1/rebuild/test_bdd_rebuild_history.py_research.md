# sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild_history.py

Purpose: v1 pytest-bdd coverage for rebuild history records. It focuses on full rebuild of a faulted replica; partial rebuild scenario is declared but not implemented.

Important APIs and control flow: fixtures create three 64 MiB aio files for source, target, and new child, create a two-child nexus, and expose lookup by UUID. Steps remove `target_uri`, add `new_child_uri` with `norebuild=True`, start a rebuild on the new child, sleep two seconds, call `GetRebuildHistory`, and assert exactly one record exists. Partial rebuild steps raise `NotImplementedError`.

State, dependencies, and integration: state includes three host image files, a v1 nexus with child replacement, rebuild execution state, and rebuild history records stored by io-engine. It depends on pytest-bdd feature files, `nexus_pb2`, sudo, and v1 fixtures.

Risks and test signals: the full rebuild waits a fixed two seconds instead of polling completion, so slow hosts may be flaky. The partial rebuild scenario will fail if enabled. Assertions only check record count, not record fields, child URI, or rebuild type. The file still provides useful coverage that history is populated and retrievable after a full rebuild path.
