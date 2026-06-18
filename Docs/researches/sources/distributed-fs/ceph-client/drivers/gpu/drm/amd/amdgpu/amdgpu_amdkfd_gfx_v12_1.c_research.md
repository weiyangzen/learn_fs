# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c

Purpose: this file adapts the narrow GFX12 KFD/KGD support to GC 12.1.0 multi-instance hardware. It uses `amdgpu_gfx_select_me_pipe_q`, `GET_INST`, and XCC-aware register writes for queue selection, interrupt setup, dumps, wave control, trap value generation, and address watchpoints.

Important APIs and functions: `init_interrupts_v12_1`, `hqd_dump_v12_1`, `hqd_sdma_dump_v12_1`, `wave_control_execute_v12_1`, debug trap enable/disable, trap override validation and conversion, wave-launch mode, address-watch setup/clear, and SDMA doorbell placeholder populate `gfx_v12_1_kfd2kgd`. `get_sdma_rlc_reg_offset` maps a logical SDMA engine through `GET_INST(SDMA0, engine_id)` and `adev->sdma.num_inst_per_xcc` to select SDMA0 or SDMA1 register bases per XCC.

Control flow: compute dump selects the requested queue for the requested instance, reads 56 HQD registers from `regCP_MQD_BASE_ADDR` through `regCP_HQD_PQ_WPTR_HI`, and releases selection. SDMA dump calculates a per-instance queue offset and reads the compact queue register range through context status. Wave control locks `grbm_idx_mutex`, writes per-instance `GRBM_GFX_INDEX` and `SQ_CMD`, and restores broadcast selection. Debug trap and trap-mask logic mirrors GFX12, including wave-start/end support and special launch-mode value 4 for stall. Address watch writes TCP watch address registers through `WREG32_XCC` and uses a 25-bit high address mask.

State and persistence: state persists in per-instance interrupt, GRBM/SQ, SDMA, TCP watch, and debug-control registers when callers apply returned values. This file allocates dump buffers with `kmalloc`, unlike some sibling files that use `kmalloc_objs`.

Dependencies and integration: depends on GC 12.1.0 register headers, `soc_v1_0.h`, XCC instance macros, KFD UAPI trap masks, and AMDGPU SDMA instance topology. Integration is `const struct kfd2kgd_calls gfx_v12_1_kfd2kgd`.

Risks: SDMA offset logic depends on correct `num_inst_per_xcc`; invalid modulo cases call `BUG()`. Address-watch high bits differ from GFX12 (`0x1ffffff` versus `0xffff`), so cross-generation reuse is unsafe. The callback table remains narrow and leaves queue lifecycle callbacks absent. Tests should cover multi-XCC dump instance selection, SDMA engine-to-XCC mapping, 49-bit watch addresses, trap mask round-trips, and NULL callback handling in KFD.
