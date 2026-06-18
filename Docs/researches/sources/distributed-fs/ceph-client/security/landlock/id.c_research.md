# sources/distributed-fs/ceph-client/security/landlock/id.c

## Purpose

`id.c` implements audit-only unique ID generation for Landlock domains. IDs are 64-bit, boot-randomized, monotonic, and slightly randomized between allocations to reduce predictability.

## Important APIs, Types, and Functions

`next_id` is the global atomic counter. `init_id()` initializes a counter to `2^32 + random_32bits` using `cmpxchg` so initialization happens once. `landlock_init_id()` seeds `next_id`. `get_id_range()` returns the current ID and increments by `number_of_ids + random_4bits`. `landlock_get_id_range()` uses a random low nibble for blurring. KUnit tests cover initialization and step behavior.

## Control Flow

At LSM init, `landlock_init_id()` seeds the counter. Domain creation requests one ID through `landlock_get_id_range(1)`. Atomic fetch-add returns a unique range start and reserves space for future IDs.

## State and Persistence Behavior

State is an in-memory atomic counter for the running boot. IDs are not persisted across reboots, but the randomized high starting range reduces collision and information leakage across logs.

## Dependencies and Integration Points

The file is compiled under `CONFIG_AUDIT` and used by `domain.c`. It depends on random helpers, atomics, and KUnit for tests.

## Risks and Test Signals

Failure to initialize would yield ID 0 warnings. Overflow is theoretically possible but made impractical by a large range and randomized stepping. Test KUnit suite `landlock_id`, boot audit domain creation, and repeated restrict-self ID uniqueness.
