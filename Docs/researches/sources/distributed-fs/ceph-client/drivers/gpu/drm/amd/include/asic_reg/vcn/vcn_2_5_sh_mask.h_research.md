# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_5_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003446`: lines 1-2543, `Docs/researches/chunks/subset-b-003446_research.md`
- `subset-b-003447`: lines 2544-3660, `Docs/researches/chunks/subset-b-003447_research.md`

## Chunk Research

### subset-b-003446: lines 1-2543

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_5_sh_mask.h lines 1-2543

## Scope and Purpose

This chunk is the first 2543 lines of the generated AMD VCN 2.5 register shift/mask header. It contains no executable C control flow; its job is to publish bitfield `__SHIFT` and `__MASK` constants used by the amdgpu VCN/JPEG 2.5 driver code when composing, clearing, polling, or decoding memory-mapped hardware registers. In this range there are 2134 `#define` entries spanning 355 register names.

The file is paired with the matching register-address header for VCN 2.5 and is included directly by `amdgpu/vcn_v2_5.c` and `amdgpu/jpeg_v2_5.c`. Those drivers use these constants with MMIO helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and DPG-mode write helpers to manipulate video decode, JPEG decode/encode, interrupt, power, clock-gating, ring-buffer, and MMSCH virtualization registers.

## Address Blocks Covered

- Lines 25-417, `uvd0_mmsch_dec`: MMSCH microcontroller/scheduler masks for ucode and SRAM access, VF context/GPCOM memory windows, mailboxes, interrupts, scratch registers, GPU IOV command/status blocks, VFID FIFOs, and VM busy status.
- Lines 418-581, `uvd0_jpegnpdec`: JPEG decode front-end masks for control, ring buffer base/pointers/size, interrupt enable/status, pitch, GFX8/GFX10 tiling and address config, GPCOM command/data, scratch, and soft reset.
- Lines 582-630, `uvd0_uvd_jpeg_enc_dec`: JPEG encode interrupt, status, engine control, and scratch masks.
- Lines 631-698, `uvd0_uvd_jpeg_enc_sclk_dec`: JPEG encoder SCLK-side status, pitch/base addresses, GFX10 tiling/address config, GPCOM, clock-gating control, scratch, and soft reset.
- Lines 699-816, `uvd0_uvd_jrbc_dec`: JPEG decode ring-buffer controller masks for RB/IB pointers and size, urgent priority, conditional-read timers, status/error bits, preemption command/fence data, and scratch.
- Lines 817-934, `uvd0_uvd_jrbc_enc_dec`: Encoder-side JRBC equivalent of the previous block, including separate `UVD_JRBC_ENC_*` status, timer, preempt, and ring size masks.
- Lines 935-1255, `uvd0_uvd_jmi_dec`: JPEG memory interface and LMI/JMI masks for arbitration wait, burst size, swap mode, VMID assignment, perfmon, 64-bit BAR low/high address halves, preempt fence addresses, and decode/encode swap controls.
- Lines 1256-1341, `uvd0_uvd_jpeg_common_dec`: Common JPEG reset status, system interrupt enable/status/ack, master interrupt enable, IH control, and JRBBM arbitration masks.
- Lines 1342-1460, `uvd0_uvd_jpeg_common_sclk_dec`: JPEG common clock-gating and memory power-management masks, soft reset, and four performance counter banks.
- Lines 1461-1731, `uvd0_uvd_pg_dec`: UVD/JPEG power-gating FSM and status masks, DPG LMA indirect access, DPG pause/ack, scratch registers, VCPU cache BAR/offset/VMID, page-fault status/clear bits, address config, and general-purpose counters.
- Lines 1732-2543, start of `uvd0_uvddec`: Core UVD status/busy, soft reset, MMSCH reset, clock-gating, SUVD clock-gating, GPCOM command/data, VCPU and SYS interrupt enable/status/ack, job/context/ring metadata, multiple ring-buffer base/size/pointer sets, output ring-buffer registers, and the beginning of `UVD_RB_ARB_CTRL`.

## Important Macros and Register Families

The macros follow a stable generated naming contract: `REGISTER__FIELD__SHIFT` gives the field bit offset and `REGISTER__FIELD_MASK` gives the already-positioned bitmask. Driver code typically clears `FIELD_MASK`, then ORs a shifted value such as `value << FIELD__SHIFT`; single-bit control paths often OR or clear only the mask.

Key families in this chunk:

- `MMSCH_UCODE_*`, `MMSCH_SRAM_*`, `MMSCH_CTL`, `MMSCH_CNTL`, and `UVD_MMSCH_SOFT_RESET`: scheduler firmware/SRAM loading, run-stall/reset, clocking, timeout, NACK, and lock fields.
- `MMSCH_VF_*`, `MMSCH_GPUIOV_*`, `MMSCH_VFID_FIFO_*`, `MMSCH_VM_BUSY_STATUS_*`: SR-IOV and virtualization state for VF context buffers, GPCOM buffers, host/VF mailboxes, active function IDs, VM busy maps, and per-scheduler command/status blocks. The generated field names `FUNCTINO_ID` and `NEXT_FUNCTINO_ID` are misspelled in the header and therefore part of the ABI seen by C users.
- `UVD_JPEG_*`, `JPEG_DEC_*`, `UVD_JPEG_ENC_*`, `JPEG_ENC_*`: JPEG decode and encode control, command submission, address layout, pitch/base, soft reset, scratch, and engine idle/status masks.
- `UVD_JRBC_*` and `UVD_JRBC_ENC_*`: JPEG ring-buffer and indirect-buffer command processor controls, including read/write pointers, buffer-valid diagnostics, conditional read retry/timeout fields, illegal-command/memory-timeout/trap/preempt status bits, and preemption fence registers.
- `UVD_JMI_*`, `UVD_LMI_*`: memory-client setup for JPEG decode/encode, VMIDs, 64-bit BAR halves, endian/swap controls, arbitration and burst settings, and perfmon counters.
- `JPEG_SYS_INT_*`, `JPEG_MASTINT_EN`, `JPEG_IH_CTRL`: JPEG interrupt routing, status, acknowledgement, master enable, overrun reset/status, IH VMID/user data/ring ID, and arbitration drop controls. `jpeg_v2_5.c` uses `JPEG_SYS_INT_EN__DJRBC_MASK` for interrupt setup.
- `JPEG_CGC_*`, `JPEG_*_CGC_MEM_CTRL`, `UVD_CGC_*`, `UVD_SUVD_CGC_*`: clock-gating, dynamic clock mode, block active status, and memory light/deep/shutdown controls for JPEG, UVD, and SUVD sub-blocks.
- `UVD_PGFSM_*`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_DPG_*`: power-gating configuration/status, DPG-mode stalling, LMA SRAM indirect access, pause/ack sequencing, and DPG VCPU cache addressing. `vcn_v2_5.c` uses `UVD_POWER_STATUS__*` and `UVD_PGFSM_CONFIG__UVDM_UVDU_PWR_ON` around power transitions.
- `UVD_VCPU_INT_*`, `UVD_SYS_INT_*`, `UVD_MASTINT_EN`, `UVD_GPCOM_*`: firmware/system mailbox commands, interrupt enable/ack/status, interrupt routing, and master interrupt gating.
- `UVD_RB_BASE_*`, `UVD_RB_SIZE*`, `UVD_RB_RPTR*`, `UVD_RB_WPTR*`, `UVD_OUT_RB_*`: decode ring-buffer address and pointer fields, including four input rings and one output ring.

## Control Flow and State Behavior

There are no functions, branches, or data structures in this header. Runtime behavior emerges when the VCN 2.5 and JPEG 2.5 driver code applies these constants to hardware registers:

- Initialization and reset flows write soft-reset masks, clock-gating masks, power-gating FSM fields, and ring-buffer base/size/pointer fields.
- Command-submission flows update RB/IB write pointers and poll status/job-done bits exposed by `UVD_STATUS`, `UVD_JRBC_STATUS`, `UVD_JRBC_ENC_STATUS`, and related interrupt status registers.
- Power-management flows use `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `UVD_PGFSM_CONFIG`, `UVD_PGFSM_STATUS`, `UVD_DPG_PAUSE`, and DPG LMA/cache masks to enter/exit gated modes without racing active engines.
- Virtualization flows use MMSCH VF context address/size/VMID/mailbox fields and GPU IOV command/status fields. In `vcn_v2_5.c`, the driver programs `mmMMSCH_VF_CTX_ADDR_LO/HI`, `mmMMSCH_VF_VMID`, `mmMMSCH_VF_CTX_SIZE`, and mailbox registers using masks from this header.
- Interrupt flows enable, route, read, and acknowledge VCPU, SYS, JPEG SYS, JPEG master, and JPEG encoder interrupts. Incorrect pairing of enable/status/ack masks can leave interrupts stuck or dropped.

The state represented here is exclusively hardware state: MMIO register bits, SRAM indices/data ports, VMID bindings, physical/GPU address halves, ring pointers, busy/status bits, interrupt latches, and power/clock gating state. The header itself persists no state and allocates no memory.

## Dependencies and Integration Points

This header depends on the generated AMD register naming convention and on the companion VCN 2.5 address header (`vcn_2_5_offset.h`) for `mm*` register offsets. It is consumed by amdgpu ASIC-specific implementation files, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c`, which includes the header and uses masks for UVD clock gating, power gating, interrupts, ring arbitration, GPCOM registers, MMSCH initialization, and ring setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c`, which includes the header and uses JPEG interrupt masks such as `JPEG_SYS_INT_EN__DJRBC_MASK`.
- Shared amdgpu MMIO and DPG helpers that expect masks to be already shifted and shifts to be raw bit positions.

The chunk also mirrors many register families present in other VCN generations. That makes it easy to compare with `vcn_4_*_sh_mask.h` or older UVD headers, but values must not be mechanically copied across ASIC generations because field positions and field availability vary.

## Risks and Edge Cases

- This is generated hardware-contract data. A single wrong mask or shift can silently program the wrong bit, causing hangs, power-transition failures, lost interrupts, page faults, or ring-buffer corruption.
- The chunk ends at line 2543 in the middle of `UVD_RB_ARB_CTRL`; later masks for that register are in the next chunk and must be merged before any full-file conclusion about that register.
- Some macro spellings appear generated from hardware descriptions, including `FUNCTINO_ID`. Callers must use the exact generated names; "fixing" the spelling in only one file would break builds.
- Address and size low fields are often aligned, for example ring/JPEG base lows use shifts such as 6 and masks ending in `C0`. Callers must pass appropriately aligned addresses or they will lose low bits.
- Several fields represent write-one-to-clear or acknowledgement semantics (`*_ACK`, `*_CLEAR`, page-fault clear bits, overrun reset). Generic read-modify-write without understanding register semantics can clear pending events.
- Power/clock-gating masks interact with busy/status bits. Clearing clock or power without observing busy/idle fields can strand firmware or engines in reset/gated states.
- VMID and BAR fields split 64-bit addresses and memory-domain identity across multiple registers. Misordered writes or stale high halves can redirect JPEG/JRBC/VCPU memory accesses.

## Test and Validation Signals

Useful validation is mostly build-time and hardware/driver runtime oriented:

- Compile coverage of `vcn_v2_5.c` and `jpeg_v2_5.c` catches missing or renamed macros.
- Static checks should verify each register field has consistent `__SHIFT` and `_MASK` pairs and that masks match the declared bit positions for generated data.
- Runtime smoke signals include successful VCN firmware boot, MMSCH mailbox response becoming nonzero during initialization, ring test jobs completing, JPEG decode/encode job-done interrupts firing and acknowledging, no persistent `*_ILLEGAL_CMD`, `*_MEM_*_TIMEOUT`, NACK, or page-fault status bits, and clean suspend/resume or DPG transitions.
- Power-management validation should poll the relevant `UVD_PGFSM_STATUS`, `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `JPEG_CGC_STATUS`, `UVD_CGC_STATUS`, and `UVD_SUVD_CGC_STATUS` fields before and after gating.
- Interrupt validation should pair enable/status/ack masks for VCPU, SYS, JPEG SYS, and JPEG encoder paths and confirm no overrun bits remain after acknowledgement.

## Unresolved Cross-Chunk References

This report covers only lines 1-2543. The next chunk is required to complete `UVD_RB_ARB_CTRL` and the remainder of the `uvd0_uvddec` block, including any additional ring, decode, memory, semaphore, or firmware interface masks that follow.

### subset-b-003447: lines 2544-3660

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_2_5_sh_mask.h lines 2544-3660

## Scope

This chunk covers the tail of the generated AMDGPU VCN 2.5 shift/mask register header. It starts in the middle of the `UVD_RB_ARB_CTRL` field-mask group, continues through context/scratch registers, VCPU cache and control fields, MPC decode tuning, RBC ring-buffer command processor fields, LMI address/VM/coherency/status/performance fields, MDM DMA and pipeline-busy fields, LMI CRC registers, and ends with VCN/JPEG 2.6.0 RAS poison/status and interrupt enable fields plus the include guard close.

The file is a preprocessor-only hardware-description header. It defines `#define` constants for 32-bit register fields; it does not define C functions, structs, global storage, locks, callbacks, or executable control flow. Runtime behavior is introduced by AMDGPU VCN code that includes this header together with the matching register-address header and passes the masks/shifts to `RREG32*`, `WREG32*`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, and DPG-mode register write helpers.

## Purpose

`vcn_2_5_sh_mask.h` is the bit-layout companion for the VCN 2.5 ASIC register address definitions. The naming convention is consistent throughout this chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit of the field.
- `<REGISTER>__<FIELD>_MASK` gives the masked bit range in the 32-bit register value.

The covered range supplies the field encodings used to bring up and stop the VCN decode engine, program VCPU-visible memory apertures, configure ring-buffer and indirect-buffer submission, control the LMI memory interface, observe media DMA/pipeline idleness, and enable RAS handling on VCN 2.6.0 media IP that shares this header.

## Important Macro Families

### Context, Scratch, Version, and Surface-Like Registers

The chunk begins with the final `UVD_RB_ARB_CTRL` masks: `RBC_DROP`, `RBC_DIS`, `FWOFLD_DROP`, `FWOFLD_DIS`, and `FAST_PATH_EN`. The matching shifts and earlier fields are above the chunk boundary, so this range alone is incomplete for that register.

`UVD_CTX_INDEX` and `UVD_CTX_DATA` describe indexed context access: a 9-bit context index and a full-width data register. `UVD_CXW_WR`, `UVD_CXW_WR_INT_ID`, `UVD_CXW_WR_INT_CTX_ID`, and `UVD_CXW_INT_ID` provide command/status and interrupt ID fields. `UVD_TOP_CTRL` exposes a small codec standard and standard-version selector.

`UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, and `UVD_PICCOUNT` are full-width `DUM` fields, likely legacy or firmware-facing decode parameter registers. `UVD_SCRATCH_NP` and `UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23` are full-width scratch/data registers. `UVD_VERSION` splits minor version at bits 0..15 and major version at bits 16..27.

### VCPU Cache Windows and Core Control

The `uvd0_ecpudec` address block defines VCPU memory-window layout and VCPU control fields:

- `UVD_VCPU_CACHE_OFFSET0` through `_OFFSET8` and matching `UVD_VCPU_CACHE_SIZE0` through `_SIZE8` use 21-bit fields for cache aperture offsets and sizes.
- `UVD_VCPU_NONCACHE_OFFSET0/1` use 25-bit non-cache offsets, with `UVD_VCPU_NONCACHE_SIZE0/1` using 21-bit sizes.
- `UVD_VCPU_CNTL` controls error reporting, PMB/RBBM soft reset, abort request, clock enable, trace enable/mux, JTAG enable, timeout disable, PRB timeout value, and block reset.
- `UVD_VCPU_PRID`, `UVD_VCPU_TRCE`, and `UVD_VCPU_TRCE_RD` expose processor ID and trace/program-counter readback fields.

`vcn_v2_5.c` uses `UVD_VCPU_CNTL__CLK_EN_MASK`, `UVD_VCPU_CNTL__BLK_RST_MASK`, and `UVD_VCPU_CNTL__PRB_TIMEOUT_VAL__SHIFT` during both DPG and non-DPG bring-up. Startup writes enable the VCPU clock, set the PRB timeout, assert/deassert block reset, and then poll decode status. Stop paths assert block reset and clear the clock-enable bit after LMI and engine-idle waits.

### MPC Decode Path

The `uvd0_uvd_mpcdec` block describes motion/picture-cache and memory-pixel-controller behavior:

- `UVD_MP_SWAP_CNTL` gives 16 two-bit memory-swap selectors for reference surfaces `MP_REF0` through `MP_REF15`.
- `UVD_MPC_LUMA_*` and `UVD_MPC_CHROMA_*` registers expose full-width search, hit, and pending-hit counters.
- `UVD_MPC_CNTL` controls replacement mode, performance counter reset, average weight, urgent request enable, SMPAT request speedup, and test mode.
- `UVD_MPC_PITCH` provides an 11-bit luma pitch field.
- `UVD_MPC_SET_MUXA0/A1`, `UVD_MPC_SET_MUXB0/B1`, `UVD_MPC_SET_MUX`, and `UVD_MPC_SET_ALU` define small mux and ALU-selector fields used for MPC setup.
- `UVD_MPC_PERF0` and `UVD_MPC_PERF1` expose maximum and average latency fields.

The VCN 2.5 startup path programs `UVD_MPC_CNTL__REPLACEMENT_MODE__SHIFT` and writes mux values for `UVD_MPC_SET_MUXA0`, `UVD_MPC_SET_MUXB0`, and `UVD_MPC_SET_MUX` before resuming memory-controller state. These constants are therefore part of the normal decode-engine initialization sequence, not just diagnostics.

### RBC Ring Buffer, Semaphores, and Job Start

The `uvd0_uvd_rbcdec` block maps the ring-buffer command processor and synchronization registers:

- `UVD_RBC_IB_SIZE` and `UVD_RBC_IB_SIZE_UPDATE` describe indirect-buffer sizes in bits 4..22.
- `UVD_RBC_RB_CNTL` defines ring buffer size/block size and control bits for no-fetch, write-pointer polling, no-update, and read-pointer writeback.
- `UVD_RBC_RB_RPTR_ADDR`, `UVD_RBC_RB_RPTR`, `UVD_RBC_RB_WPTR`, `UVD_RBC_WPTR_STATUS`, `UVD_RBC_WPTR_POLL_CNTL`, and `UVD_RBC_WPTR_POLL_ADDR` define ring read/write pointer state, polling cadence, and polling address.
- `UVD_RBC_VCPU_ACCESS` has an `ENABLE_RBC` bit controlling VCPU access to the RBC path.
- `UVD_RBC_READ_REQ_URGENT_CNTL` controls command-read priority marking.
- `UVD_SEMA_CMD`, `UVD_SEMA_ADDR_LOW`, `UVD_SEMA_ADDR_HIGH`, `UVD_SEMA_CNTL`, and the three semaphore timeout-control/status registers define semaphore request, VMID, address, enable, timeout count, resend timer, and timeout-clear fields.
- `UVD_ENGINE_CNTL` starts the engine and selects start mode, with an additional `NJ_PF_HANDLE_DISABLE` bit.
- `UVD_JOB_START` exposes a one-bit job-start trigger.
- `UVD_RBC_BUF_STATUS` exposes validity and read/write addresses for RB and IB internal buffers.

These fields are integration points for VCN ring submission and scheduler bring-up. Incorrect `RB_NO_FETCH`, pointer, size, or polling encodings can leave the ring unfetchable, desynchronize host and hardware pointers, or make the engine read stale commands. Semaphore fields are similarly sensitive because they can participate in GPU-visible synchronization and VMID-qualified waits/signals.

### LMI Memory Interface and VMID Mapping

The `uvd0_lmi_adpdec` block is the largest part of the chunk. It maps host memory bases, VMIDs, arbitration, coherency, urgent/stall control, performance counters, and clean/idle status:

- `UVD_LMI_RBC_RB_64BIT_BAR_*`, `UVD_LMI_RBC_IB_64BIT_BAR_*`, `UVD_LMI_LBSI_64BIT_BAR_*`, `UVD_LMI_VCPU_NC0/NC1_64BIT_BAR_*`, `UVD_LMI_VCPU_CACHE_64BIT_BAR_*`, `UVD_LMI_VCPU_CACHE1` through `_CACHE8_64BIT_BAR_*`, and `UVD_LMI_MMSCH_NC0` through `_NC7_64BIT_BAR_*` provide low/high halves of 64-bit base addresses.
- `UVD_LMI_MMSCH_NC_VMID`, `UVD_LMI_VCPU_CACHE_VMIDS_MULTI`, `UVD_LMI_VCPU_NC_VMIDS_MULTI`, `UVD_LMI_VCPU_CACHE_VMID`, `UVD_LMI_RBC_RB_VMID`, and `UVD_LMI_RBC_IB_VMID` pack 4-bit VMIDs for multiple memory windows.
- `UVD_LMI_MMSCH_CTRL` controls MMSCH coherency, VM enable, read/write memory swap, read/write request policy, and drop behavior.
- `UVD_LMI_ARB_CTRL2` controls CENC and atomic wait enable/max burst plus MIF read/write return maxima.
- `UVD_LMI_LAT_CTRL`, `UVD_LMI_LAT_CNTR`, and `UVD_LMI_AVG_LAT_CNTR` expose latency performance-measurement controls and counters.
- `UVD_LMI_SPH` exposes an address/status path with valid and overflow bits.
- `UVD_LMI_CTRL2` controls SPH disable, LMI/UMC arbitration stalls, UMC urgent controls, CRC1 reset/select, memory ID selection, non-cache extension enables, SPU extra CID, RE offload, backpressure clear, and non-JPEG MIF gating.
- `UVD_LMI_URGENT_CTRL` gives separate MC and UMC read/write urgent-stall enables and assert fields.
- `UVD_LMI_CTRL` controls write-clean timer, request mode, MC urgent mask/assert, data coherency, CRC reset/select, VCPU/CM/DB/IT/MIF coherency, outstanding-read throttling, and reserved bits.
- `UVD_LMI_STATUS` exposes clean/idleness signals for VCPU/LMI, MC/UMC reads and writes, pending writes, UMC UVD/AVP idle, adapter clean state, BSP write clean state, and CENC read clean.
- `UVD_LMI_PERFMON_CTRL`, `UVD_LMI_PERFMON_COUNT_LO`, `UVD_LMI_PERFMON_COUNT_HI`, and `UVD_LMI_MC_CREDITS` expose performance-monitor state/select/count and memory-controller credit fields.

`vcn_v2_5.c` directly uses `UVD_LMI_CTRL` fields during start to enable write-clean timer behavior, request mode, CRC reset, MC urgent masking, and data/VCPU coherency. It uses `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK` to unblock the UMC channel during start and to block it during stop. Stop logic waits on `UVD_LMI_STATUS__VCPU_LMI_WRITE_CLEAN_MASK`, `READ_CLEAN`, `WRITE_CLEAN`, `WRITE_CLEAN_RAW`, then waits on `UMC_READ_CLEAN_RAW` and `UMC_WRITE_CLEAN_RAW` after stalling UMC arbitration. These masks are therefore part of the shutdown ordering guarantee that outstanding media reads/writes are drained before VCPU reset and clock disable.

### MDM DMA and Pipeline Busy State

The `uvd0_uvdnpdec` block describes non-pipe or media data-mover status:

- `MDM_DMA_CMD` is a full-width command register.
- `MDM_DMA_STATUS` has busy bits for SDB/SCM/RB/SCLR DMA read/write activity.
- `MDM_DMA_CTL` controls MDM bypass, four-command mode, encode mode, VP9 decode mode, and software data reset.
- `MDM_ENC_PIPE_BUSY` exposes busy bits for IME, SMP, SIT, SDB, entropy/header, LCM, MDM read/write paths, EFC, MIF current/reference/general/BSP paths, and multiple BSD readers.
- `MDM_WIG_PIPE_BUSY` exposes a similar busy map for the WIG path, including TBE, entropy/header FIFO, LCM, MDM/MIF paths, additional BSD reader, extra BSP writers, and LCM BSP-not-empty state.

These are mostly observability and low-level mode-control definitions. They are useful for diagnostics, hang analysis, firmware-assisted waits, or power-management code that must prove encode/decode subpipes are idle before gating clocks or resetting media datapaths.

### LMI CRC and VCN/JPEG 2.6 RAS

The `lmi_adp_indirect` block defines `UVD_LMI_CRC0` through `UVD_LMI_CRC3`, each as a full-width CRC32 field. These are diagnostic or validation counters for LMI traffic.

The last section is explicitly labeled VCN/JPEG 2.6.0 even though it lives in the VCN 2.5 header:

- `UVD_RAS_VCPU_VCODEC_STATUS`, `UVD_RAS_MMSCH_FATAL_ERROR`, `UVD_RAS_JPEG0_STATUS`, and `UVD_RAS_JPEG1_STATUS` split poison reporting into `POISONED_VF` bits 0..30 and `POISONED_PF` bit 31.
- `VCN_RAS_CNTL` enables VCPU/VCODEC and MMSCH interrupt/PMI paths, rearms them, controls VCPU/VCODEC stall-on-error, and exposes ready bits.
- `UVD_VCPU_INT_EN__RASCNTL_VCPU_VCODEC_EN_MASK` and `UVD_SYS_INT_EN__RASCNTL_VCPU_VCODEC_EN_MASK` enable RAS interrupt propagation through VCPU and system interrupt paths.

`vcn_v2_5.c` uses these 2.6.0 masks in `vcn_v2_6_enable_ras()`, guarded by `amdgpu_ip_version(adev, UVD_HWIP, 0) == IP_VERSION(2, 6, 0)`. That routine writes `VCN_RAS_CNTL` with VCPU/VCODEC rearm, IH enable, PMI enable, and stall enable, then enables the corresponding VCPU and SYS interrupt bits through DPG-mode register writes. The 2.6.0 labels are therefore intentional compatibility support rather than dead generated output.

## Control Flow and State Behavior

There is no local control flow in this header. The constants influence control flow only through external code that reads, writes, and polls hardware registers.

The effective runtime sequences represented by this chunk include:

- VCN start: enable VCPU clock/reset controls with `UVD_VCPU_CNTL`, program LMI coherency and urgent behavior through `UVD_LMI_CTRL`, configure MPC replacement/mux state, resume memory-controller mappings, unblock UMC arbitration through `UVD_LMI_CTRL2`, unblock VCPU register access via `UVD_RB_ARB_CTRL`, deassert VCPU reset, and poll decode responsiveness.
- VCN DPG start: use DPG-mode register writes for the same VCPU, LMI, and MPC setup while the dynamic power-gating SRAM path may be active.
- VCN stop: wait for VCN idle, wait for LMI clean status, stall UMC arbitration, wait for UMC raw clean status, block VCPU register access, assert VCPU reset, disable VCPU clock, clear status, and re-enable clock gating.
- RAS enable on VCN 2.6.0: write `VCN_RAS_CNTL`, `UVD_VCPU_INT_EN`, and `UVD_SYS_INT_EN` to arm poison/error signaling for VCPU/VCODEC and related media blocks.

Hardware state described by this chunk persists in device registers until reset, power-gating loss, firmware reinitialization, or explicit reprogramming. The header itself has no persistence. Configuration state includes BAR base addresses, VMID assignments, LMI coherency/arbitration policy, RBC ring controls, MPC control/mux settings, DMA mode bits, and RAS interrupt enables. Status state includes VCPU trace/readback, ring-buffer validity and pointers, semaphore timeout bits, LMI clean/idle/performance counters, MDM busy state, CRC values, and RAS poisoned-PF/VF flags.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header ecosystem:

- The matching VCN 2.5 address header supplies register addresses such as `mmUVD_VCPU_CNTL`, `mmUVD_LMI_CTRL`, `mmUVD_LMI_STATUS`, `mmUVD_RBC_RB_CNTL`, and `mmVCN_RAS_CNTL`.
- AMDGPU SOC15 register helpers supply instance-aware MMIO access and DPG-mode access: `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `WREG32_SOC15_DPG_MODE`, `SOC15_REG_OFFSET`, `SOC15_DPG_MODE_OFFSET`, and `SOC15_WAIT_ON_RREG`.
- VCN runtime code in `drivers/gpu/drm/amd/amdgpu/vcn_v2_5.c` is the closest consumer for this ASIC generation. Adjacent VCN/UVD generation files reuse similarly named fields, so names can appear across multiple generated headers.
- Firmware/shared-memory setup code interacts indirectly with VCPU cache/non-cache offset and size windows, LMI BAR base registers, and VMID mapping fields.
- Ring scheduling and command submission code depends on RBC ring-buffer size, pointer, no-fetch/no-update, polling, IB, semaphore, engine-start, and job-start fields.
- RAS handling integrates with AMDGPU interrupt handling through `VCN_RAS_CNTL`, VCPU interrupt enable, SYS interrupt enable, and poisoned PF/VF status masks.

## Risks

- Chunk-boundary risk: line 2544 starts after the `UVD_RB_ARB_CTRL` field shifts and earlier masks. A reader must reconcile with the previous chunk for the complete register definition.
- Generated-header drift: the VCN 2.5 and 2.6.0 field layouts are ASIC-specific. Reusing constants from VCN 2.0, 3.x, or later headers can compile while programming the wrong bits.
- RAS version risk: the tail section contains VCN/JPEG 2.6.0 definitions inside this VCN 2.5 header. Callers must retain the runtime IP-version guard used by `vcn_v2_6_enable_ras()` or risk enabling unsupported interrupt/status bits.
- Reset/clock sequencing risk: wrong `UVD_VCPU_CNTL` masks can leave the VCPU in reset, start it without a clock, disable timeout behavior unexpectedly, or reset it while active.
- Memory-drain risk: stop/shutdown correctness depends on the exact `UVD_LMI_STATUS` clean bits and `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK`. Bad masks can reset or power-gate VCN while MC/UMC writes are still pending.
- Coherency risk: `UVD_LMI_CTRL` and `UVD_LMI_MMSCH_CTRL` encode data coherency, VM, swap, and urgent/drop policy. Incorrect writes can corrupt firmware-visible memory, ring buffers, or decoded surfaces.
- Ring-buffer risk: incorrect RBC buffer sizes, pointer masks, poll address alignment, or no-fetch/no-update bits can deadlock command submission or make hardware fetch from the wrong memory.
- VMID/address risk: LMI BAR low/high and packed VMID fields control GPU virtual-memory attribution for multiple VCPU, RBC, MMSCH, cache, and non-cache windows. Bitfield mistakes can cause accesses in the wrong VM context.
- Busy/status interpretation risk: MDM and LMI status bits may be sticky, sampled, or hardware-cleared according to ASIC rules not encoded in this header. Polling code needs hardware-documented timeout and clear semantics.

## Test Signals

Useful validation signals for changes touching consumers of this chunk include:

- Build coverage for AMDGPU with VCN 2.5/2.6 headers included, catching misspelled generated symbols and wrong header selection.
- VCN firmware bring-up logs showing successful decode engine response after `UVD_VCPU_CNTL` clock/reset sequencing.
- Ring tests or media decode submissions that advance RBC read/write pointers and complete jobs without ring timeout.
- Suspend, runtime power-management, and module unload paths that execute VCN stop and do not timeout on `UVD_LMI_STATUS` clean waits.
- DPG-mode testing, because several writes are routed through `WREG32_SOC15_DPG_MODE` and can diverge from normal MMIO paths.
- RAS injection or poison-status tests on IP version 2.6.0, verifying `VCN_RAS_CNTL`, VCPU interrupt, SYS interrupt, and poisoned PF/VF status handling.
- Hang/debug captures that correlate MDM busy bits, LMI CRC/perf counters, and LMI clean status with expected media workload state.
