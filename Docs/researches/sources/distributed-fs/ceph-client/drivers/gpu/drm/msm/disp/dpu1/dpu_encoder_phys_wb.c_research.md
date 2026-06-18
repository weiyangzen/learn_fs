# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_wb.c

## Purpose
Implements writeback physical encoders. It prepares writeback jobs, maps framebuffer layout and addresses, configures WB/CDM/CWB/CTL routing, applies VBIF QoS and outstanding-transaction settings, and waits for WB-done IRQ completion.

## Important APIs, Types, and Functions
The constructor is `dpu_encoder_phys_wb_init`; `dpu_encoder_phys_wb_init_ops` installs writeback-specific encoder ops. Important helpers are `dpu_encoder_phys_wb_prepare_wb_job`, `dpu_encoder_phys_wb_cleanup_wb_job`, `dpu_encoder_phys_wb_setup`, `dpu_encoder_phys_wb_setup_fb`, `dpu_encoder_phys_wb_setup_ctl`, `_dpu_encoder_phys_wb_update_flush`, `dpu_encoder_phys_wb_done_irq`, `dpu_encoder_phys_wb_wait_for_commit_done`, `dpu_encoder_phys_wb_set_ot_limit`, `dpu_encoder_phys_wb_set_qos_remap`, and `dpu_encoder_phys_wb_set_qos`.

## Control Flow and State
Writeback is always considered master. `prepare_wb_job` pins/prepares the framebuffer, derives DPU plane sizes and addresses, records job/connector backpointers, and handles planar Cb/Cr plane swap for selected formats. Pre-kickoff queues the DRM writeback job, configures VBIF, framebuffer output, CDM for YUV, CWB, CTL topology, and pending flush masks. WB-done IRQ sends frame done and vblank callbacks, decrements pending kickoff, signals DRM writeback completion, and wakes commit waiters. Timeouts snapshot once, signal completion anyway, emit frame error, decrement pending count, and set `DPU_ENC_ERR_NEEDS_HW_RESET`.

## Dependencies and Integration Points
Integrates with DRM writeback connector/job APIs, MSM framebuffer prepare/cleanup and IOVA helpers, DPU format helpers, VBIF QoS helpers, catalog performance tables, WB ops, CTL ops, CDM/CWB helpers, merge-3D, and core IRQ registration.

## Risks and Test Signals
Risks include unbalanced framebuffer prepare/cleanup, stale `wb_job` making commits valid incorrectly, format plane-address mistakes for planar/UBWC/YUV output, incorrect RT vs NRT QoS when CWB is active, and missing legacy WB teardown for pre-DPU5 hardware. Tests should cover RGB and YUV writeback, UBWC/tiled layouts, CWB path, WB-done timeout, connector completion signaling, IRQ refcounting, and disable cleanup after active commits.
