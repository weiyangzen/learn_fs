# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot_util.c

Purpose: Implements display snapshot register capture, printing, atomic-state duplication, and memory cleanup.

Important APIs/functions: `msm_disp_snapshot_add_block()` allocates a block, formats its name, aligns length, dumps registers, and appends it. `msm_disp_snapshot_capture_state()` invokes DP, DSI, and KMS-specific snapshot callbacks, then duplicates DRM atomic state. `msm_disp_state_print()` prints metadata, each block, and the DRM atomic state. `msm_disp_state_free()` releases duplicated atomic state, register dumps, block nodes, and the state object.

Control flow: Register dump allocates a padded u32 buffer and reads four registers per 16-byte row with relaxed reads, zero-filling out-of-range columns. Atomic capture records real time, locks all modeset locks with backoff, duplicates state, then drops locks. Capture order is DP blocks, DSI blocks, KMS snapshot callback, atomic state.

State and persistence: Captured register data is an owned copy detached from MMIO after capture. Atomic state is reference-counted through DRM. All allocations are freed by the devcoredump free callback.

Dependencies/integration: Depends on generated kernel release string, DRM atomic helpers/printers, MSM DP/DSI/KMS snapshot callbacks, MMIO read helpers, kvzalloc/kvfree, and Linux list management.

Risks and test signals: `num_rows = len / REG_DUMP_ALIGN` while allocation uses `aligned_len * REG_DUMP_ALIGN`; this code treats `aligned_len` as byte length after callers pass raw lengths and alignment. Snapshot capture can be expensive under modeset locks. Test odd register lengths, missing allocation handling, DP+DSI mixed devices, atomic duplication during hotplug, and devcoredump free after partial capture failure.
