# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/PathPropertiesTest.java

Purpose: validates journaled path-level property add/remove behavior and deterministic hashing.

Important APIs/types/functions: uses `PathProperties`, `NoopJournalContext`, `PropertyKey`, `ReadType`, and `WriteType`. Static maps model read/write property sets for root and nested paths.

Control flow: `empty` expects a fresh store to have no properties. `add` adds root and `/dir1` properties, overwrites existing path properties, then adds/merges additional root, nested, and sibling path entries and verifies string-keyed maps. `remove` exercises removal from empty state, removal of nonexistent paths/keys, targeted key removal leaving partial property maps, and full path removal. `hashEmpty` checks a stable non-null hash for empty state. `hash` verifies hash changes as properties are added or partially removed, returns to a previous hash when state returns to the same map, and returns to the empty hash after all removals.

State and persistence behavior: `PathProperties` is in-memory here, but operations accept a journal context, so these calls represent the journaled mutation API used by the meta master.

Dependencies and integration points: path properties feed per-path configuration in the master and must hash consistently for configuration/reporting comparisons.

Risks: `NoopJournalContext` means actual journal entry emission is not validated. Tests do not cover invalid property names, concurrent access, or path normalization.

Test signals: strong signal for core map mutation semantics and hash determinism.
