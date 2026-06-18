# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.c

## Purpose
Builds and mutates the kernel-side etnaviv GPU ring command buffer, including pipe switching, MMU flushes/context switches, user command buffer linking, event emission, cache flushes, sync points, and GPU stop/end handling.

## Important APIs, Types, and Functions
Key functions are `etnaviv_buffer_init`, `etnaviv_buffer_config_mmuv2`, `etnaviv_buffer_config_pta`, `etnaviv_buffer_end`, `etnaviv_sync_point_queue`, and `etnaviv_buffer_queue`. Important helpers include `etnaviv_cmd_select_pipe`, `etnaviv_buffer_reserve`, `etnaviv_buffer_replace_wait`, and `etnaviv_buffer_dump`. It uses `struct etnaviv_gpu`, `struct etnaviv_cmdbuf`, IOMMU mappings, chip identity flags, and command macros.

## Control Flow
The ring is initialized with a WAIT/LINK loop, optionally preceded by PPU flop reset commands. New submissions reserve space, optionally switch MMU context and flush MMU, optionally switch 2D/3D pipe with cache maintenance, link into the submitted cmdbuf, append a return sequence with cache flushes, event, WAIT/LINK loop, then atomically replaces the previous WAIT with a LINK to start execution. End and sync-point paths similarly replace a waitlink with END or a short event/END sequence.

## State and Persistence
Mutates `gpu->buffer.user_size`, `gpu->exec_state`, `gpu->mmu_context`, and `gpu->flush_seq`. Command buffer memory is persistent for the bound GPU and suballocated in DMA memory. `etnaviv_buffer_replace_wait()` uses barriers because the GPU may be reading the same WAIT while the CPU patches it.

## Dependencies and Integration Points
Depends on generated command/state headers, MMU context APIs, cmdbuf VA translation, GPU locks, BLT feature flags, PPU flop reset support, and event IDs consumed by GPU IRQ handling. Called from GPU initialization and submit execution paths.

## Risks
Incorrect prefetch dword counts, waitlink offsets, memory barriers, or context-switch ordering can jump the FE to bad addresses or hang the GPU. MMU context switches must occur only after old-context ring targets are computed. Feature-specific BLT/cache flush paths are hardware sensitive.

## Test Signals
GPU submit tests, hang recovery traces, ring debugfs dumps, command hex dumps under `DRM_UT_DRIVER`, MMU context switch stress, 2D/3D mixed workloads, and BLT-capable chip coverage are important.
