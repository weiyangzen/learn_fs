# sources/distributed-fs/ipfs-kubo/repo/common/common_test.go

Purpose: tests the deep merge behavior that repo config persistence relies on when struct-derived config values are merged back into a raw user JSON map.

Important APIs and control flow: `TestMapMergeDeepReturnsNew` checks the left input is not mutated. `TestMapMergeDeepNewKey` checks additions from the right map. `TestMapMergeDeepRecursesOnMaps` verifies nested maps are merged recursively. `TestMapMergeDeepRightNotAMap` confirms a non-map right value replaces an existing left map.

State and persistence: all data is in-memory test maps, but the asserted semantics protect persisted config files from accidental removal of keys unknown to the typed config struct.

Dependencies and integration: uses `stretchr/testify/require`; indirectly documents expectations for `fsrepo.SetConfig`.

Risks and test signals: strong signal for merge semantics, but no direct tests for `MapGetKV` or `MapSetKV`, no nil-map variants beyond clone behavior, and no type-alias map cases.
