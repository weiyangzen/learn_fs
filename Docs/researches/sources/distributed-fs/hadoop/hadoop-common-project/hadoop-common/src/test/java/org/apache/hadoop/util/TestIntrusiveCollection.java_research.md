# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIntrusiveCollection.java

Purpose: behavior-driven tests for `IntrusiveCollection`, where list linkage is stored inside each element to reduce per-node allocation.

Important APIs and types: `IntrusiveCollection<T>`, `IntrusiveCollection.Element`, `add`, `remove`, `clear`, `contains`, `isEmpty`, and iteration. `SimpleElement` implements the intrusive callbacks and stores per-collection prev/next/membership maps.

Control flow: scenarios cover adding a single element, removing that element, clearing multiple elements, and iterating three inserted elements in insertion order. Each operation verifies collection membership through the public API rather than inspecting internal pointers directly.

State and persistence: state is in memory and split between the collection and each element's per-list linkage maps. The test model supports membership in multiple intrusive collections because maps are keyed by collection instance.

Dependencies and integration points: extends `HadoopTestBase` for assertion helpers and tests the element callback contract required by any production intrusive element.

Risks: stale element membership flags, broken prev/next updates, iterator order changes, or clear not invoking element cleanup would lead to memory retention or corrupted intrusive lists. Test signals are simple add/remove/clear/iteration assertions over concrete callback state.
