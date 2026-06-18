# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration_types.h

Purpose: defines the per-GT, per-VF PF migration state embedded in VF metadata.

Important type: `struct xe_gt_sriov_migration_data` contains a `ptr_ring` for migration packets and a nested save state with `data_remaining` bitmap and `vram_offset`.

Control flow: PF control checks ring full/empty states to enter WAIT_DATA bits; migration save logic uses `data_remaining` to decide which packet type to emit next and `vram_offset` to continue chunked VRAM saves.

State and persistence: all state is volatile and per VF. Ring cleanup is registered during PF migration init and frees unprocessed packet objects.

Dependencies and integration: includes Linux `ptr_ring`; embedded in `xe_gt_sriov_pf_types.h`.

Risks: `data_remaining` uses packet type values as bit positions, so packet enum changes must remain compatible. `vram_offset` must reset at save start to avoid skipped chunks.

Test signals: migration save restart, ring cleanup on driver teardown, and large LMEM tests that advance `vram_offset` across multiple chunks.
