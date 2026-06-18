# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c

Purpose: this file adapts the GFX10 KFD/KGD bridge for GFX10.3 ASICs. It reuses base GFX10 debug/watch/IQ helpers but supplies generation-specific queue programming, PASID-to-IH mapping for devices where ATC is defeatured, SDMA register offsets for up to four engines, and trap handler setup.

Important APIs and functions: `program_sh_mem_settings_v10_3`, `set_pasid_vmid_mapping_v10_3`, `init_interrupts_v10_3`, `hqd_load_v10_3`, `hiq_mqd_load_v10_3`, `hqd_dump_v10_3`, `hqd_sdma_load_v10_3`, `hqd_sdma_dump_v10_3`, `hqd_is_occupied_v10_3`, `hqd_sdma_is_occupied_v10_3`, `hqd_destroy_v10_3`, `hqd_sdma_destroy_v10_3`, `wave_control_execute_v10_3`, `get_atc_vmid_pasid_mapping_info_v10_3`, `set_vm_context_page_table_base_v10_3`, and `program_trap_handler_settings_v10_3` are bound into `gfx_v10_3_kfd2kgd`.

Control flow: compute load mirrors base GFX10 but also programs `RLC_CP_SCHEDULERS.scheduler1` for HIQ queues with VMID 0. HIQ load submits `PACKET3_MAP_QUEUES` through KIQ. PASID mapping writes only `IH_VMID_0_LUT` because the comment states ATC is defeatured on Sienna Cichlid. SDMA load/destroy use GFX10 register names with engine base selected by a switch over engines 0-3. Queue destroy maps KFD drain/reset/save requests to CP dequeue request values and polls `CP_HQD_ACTIVE`. Trap handler setup writes TBA/TMA registers with `TRAP_EN` set in `SQ_SHADER_TBA_HI`.

State and persistence: persistent state is in SRBM-selected HQD registers, SDMA queue registers, IH LUT, GFXHUB VM PT registers, shader trap handler registers, and KIQ ring packets. SDMA destroy copies RPTR back into the MQD. Debug and address-watch state is delegated to shared GFX10 helpers.

Dependencies and integration: includes GFX10.3 GC, OSSSYS 5.0.0, ATHUB 2.1.0, `v10_structs`, `nv/nvd`, and `amdgpu_amdkfd_gfx_v10.h`. The callback table is the integration boundary with KFD.

Risks: the ATC-defeatured mapping means code expecting `get_atc_vmid_pasid_mapping_info_v10_3` to observe mappings can see stale or absent ATHUB state. Invalid SDMA engine ids fall through to engine 0 after warning. Queue WPTR guessing has the same wrap assumption as GFX9/10. Test signals include IH-only PASID mapping, HIQ scheduler1 setup/clear, KIQ map queue packet emission, SDMA queue lifecycle on engines 0-3, and shared GFX10 debugger/watchpoint behavior on GFX10.3 hardware.
