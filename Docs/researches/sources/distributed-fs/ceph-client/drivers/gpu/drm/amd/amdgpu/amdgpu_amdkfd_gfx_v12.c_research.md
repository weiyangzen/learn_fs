# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12.c

Purpose: this file provides a narrower GFX12 KFD/KGD callback table for SOC24-era devices. It implements interrupt setup, HQD and SDMA register dumps, wave-control execution, per-VMID debug control value generation, trap-mask conversion, address-watch programming, and an SDMA doorbell placeholder.

Important APIs and functions: `init_interrupts_v12` enables timestamp and opcode-error interrupts for a selected MEC pipe. `hqd_dump_v12` dumps 56 compute HQD registers after SRBM queue selection. `hqd_sdma_dump_v12` dumps a compact SDMA queue range from `RB_CNTL` through `CONTEXT_STATUS`. `wave_control_execute_v12` writes `GRBM_GFX_INDEX` and `SQ_CMD` and restores broadcast selection. Debug callbacks return `SPI_GDBG_PER_VMID_CNTL` values with trap enable, exception mask, replacement mode, optional trap-on-start/end bits, and either launch mode or stall mode. `kgd_gfx_v12_set_address_watch` writes TCP watch address high/low registers and returns a valid control value.

Control flow: queue-specific register access is protected by `srbm_mutex` and selected with `soc24_grbm_select`. Dump helpers allocate output arrays, select the queue, read sequential registers, and release the queue. Debug trap override first maps previous hardware control to KFD mask bits, merges requested bits, maps back to hardware fields, and returns the new control value. The callback table omits many older callbacks such as queue load/destroy and VM mapping, suggesting those are supplied elsewhere or unsupported in this table.

State and persistence: this file mostly observes or returns register state rather than owning queue lifecycle. It mutates interrupt registers, `GRBM_GFX_INDEX`, `SQ_CMD`, and TCP watch address registers. Debug state persists wherever the returned per-VMID control values are applied by KFD.

Dependencies and integration: includes GC 12.0.0 register headers, SOC24 GRBM selection, and KFD UAPI trap masks. `gfx_v12_kfd2kgd` is the integration point and sets `get_atc_vmid_pasid_mapping_info = NULL`.

Risks: the reduced callback set means callers must tolerate NULL function pointers for queue lifecycle and VM operations. `BUG()` is used for invalid SDMA engine ids. Address-watch clear and SDMA doorbell reporting are placeholders returning 0. Test signals include callback-table NULL handling, HQD/SDMA dump sizes, trap mask round-trips including wave-start/end, stall launch mode value 4, and TCP watchpoint hits on GFX12.
