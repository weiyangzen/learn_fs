# sources/control-plane/mayastor/test/python/v1/rebuild/test_bdd_rebuild.py

Purpose: v1 equivalent of the rebuild BDD tests, covering rebuild start/stop/pause/resume and child online/offline state transitions through the v1 nexus service.

Important APIs and control flow: helpers map text to `nexus_pb2` enum classes. Fixtures create two 64 MiB aio files, a named nexus with `minCntlId`, `maxCntlId`, reservation key, and one source child, then look it up through `nexus_rpc.ListNexus`. Step functions add a target child with `norebuild=True`, call `StartRebuild`, `PauseRebuild`, `ResumeRebuild`, `StopRebuild`, `GetRebuildStats`, `GetRebuildState`, and `ChildOperation`. Then steps assert nexus state, source/target child states, rebuild count, rebuild state string, undefined rebuild state, and stat counters.

State, dependencies, and integration: state lives in `/tmp/disk-rebuild-*.img`, v1 nexus child records, rebuild counters, and gRPC status. It depends on `nexus_pb2`, pytest-bdd, sudo, and v1 fixtures.

Risks and test signals: `rebuild_state` catches all exceptions and converts them to `None`, which can hide unexpected errors. Unlike the legacy variant, offline child operation does not retry for degraded state. Signals are direct enum and counter comparisons.
