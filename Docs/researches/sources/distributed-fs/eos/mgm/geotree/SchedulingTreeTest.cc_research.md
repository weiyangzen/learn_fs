# sources/distributed-fs/eos/mgm/geotree/SchedulingTreeTest.cc

## Purpose
`SchedulingTreeTest.cc` is a standalone test and benchmark harness for the EOS geotree scheduling structures. It validates slow-tree construction, fast-tree generation, placement/access behavior, geotag proximity lookup, gateway proxy access mapping, and performance characteristics for copy, placement, access, update, and rebuild operations.

## Important APIs, Types, And Functions
Important helpers include `PopulateSchedGroupFromFile`, `treeDepthSimilarity`, template `functionalTestFastTree`, `testAccess`, `debugDisplayPlct`, and `debugDisplayAccs`. There are three entry-style functions: the compiled `main()` demonstrates gateway access mapping on a small hand-built tree; `main2()` is another small gateway/saturation experiment; and `mainFull()` is the larger functional and burn-in test using `SchedulingTreeTest.cc.testfile`.

## Control Flow
The active `main()` constructs a slow tree with three nodes, builds a `FastGatewayAccessTree`, prints access mapping and slow-tree tables, then queries several geotags through `GeoTag2NodeIdxMap` and `findFreeSlotFirstHitBack()` to show which proxygroup can serve each geotag. `functionalTestFastTree()` copies placement and access trees into stack buffers, places a random number of replicas, enumerates access replicas, checks placement/access set equality, checks closest geotag lookup, then verifies access selection chooses a placed replica with maximal tree-depth similarity. `mainFull()` parses host/geotag data into scheduling groups, inserts randomized filesystem states, removes/reinserts each item to exercise mutation, builds all fast-tree variants, validates draining and balancing similarity maps, runs functional tests, prints display examples, and runs burn-in speed loops.

## State And Persistence
The test stores all state in process memory: generated scheduling groups, slow trees, fast trees, info vectors, id maps, geotag maps, status counters, and benchmark buffers. Input persistence is limited to the `.testfile` next to the source. Test output is written to stdout/stderr.

## Dependencies And Integration Points
The file includes `SchedulingSlowTree.hh`, EOS logging, string utilities, random utilities, table formatting, and standard containers/streams. It directly instantiates and calls the slow/fast tree APIs used by `GeoTreeEngine`, making it a useful low-level regression harness even though it is not written as a modern unit-test framework.

## Risks And Edge Cases
The active `main()` means `mainFull()` burn-in coverage is not run unless the source is modified or the symbol is invoked differently by a build rule. The tests rely heavily on `assert`, so release builds with `NDEBUG` would normally disable checks, although the file explicitly `#undef NDEBUG` before includes. Randomized data can make failures less reproducible unless RNG seeding is controlled. Fixed stack buffers use `bufferSize = 16384`, so larger trees can fail copy tests because `copyToBuffer()` returns required size. The functional test template casts copied trees to concrete `FastPlacementTree` and `FastROAccessTree` pointers, which matches current call sites but is not fully generic.

## Test Signals
Existing signals include assertion success for placement/access round trips, geotag closest-node identity, nearest-replica access, insert/remove/reinsert, fast-tree consistency, draining placement/access, and fs-id map lookup. Performance output reports placements/sec, copies/sec, repopulation/sec, access/sec, update/sec, and builds/sec. Additional desirable signals would make `mainFull()` part of automated CI, add deterministic RNG seeds, cover saturated skip with large node counts, and check failure paths for undersized buffers/maps.
