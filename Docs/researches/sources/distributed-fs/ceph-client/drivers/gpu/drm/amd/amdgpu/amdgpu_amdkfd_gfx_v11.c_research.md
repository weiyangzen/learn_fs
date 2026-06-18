# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c

Purpose: this file implements the GFX11 KFD/KGD callback table. It updates the GFX10-style queue, SDMA, VM, wave-control, and debug routines for SOC21 register selection and GFX11 register names.

Important APIs and functions: callback implementations include `program_sh_mem_settings_v11`, `set_pasid_vmid_mapping_v11`, `init_interrupts_v11`, `hqd_load_v11`, `hiq_mqd_load_v11`, `hqd_dump_v11`, `hqd_sdma_load_v11`, `hqd_sdma_dump_v11`, occupancy checks, destroy paths, `wave_control_execute_v11`, `set_vm_context_page_table_base_v11`, GFX11 debug trap helpers, trap mask mapping, address-watch setup/clear, and placeholder HQD PQ/reset/doorbell helpers.

Control flow: SRBM selection uses `soc21_grbm_select`. Compute queue load writes `v11_compute_mqd` HQD fields, handles HIQ scheduler1 programming for VMID 0, enables doorbell logic, seeds CP WPTR polling when a user pointer is supplied, starts the EOP fetcher, and marks the queue active. HIQ mapping uses KIQ `PACKET3_MAP_QUEUES`. SDMA queue load/destroy use renamed `SDMA0_QUEUE0_*` registers and two-engine offset selection; invalid engine ids call `BUG()`. Debug trap callbacks return per-VMID control values instead of globally writing `SPI_GDBG_TRAP_MASK`. Trap validation supports FP, integer divide-by-zero, address watch, memory violation, and conditionally wave-start/end trap bits for GC IP >= 11.0.4. Address watch writes TCP watch address registers through RLC writes and returns a valid control value.

State and persistence: state persists in HQD/SDMA registers, IH LUT, GFXHUB page-table registers, SPI per-VMID debug controls, TCP watch registers, and MQD RPTR fields saved on SDMA destroy. The callback table sets `get_atc_vmid_pasid_mapping_info = NULL`, indicating no ATHUB query path here.

Dependencies and integration: depends on GC 11.0.0, OSSSYS 6.0.0, SOC21 GRBM selection, `v11_structs`, KFD UAPI debug masks, KIQ ring infrastructure, and GFXHUB VM functions. Integration is `const struct kfd2kgd_calls gfx_v11_kfd2kgd`.

Risks: `BUG()` on invalid SDMA engine ids is harsher than older warning/fallback behavior. `KFD_PREEMPT_TYPE_WAVEFRONT_SAVE` is not handled in destroy and falls back to drain through default behavior. Address-watch clear returns 0 without writing a clear register. Tests should cover SDMA engine validation, GC 11.0.4+ wave start/end trap support, KIQ HIQ load, compute queue preemption timeouts, and VMID rejection in page-table programming.
