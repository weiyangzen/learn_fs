# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.c

## Purpose
`xe_lrc.c` implements Logical Ring Context creation, layout, register image initialization, ring writes, seqno fences, memory-backed interrupt register patching, context-restore workaround batches, default LRC dumping/lookup, hang snapshots, and context timestamp accounting.

## Important APIs, Types, And Functions
- Public creation/lifetime: `xe_lrc_create()`, `xe_lrc_destroy()`, `xe_lrc_get()`/`put()` in the header.
- Size/layout helpers: `xe_gt_lrc_hang_replay_size()`, `xe_gt_lrc_size()`, `xe_lrc_reg_size()`, `xe_lrc_engine_state_size()`, offsets, and GGTT/map helpers.
- Context initialization: `empty_lrc_data()`, `set_offsets()`, `set_context_control()`, `set_memory_based_intr()`, `xe_lrc_ctx_init()`, and `xe_lrc_init()`.
- Ring and descriptor helpers: `xe_lrc_write_ring()`, `xe_lrc_set_ring_head/tail()`, `xe_lrc_ring_head/tail/space()`, and `xe_lrc_descriptor()`.
- Fence/seqno helpers: `xe_lrc_alloc_seqno_fence()`, `xe_lrc_init_seqno_fence()`, `xe_lrc_seqno()`, and start-seqno equivalents.
- Workaround/indirect context setup: `setup_wa_bb()`, `setup_indirect_ctx()`, `xe_lrc_setup_wa_bb_with_scratch()`.
- Debug/recovery: `xe_lrc_dump_default()`, `xe_lrc_lookup_default_reg_value()`, `xe_lrc_snapshot_capture()`, delayed capture/print/free.
- Utilization: `xe_lrc_timestamp()` and `xe_lrc_update_timestamp()`.

## Control Flow
Creation allocates `struct xe_lrc`, calculates BO size from ring, PPHWSP, context image, optional indirect context/ring-state pages, and WA BB, then creates a GGTT-pinned context BO plus a system seqno BO. `xe_lrc_ctx_init()` copies default or replay state, writes VM PDP/ASID, programs memory IRQ pointers and MSI-X vector data, initializes ring registers, descriptor fields, arbitration, seqno memory, WA BB, and optional indirect context. Runtime ring writes update the software tail and wrap around the mapped ring. Snapshot capture grabs stable scalar state immediately and defers BO copy to a sleepable path.

## State And Persistence
The LRC BO contains ring, PPHWSP, context image, optional indirect pages, and WA BB. `seqno_bo` stores GPU-written sequence numbers in system memory. `struct xe_lrc` stores descriptor, ring tail shadow, fence context, replay size, flags, and cached timestamp. BOs are pinned/mapped until refcounted destruction. Context images are persistent GPU-visible state that may be copied from defaults, replay buffers, or updated after GGTT address changes.

## Dependencies And Integration Points
The file integrates with hardware engine metadata, GT default LRC storage, VM page-table descriptors, BO/GGTT allocation, memory IRQ pointers, MSI-X vectors, ring operation workarounds, configfs test batch injection, DRM client BO accounting, hw fences, tracepoints, and Xe map wrappers. It uses generated register layout constants and MI/GFXPIPE/GFX_STATE instruction definitions.

## Risks
The file is sensitive to platform register layout tables and engine-class variants. Indirect context and indirect ring-state offsets depend on BO size and flags. Workaround batch generation must never overflow 4 KiB WA BB or indirect context limits. Configfs-injected batches intentionally taint the kernel and can submit arbitrary context-restore commands. Timestamp accounting is explicitly racy for active contexts and requires read-again logic. Memory IRQ pointers must be repatched if BO GGTT addresses change.

## Test Signals
Tests should cover LRC sizing by platform/class, context creation with VM/user/PXP/runalone flags, ring wrap writes, seqno fence initialization, WA BB scratch path for iomem/non-iomem maps, indirect context setup, memory IRQ pointer patching, MSI-X vector programming, default LRC register lookup, snapshot delayed capture, and timestamp update on active/inactive contexts.
