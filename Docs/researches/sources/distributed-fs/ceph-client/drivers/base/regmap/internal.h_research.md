# sources/distributed-fs/ceph-client/drivers/base/regmap/internal.h

## Purpose
This internal header defines the private regmap core structures, cache backend interface, debugfs hooks, range/window bookkeeping, async state, formatting helpers, and internal function prototypes shared by regmap implementation files.

## Important APIs, Types, And Functions
Important types include `struct regmap`, `struct regmap_format`, `struct regmap_async`, `struct regcache_ops`, `struct regmap_range_node`, `struct regmap_field`, and `struct regmap_ram_data`. It declares core predicates (`regmap_readable()`, `regmap_writeable()`, `regmap_volatile()`), low-level write/raw-write functions, cache lifecycle/sync helpers, async completion, endian selection, cache backend ops instances, and RAM regmap initialization helpers.

## Control Flow And State
`struct regmap` centralizes locking, bus callbacks, register format, access tables, raw/single/multi IO limits, cache configuration and state (`cache_only`, `cache_bypass`, `cache_dirty`, defaults, patch list), async queues, debugfs state, range windows, and optional hwspinlock. `struct regcache_ops` is the polymorphic cache backend contract with init/exit/populate/read/write/sync/drop/debugfs hooks.

Inline helpers compute register offsets and cache indexes using stride or stride order, expose cached value addresses, and return a user-facing regmap name. Debugfs hooks compile to no-ops without `CONFIG_DEBUG_FS`.

## Dependencies And Integration Points
This header is consumed by all regmap core, cache, debugfs, transport, and KUnit files. It depends on public `linux/regmap.h` for external configuration/types and internal regmap locking conventions.

## Risks And Test Signals
Risks include ABI-like internal structure coupling across many files, incorrect cache word-size assumptions, lock misuse when backend code calls map operations, and config-specific missing prototypes. Test signals include full regmap build coverage, lockdep with mutex/spin/raw-spin regmaps, KUnit RAM backend tests, cache backend matrix tests, and sparse/compile checks across debugfs and non-debugfs configs.
