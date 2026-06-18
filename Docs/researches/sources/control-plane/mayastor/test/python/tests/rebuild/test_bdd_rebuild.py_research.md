# sources/control-plane/mayastor/test/python/tests/rebuild/test_bdd_rebuild.py

Purpose: legacy pytest-bdd coverage for nexus rebuild operations. It maps feature scenarios for running, stopping, pausing, resuming rebuilds and setting children online/offline.

Important APIs and control flow: helpers translate textual nexus, child, and action states into `mayastor_pb2` enums. `lookup_nexus`, `lookup_nexus_child`, and retrying `wait_child_state` poll observed state. Fixtures create two 64 MiB aio files, create a single-child nexus via `ms.CreateNexus`, then add a target child with `norebuild=True`. Step functions call `AddChildNexus`, `StartRebuild`, `PauseRebuild`, `ResumeRebuild`, `StopRebuild`, `GetRebuildStats`, `GetRebuildState`, and `ChildOperation`.

State, dependencies, and integration: state exists in host `/tmp/disk-rebuild-source.img` and target image, plus transient nexus child/rebuild state inside `ms0`. The file depends on pytest-bdd feature text, `retrying`, sudo file setup, `common.mayastor`, and legacy `mayastor_pb2`.

Risks and test signals: bare `except` in `rebuild_state` may hide unexpected gRPC failures. Offline waits retry only five times, making timing-sensitive regressions possible. Assertions cover nexus state, child state, rebuild count, explicit rebuild state, undefined state, and zero/non-zero rebuild stat counters.
