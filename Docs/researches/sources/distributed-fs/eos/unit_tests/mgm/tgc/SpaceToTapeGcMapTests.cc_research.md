# sources/distributed-fs/eos/unit_tests/mgm/tgc/SpaceToTapeGcMapTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/tgc/SpaceToTapeGcMapTests.cc

Purpose: tests `SpaceToTapeGcMap`, the map from EOS space names to per-space tape garbage collector instances.

Important APIs and types: `SpaceToTapeGcMap`, `DummyTapeGcMgm`, `getGc`, `createGc`, `destroyAllGc`, `toJson`, and `MaxLenExceeded`.

Control flow: constructor test checks initial empty state. Unknown-space lookup returns no GC. `createGc` creates a GC for a space, duplicate creation is rejected or handled as already exists, and `createAndDestroyAllGc` verifies cleanup. JSON tests check serialized map state and max-length exception behavior.

State and persistence: in-memory map of space names to GC objects. `destroyAllGc` clears managed instances; no external persistence.

Dependencies and integration: used by multi-space TGC management to create, retrieve, report, and destroy per-space collectors.

Risks and test signals: ownership and duplicate handling are the main risks. JSON max-length behavior protects status APIs from excessive output.
