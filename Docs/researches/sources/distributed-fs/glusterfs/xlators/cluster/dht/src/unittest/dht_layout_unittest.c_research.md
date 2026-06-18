# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_unittest.c

## Purpose
Defines a cmocka unit test for `dht_layout_new`, validating layout allocation defaults both with and without a populated DHT private config.

## Important APIs and Functions
- `helper_xlator_init`: allocates a minimal `xlator_t`, memory accounting structure, context, and per-type locks for tests.
- `helper_xlator_destroy`: destroys locks and frees the test xlator/context/accounting allocations.
- `test_dht_layout_new`: asserts invalid inputs fail, then verifies `dht_layout_new` initializes type, count, refcount, generation, and spread count.
- `main`: runs the single cmocka test group.

## Control Flow
The test first expects assert failures for NULL xlator and negative count. It then creates a test xlator with no private config and expects a layout with `DHT_HASH_TYPE_DM`, requested count, refcount 1, generation 0, and spread count 0. Next it attaches a `dht_conf_t` with `dir_spread_cnt` and `gen`, calls `dht_layout_new` again, and verifies those values are copied into the layout.

## State and Persistence
All state is in-memory test allocation. The test manually allocates/frees layouts and config, and uses lock init/destroy around the fake memory accounting records. There is no persistent output.

## Dependencies and Integration Points
Uses `dht-common.h`, GlusterFS logging/xlator headers, cmocka, and cmocka-pbc macros such as `REQUIRE`/`ENSURE`. It depends on `dht_layout_mock.c` to satisfy unrelated production symbols.

## Risks
- The helper appears to write `xl->mem_acct->num_types` before allocating `xl->mem_acct`, which is suspicious and may rely on header/macros or be a latent test bug.
- The destroy path uses `xl->mem_acct.rec`/`xl->mem_acct.num_types` member syntax inconsistent with earlier pointer syntax; this should be checked against the actual `xlator_t` definition.
- Coverage is narrow and does not test layout ranges, sorting, xattr extraction, merge, or anomaly detection.

## Test Signals
The only direct signal is allocation/default initialization of `dht_layout_new`. It is useful as a smoke test for layout struct initialization, but not for self-heal correctness.
