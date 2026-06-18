# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.c

Purpose: manages HuC firmware initialization, upload, authentication via GuC or GSC, status sanitization, and debug printing.

Important functions: `xe_huc_init`, `xe_huc_init_post_hwconfig`, `xe_huc_upload`, `xe_huc_auth`, `xe_huc_is_authenticated`, `xe_huc_sanitize`, `xe_huc_print_info`, plus local GSC auth helpers `huc_alloc_gsc_pkt`, `huc_emit_pxp_auth_msg`, and `huc_auth_via_gsccs`.

Control flow: init marks firmware type as HuC, skips unsupported non-media GTs on newer platforms, initializes firmware metadata, skips extra work if disabled or SR-IOV VF, allocates a GGTT system BO for GSC auth packets when GSC headers are present, and marks firmware loadable. Upload sends the firmware through `xe_uc_fw_upload`. Authentication first checks existing auth status, verifies firmware is loaded, triggers GuC RSA auth or submits a PXP 4.3 GSC packet through GSCCS, waits for the appropriate MMIO auth bit, and updates firmware status to running or load fail.

State/persistence: `struct xe_huc` stores generic firmware state and an optional `gsc_pkt` BO used as input/output packet storage. Firmware BO may be reinitialized into VRAM after hwconfig on DGFX.

Dependencies/integration: uses uC firmware helpers, GuC auth, GSC packet submit helpers, GGTT BO mapping, forcewake/MMIO, PXP command ABI, SR-IOV checks, and GT/device logging.

Risks/test signals: platform/GT support checks are sensitive because HuC availability differs between media and primary GTs. GSC auth retries handle pending replies; reply parsing and status handling must distinguish already-authenticated from real failure. Test GuC and GSC auth modes, missing packet BO, pending GSC replies, auth timeout, firmware disabled/unavailable, DGFX VRAM reinit, and HuC status debug output.
