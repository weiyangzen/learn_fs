# sources/distributed-fs/ceph-client/tools/include/linux/types.h

## Purpose
Supplies a small userspace-compatible subset of Linux kernel type definitions for tools built from the Ceph-client kernel tree. It lets tools include kernel-style headers without pulling in the full in-kernel type system.

## APIs, Types, and Functions
Defines forward declarations for `struct page` and `struct kmem_cache`, `gfp_t` flag categories, fixed-width aliases `u64/s64/u32/s32/u16/s16/u8/s8`, bitwise-endian aliases `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`, checksum types, `phys_addr_t`, `atomic_t`, `refcount_t`, and simple `list_head`, `hlist_head`, and `hlist_node` containers. Sparse annotations such as `__bitwise`, `__force`, `__user`, `__must_check`, and `__cold` are reduced for tools builds.

## Control Flow, State, and Persistence
There is no executable control flow. State is purely compile-time type layout and annotation state that downstream tools code relies on when compiling kernel-derived helpers. `phys_addr_t` changes width based on `CONFIG_PHYS_ADDR_T_64BIT`, so persisted binary layouts that embed it are configuration-sensitive.

## Dependencies and Integration
Depends on UAPI Linux type headers, C99 integer types, and optional sparse `__CHECKER__` behavior. Integration points are kernel tool headers under `tools/include/linux`, perf/libbpf-style userspace helpers, list/hlist consumers, and any code that expects kernel endian/checksum type spelling.

## Risks and Test Signals
Risks include ABI mismatch with real kernel headers, accidental use of these reduced definitions in contexts that need true kernel-only semantics, and config-dependent `phys_addr_t` width. Test signals are building all tools against this header, sparse builds for bitwise annotations, 32-bit and 64-bit compile coverage, and static checks that list/hlist layout matches tool expectations.
