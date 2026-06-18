# sources/distributed-fs/lizardfs/src/common/goal.h

Purpose: declares the domain model for LizardFS replication goals, including standard, tape, XOR, and erasure-code slice layouts with label constraints.

Important APIs/types/functions: `detail::SliceType` maps integer type IDs to names and expected part counts, including EC types. `SliceIterator` iterates part proxies. `Goal::Slice` stores part sizes and label data in compact flat vectors, exposes label-map proxies per part, copy counting, merge, validity, equality, and iterators. `GoalId` validates goal IDs 1..40. `Goal` stores named slices in a `flat_set`, exposes `setSlice`, `mergeIn`, `find`, `operator[]`, `size`, name access, iterators, and equality.

Control flow: callers build or parse goals by accessing slices and part label maps. Missing `Goal::operator[]` creates a new slice for a type; const access throws when absent.

State and persistence: goals are in-memory policy objects with compact storage. They integrate with config/parsing layers but do not persist themselves here.

Dependencies and integration: depends on `MediaLabel`, `flat_map`, `flat_set`, `small_vector`, and `vector_range`. Used by chunk placement, slice traits, read planners, and configuration.

Risks: proxy objects are invalidated by inserts that resize underlying flat storage; comments warn that modifying one part can invalidate others. `SliceType::isValid` covers numeric range, not semantic availability in a deployment. Assertions protect many invariants only in debug builds.

Test signals: `goal_unittest.cc` validates representative slice operations and merge behavior.
