<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_types.h -->
# sources/distributed-fs/ceph-client/include/linux/gfp_types.h

Purpose: Defines the bit positions, internal masks, public `__GFP_*` modifiers, and common `GFP_*` flag combinations used by the Linux memory allocator.

Important APIs/types/functions: Internal enum values define GFP bit positions for zones, mobility, reclaim, I/O, zeroing, retry policy, accounting, KASAN tag behavior, lockdep, and object extensions. Public flags include zone modifiers (`__GFP_DMA`, `__GFP_HIGHMEM`, `__GFP_DMA32`, `__GFP_MOVABLE`), mobility/placement flags, watermark flags, reclaim flags, action flags, and `__GFP_BITS_MASK`. Common combinations include `GFP_ATOMIC`, `GFP_KERNEL`, `GFP_KERNEL_ACCOUNT`, `GFP_NOWAIT`, `GFP_NOIO`, `GFP_NOFS`, `GFP_USER`, `GFP_DMA`, `GFP_DMA32`, `GFP_HIGHUSER`, `GFP_HIGHUSER_MOVABLE`, `GFP_TRANSHUGE_LIGHT`, and `GFP_TRANSHUGE`.

Control flow: Consumers build `gfp_t` values from these constants; allocator code in `gfp.h` and MM interprets zones, reclaim behavior, compaction/retry policy, and accounting from the bitmask.

State and persistence behavior: Pure compile-time definitions; no runtime state.

Dependencies and integration points: Depends on bit macros and must stay synchronized with tracing/perf MM flag decoders. Integrated into almost every allocation call path.

Risks: Bit changes are ABI-like inside kernel tooling and must update trace event decoders and perf. Some combinations are invalid or dangerous, especially `__GFP_NOFAIL` in non-sleepable contexts and reclaim flags inside filesystem locks.

Test signals: Build-time checks in MM, trace/perf flag rendering tests, allocation behavior tests for common masks, KASAN HW tags builds, lockdep builds, and documentation consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp_types.h -->
