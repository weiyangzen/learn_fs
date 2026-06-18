# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.c

Purpose: implements PF-side per-GT VF migration packet production and restoration. It saves/restores GGTT, GuC firmware state, MMIO software flags, and VRAM into `xe_sriov_packet` records exchanged with userspace through a small per-VF ring.

Important APIs and functions: exported helpers include init, component save/restore for GuC/GGTT/MMIO/VRAM, `xe_gt_sriov_pf_migration_size`, ring empty/full/free, save bitmap init/pending/complete, and save/restore produce/consume functions. Internal helpers issue `GUC_ACTION_PF2GUC_SAVE_RESTORE_VF`, snapshot VF GGTT config, read/write VF SW flag MMIO through a VF view, and copy VRAM chunks with `xe_migrate_vram_copy_chunk`.

Control flow: save initialization resets `data_remaining` and VRAM offset, then marks required packet types. PF control repeatedly calls component save functions in GuC, GGTT, MMIO, VRAM order. Each save allocates a packet, fills header/body, and produces it to the ring; VRAM returns `-EAGAIN` until all 512 MiB chunks are emitted. Restore consumes packets from the ring and dispatches by packet type.

State and persistence: per-VF `struct xe_gt_sriov_migration_data` stores a `ptr_ring`, save bitmap, and VRAM offset. Data packets own BO-backed buffers and are freed on consume, failure, cleanup action, or ring flush. Migration support is disabled globally if GuC firmware is older than 70.54.0.

Dependencies and integration: used by PF control save/restore state machines and higher-level `xe_sriov_pf_migration.c` userspace orchestration. Depends on PF config for GGTT/LMEM objects, GuC buffers and CT, packet helpers, MMIO VF view, migrate copy fences, DRM exec locking, and PF migration waitqueues.

Risks: ring size is only five packets, so backpressure is expected. VRAM copy timeout is 5 seconds per chunk and chunk size is 512 MiB. Restore validates VRAM bounds but packet ordering is effectively controlled by the producer. GuC state sizing is queried dynamically but a header TODO still defines an 8 MiB maximum constant elsewhere. Failure paths must free packets exactly once.

Test signals: save/restore with and without LMEM, multi-chunk VRAM migration, ring full/empty wakeups, invalid packet sizes/offsets, old GuC firmware support disabling, and fault injection for BO allocation, GuC buffer allocation, CT errors, fence timeout, and interrupted wait events.
