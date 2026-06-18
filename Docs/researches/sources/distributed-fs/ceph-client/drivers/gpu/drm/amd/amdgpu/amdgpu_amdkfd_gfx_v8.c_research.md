# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c

Purpose: this file implements the VI/GFX8 KFD/KGD bridge. It is structurally close to GFX7 but adds GFX8 MQD layout support, HIQ scheduler programming, Tonga-specific EOP handling, larger SDMA dump coverage, and VI-specific register constants.

Important APIs and functions: `kgd_program_sh_mem_settings`, `kgd_set_pasid_vmid_mapping`, `kgd_init_interrupts`, compute `kgd_hqd_load/dump/is_occupied/destroy`, SDMA `kgd_hqd_sdma_load/dump/is_occupied/destroy`, `get_atc_vmid_pasid_mapping_info`, `kgd_wave_control_execute`, `set_scratch_backing_va`, and `set_vm_context_page_table_base` populate `gfx_v8_kfd2kgd`. `get_sdma_rlc_reg_offset` uses `SDMA1_REGISTER_OFFSET` and `KFD_VI_SDMA_QUEUE_OFFSET`.

Control flow: compute HQD load selects the queue, programs scheduler1 for HIQ if VMID is 0, writes MQD/HQD fields, skips EOP RPTR/WPTR writes on Tonga as an erratum, enables doorbell, releases SRBM while reading user WPTR, reacquires and writes WPTR if valid, then activates the HQD. Destroy clears HIQ scheduler1 when applicable, runs the same IQ timer/dequeue-pending workaround as GFX7, sends a dequeue request, and waits for inactive. SDMA load/destroy follow disable-wait-program-enable and save RPTR.

State and persistence: persistent state includes SRBM-selected HQD registers, `RLC_CP_SCHEDULERS.scheduler1`, SDMA RLC registers, ATC/IH mappings, scratch backing VA, and VM context page-table base. SDMA RPTR is saved back into the MQD.

Dependencies and integration: depends on GFX8, OSS 3.0, GMC 8.1, VI structures, and ASIC id definitions. Integration is `const struct kfd2kgd_calls gfx_v8_kfd2kgd`.

Risks: PASID mapping has no timeout. Tonga EOP handling is special and must not be removed without context-save validation. Like GFX7, the HQD destroy workaround blocks IRQ/preemption briefly and relies on fixed retry limits. Test signals include Tonga and non-Tonga HQD load, HIQ scheduler1 setup/clear, SDMA queue lifecycle, PASID update-status completion, and scratch/VM page-table programming on KFD VMIDs only.
