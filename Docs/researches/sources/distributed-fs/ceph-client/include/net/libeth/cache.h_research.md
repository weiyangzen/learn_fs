# sources/distributed-fs/ceph-client/include/net/libeth/cache.h

Purpose: Supplies compile-time cacheline layout assertion macros for libeth data structures, especially structures split into read-mostly, read-write, and cold cacheline groups.

Important APIs/types/functions: `libeth_cacheline_group_assert` validates a named cacheline group size using `offsetof` and `offsetofend`; on 64-bit 64-byte-cacheline builds it requires exact size, otherwise less-than-or-equal. `libeth_cacheline_struct_assert` validates aggregate struct size and cacheline alignment. `libeth_cacheline_set_assert` checks read-mostly, read-write, cold groups and final struct size. Helper macros compute aligned sums for one to three groups.

Control flow: These are compile-time static assertions only. They run during compilation and produce build errors when structures drift from expected layout.

State and persistence: No runtime state. The macros enforce source-level layout contracts.

Dependencies/integration: Depends on Linux cache macros, `SMP_CACHE_BYTES`, static assertions, and local struct group naming convention `__cacheline_group_begin__*`/`end__*`.

Risks: Exact assertions only apply to 64-bit/64-byte cacheline builds, while other builds allow smaller/equal sizes; expected values must be updated intentionally when structure layouts change. Test signals are compile coverage on supported architectures and CI builds with `CONFIG_64BIT` and 64-byte cachelines.
