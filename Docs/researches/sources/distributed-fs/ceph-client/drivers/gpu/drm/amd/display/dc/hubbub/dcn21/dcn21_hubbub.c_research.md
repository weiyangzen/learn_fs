# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.c

Purpose: Implements DCN2.1/Renoir hubbub behavior with host-VM/rIOMMU initialization, VM-row mirrored watermarks, request-throttling settings, and a generation workaround.

Important APIs and functions: `dcn21_dchvm_init` starts DCHVM host VM initialization, polls RIOMMU active, sets power status, requests prefetch, enables clock gating, and records `riommu_active`. `hubbub21_init_dchub` programs apertures, VMID0, and optionally runs RIOMMU prefetch. `hubbub21_program_urgent_watermarks`, `stutter_watermarks`, and `pstate_watermarks` write both base and VM-row watermark fields. `hubbub21_program_watermarks` sets SAT/outstanding/QOS thresholds and self-refresh control. `hubbub21_apply_DEDCN21_147_wa` rewrites urgency watermark A.

Control flow: constructor installs a vtable that reuses DCN2 update/DCC/refclock/readback helpers but uses DCN21 init and watermark functions. Watermark routines preserve safe-lowering semantics and return pending when lower values cannot yet be applied. DCHUB init skips RIOMMU prefetch when `skip_riommu_prefetch_wa` is set.

State and persistence: uses `dcn20_hubbub` cached watermarks and VMID state plus `hubbub->riommu_active`. Hardware state includes host VM/rIOMMU registers, VM-row watermark mirrors, QOS thresholds, and aperture registers.

Dependencies and integration: depends on Linux delay, DCN20 VMID/hubbub, and DC config flags. Integrated by DCN21 resource construction and memory-management paths.

Risks and test signals: some B/C/D stutter code writes VM_ROW_ALLOW_SR_EXIT_WATERMARK_A instead of B/C/D, and pstate B lowering sets `wm_pending = false`; both deserve review. Tests should cover RIOMMU polling timeout, skip-prefetch config, VMID0 base-address `| 1` hack, watermark mirror register selection, and DEDCN21_147 workaround execution.
