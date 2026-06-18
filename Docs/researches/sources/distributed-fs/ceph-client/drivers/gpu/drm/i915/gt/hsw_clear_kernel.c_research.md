<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/hsw_clear_kernel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/hsw_clear_kernel.c

## Purpose
`hsw_clear_kernel.c` embeds a generated Haswell GPU kernel used by i915 render clear paths. It is data-only code containing precompiled EU instructions.

## Important APIs, Types, and Functions
The only symbol is `static const u32 hsw_clear_kernel[]`, a generated instruction stream. There are no C functions or exported types in this file.

## Control Flow
Control flow is encoded inside the GPU instruction words, not in C. The including/consumer code supplies this array as a shader/kernel payload for clear operations on Haswell-generation render hardware.

## State and Persistence
The array is immutable driver data. GPU-visible persistence happens when consumers copy or reference the kernel in a batch/state object. The file itself owns no locks, allocations, or runtime state.

## Dependencies and Integration Points
The file intentionally has no includes in the snippet and is normally consumed by a render clear implementation that includes or references the array. Its generated provenance comes from IGT GPU Tools and must match Haswell EU ISA expectations.

## Risks and Edge Cases
Manual modification is high risk because the words are opaque hardware instructions. Incorrect instruction data can cause GPU hangs, bad clears, or memory corruption. The symbol is `static`, so integration depends on inclusion or same-translation-unit use rather than external linkage.

## Test Signals
Signals include Haswell render clear selftests, framebuffer/buffer clear correctness, GPU hangcheck during clear batches, and binary comparison against the known generated kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/hsw_clear_kernel.c -->
