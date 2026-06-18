# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/msm_disp_snapshot.h

Purpose: Declares MSM display snapshot data structures and capture/print/free APIs.

Important APIs/types: `struct msm_disp_state` stores device pointers, a list of register blocks, duplicated DRM atomic state, and capture time. `struct msm_disp_state_block` stores a named register block, size, copied register state, and base address. APIs initialize/destroy snapshot support, trigger async capture, capture synchronously under `dump_mutex`, print, capture register/atomic state, free dumps, and add named register blocks. Constants define max blocks, console dump switch, and register dump alignment.

Control flow/state: KMS/DP/DSI/DPU snapshot providers call `msm_disp_snapshot_add_block()` during capture; print/free iterate the block list. `msm_disp_snapshot_state_sync()` is the synchronous entry for the worker.

Dependencies/integration: Includes DRM atomic/device/print internals, Linux debugfs/list/kthread/devcoredump/PM headers, and MSM KMS definitions. The relative include of `drm_crtc_internal.h` couples it to DRM internals.

Risks and test signals: The header exposes DRM-internal dependencies and a fixed name buffer size. Test builds across kernel DRM internal changes and capture of multiple register blocks with long formatted names.
