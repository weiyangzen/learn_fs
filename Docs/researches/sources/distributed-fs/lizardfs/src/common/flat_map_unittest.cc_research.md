# sources/distributed-fs/lizardfs/src/common/flat_map_unittest.cc

Purpose: validates `flat_map` behavior against map-like expectations.

Important APIs/types/functions: helper `fill_map`; tests constructors, swap, iterator variants, insertion/erasure, `at`, `count`, custom comparator `CCmp`, `find`, `lower_bound`, and `find_nth`.

Control flow: tests build maps through `operator[]` and inserts, then assert sorted iteration, size, lookup, thrown exceptions, and data equality.

State and persistence: test-only containers.

Dependencies and integration: includes `flat_map.h`, `gtest`, strings, and iterators. It exercises `flat_map` through its public API and indirectly tests `flat_set` as storage.

Risks: tests do not cover sorted-constructor duplicate misuse, move-only keys/values, iterator invalidation contracts, or large-scale performance.

Test signals: good behavioral coverage for intended small associative use, including custom ordering.
