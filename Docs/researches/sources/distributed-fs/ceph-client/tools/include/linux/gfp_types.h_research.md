<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/gfp_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/gfp_types.h

## Purpose
This header defines the `gfp_t` allocation flag bit layout and common GFP flag combinations used by user-space tools that build against kernel-style allocator APIs.

## APIs And Flow
It exports internal `___GFP_*` bit positions, public `__GFP_*` flags, `GFP_ZONEMASK`, `__GFP_BITS_SHIFT`, `__GFP_BITS_MASK`, and composites such as `GFP_ATOMIC`, `GFP_KERNEL`, `GFP_NOIO`, `GFP_NOFS`, `GFP_USER`, `GFP_HIGHUSER_MOVABLE`, and THP combinations. There is no executable flow; allocation behavior is expressed as bitmask composition consumed by `linux/gfp.h`, `slab.h`, and tool allocator shims.

## State, Dependencies, Risks, Tests
State is compile-time only. It depends on `linux/bits.h`, `gfp_t` from tool types, and config symbols such as `CONFIG_KASAN_HW_TAGS` and `CONFIG_LOCKDEP`. Risks are drift from kernel GFP layout, especially because comments require synchronized updates in trace/mm flag users and perf kmem tooling. Test signals are compile checks for every GFP macro, bitmask value comparisons against the kernel copy, and allocator tests proving `__GFP_ZERO`, reclaim, accounting, and KASAN-related flags are accepted by tools shims.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/gfp_types.h -->
