# sources/distributed-fs/eos/unit_tests/mgm/tgc/MultiSpaceTapeGcTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/tgc/MultiSpaceTapeGcTests.cc

Purpose: tests `MultiSpaceTapeGc`, which coordinates tape garbage collectors across one or more EOS spaces.

Important APIs and types: `MultiSpaceTapeGc`, `DummyTapeGcMgm`, `MaxLenExceeded`, start/stop/restart operations, and per-space GC accessors.

Control flow: constructor and start tests create one-space and two-space configurations, start workers, and assert expected GC creation/running state. Stop and restart tests verify lifecycle transitions for one and two spaces.

State and persistence: state is in-memory orchestration of per-space GC instances and worker running flags. Tests may start worker threads but use dummy MGM behavior rather than real namespace/tape state.

Dependencies and integration: integrates `SpaceToTapeGcMap`-style space management with actual TGC lifecycle controls.

Risks and test signals: lifecycle tests are important because repeated start/stop can create duplicate workers or stale GC state. The tests focus on orchestration, not detailed file garbage-collection behavior.
