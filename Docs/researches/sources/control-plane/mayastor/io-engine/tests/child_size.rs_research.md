# sources/control-plane/mayastor/io-engine/tests/child_size.rs

Purpose: verifies nexus creation rejects children that are too small for requested nexus size or metadata requirements, and cleans up bdevs on failure.

Important APIs/types/functions: `create_nexus` builds malloc child URIs from requested sizes and calls `nexus_create`. Tests use `nexus_lookup_mut` and `UntypedBdev` enumeration/lookups.

Control flow: `child_size_ok` creates a 16 MiB nexus with larger/equal children, verifies nexus and child bdevs exist, destroys the nexus, and verifies cleanup. `child_too_small` attempts a 16 MiB nexus with an 8 MiB child and expects failure/no leaked bdevs. `too_small_for_metadata` attempts a 4 MiB nexus and expects failure because metadata consumes capacity.

State and persistence: malloc bdevs only; all state is in memory. `OnceCell<MayastorTest>` shares one Mayastor instance.

Dependencies and integration points: nexus creation/validation, malloc URI parser, bdev registry cleanup.

Risks and edge cases: assumes no other tests leave bdevs in the shared process because it asserts global bdev count is zero. Uses fixed names `core_nexus`, `m0`, `m1`, `m2`.

Test signals: covers successful cleanup and failure cleanup around size validation.
