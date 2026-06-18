# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c

Purpose: this file is the CIK/GFX7 KFD/KGD bridge. It implements queue, SDMA, PASID/VMID, memory, wave-control, scratch backing, VM fault, and VM page-table callbacks for older GFX7 hardware using legacy register names and SRBM selection.

Important APIs and functions: `kgd_program_sh_mem_settings` writes SH memory config, APE1 base/limit, and bases for a VMID. `kgd_set_pasid_vmid_mapping` programs ATC mapping, waits indefinitely for update status, clears it, and mirrors mapping to IH. `kgd_hqd_load` writes CIK MQD registers, enables doorbell control, temporarily releases SRBM selection while reading user WPTR to avoid lock inversion, then marks HQD active. SDMA load/dump/occupancy/destroy operate on `cik_sdma_rlc_registers`. `kgd_hqd_destroy` issues CP dequeue requests with an IQ timer workaround and polls active state. `set_scratch_backing_va`, `set_vm_context_page_table_base`, and `read_vmid_from_vmfault_reg` support KFD memory and fault handling.

Control flow: SRBM selection writes `mmSRBM_GFX_CNTL` under `srbm_mutex`. HQD destroy disables doorbell control, maps KFD drain/reset requests, waits around IQ timer and pending dequeue conditions with IRQs disabled and preemption disabled, writes `CP_HQD_DEQUEUE_REQUEST`, and waits for inactive. SDMA queue load disables RB enable, waits up to two seconds for idle, programs doorbell, RPTR/WPTR, virtual address, ring base, RPTR writeback, and enables RB control.

State and persistence: state lives in legacy CP HQD, SDMA RLC, ATC/IH, SH, VM context, and fault-status registers. MQD SDMA RPTR is saved on destroy. The VM page-table base writes only the low 32 bits to `VM_CONTEXT8_PAGE_TABLE_BASE_ADDR + vmid - 8`.

Dependencies and integration: includes CIK/GFX7, SDMA, OSS, GMC, and CIK structure headers. Integration is `gfx_v7_kfd2kgd`, which lacks modern debug trap callbacks but includes legacy scratch and VM fault support.

Risks: PASID mapping waits without timeout, which can hang on hardware failure. Direct user WPTR read requires careful lock release/reacquire and could race queue state changes. The IQ timer workaround uses IRQ/preemption suppression and fixed retry loops. Test signals include CIK queue load/destroy under memory pressure, SDMA idle timeout, VM fault VMID reporting, scratch backing VA programming, and PASID mapping update-status behavior.
