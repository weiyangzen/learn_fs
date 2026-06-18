# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_3_0_0_offset.h

## Purpose
`vcn_3_0_0_offset.h` is the generated register-offset map for AMD VCN 3.0.0 and its colocated JPEG hardware blocks. It gives C preprocessor names to word offsets inside SOC15 register base tables, so driver code can turn names such as `mmUVD_STATUS`, `mmUVD_RBC_RB_CNTL`, `mmUVD_JRBC_RB_WPTR`, and `mmJPEG_SYS_INT_EN` into concrete MMIO addresses with `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and related helpers.

The file is not an implementation unit. Its purpose is to keep VCN/JPEG driver code independent from raw numeric offsets while still compiling down to the hardware register ABI for VCN 3.0.0 ASICs.

## Important APIs, Types, and Functions
There are no functions, structs, enums, or storage definitions. The public interface is a large set of `#define` macros:

- `mm...` macros define register offsets, for example `mmUVD_STATUS` at `0x0080` in the `uvd0_uvddec` block and `mmUVD_RBC_RB_CNTL` at `0x02de` in the `uvd0_uvd_rbcdec` block.
- Every `mm...` register has a matching `..._BASE_IDX` selector. `BASE_IDX` is significant because SOC15 devices hold multiple base-address tables per hardware IP. This header uses base index `0` for the MMSCH and JPEG-side blocks starting near `0x1e000`, and base index `1` for the VCN decode/power/LMI blocks starting near `0x1f800`.
- `ix...` macros at the end, such as `ixUVD_CGC_MEM_CTRL` and `ixUVD_SW_SCRATCH_00`, define indirect context-register indexes for the `uvdctxind` address space rather than direct MMIO register offsets.

The main direct consumers in this tree are `amdgpu/vcn_v3_0.c` and `amdgpu/jpeg_v3_0.c`, both of which include this header together with `vcn_3_0_0_sh_mask.h`. The offset header provides the register address; the shift/mask header provides field layout for `REG_SET_FIELD()`, `WREG32_P()`, and status-bit tests.

## Register Block Layout
The header is organized by comments naming hardware address blocks and their base addresses. The most important groups are:

- `uvd0_mmsch_dec` at `0x1e000`: MMSCH microcode, SRAM, interrupt, mailbox, GPU IOV scheduling, scratch, VF FIFO, and VM-busy status registers.
- `uvd0_jpegnpdec`, `uvd0_uvd_jpeg_enc_sclk_dec`, `uvd0_uvd_jrbc_dec`, `uvd0_uvd_jrbc_enc_dec`, `uvd0_uvd_jmi_dec`, and JPEG common blocks from `0x1e200` through `0x1e780`: JPEG decode/encode controls, JPEG ring buffer controller registers, JMI/LMI memory interface registers, preemption fence registers, VMID registers, interrupt controls, clock gating, reset, and performance counters.
- `uvd0_uvd_pg_dec` at `0x1f800`: VCN power-gating, dynamic power-gating, harvesting, scratch, firmware version, feature, clock, security, and error/status registers. Notable names include `mmUVD_POWER_STATUS`, `mmCC_UVD_HARVESTING`, `mmUVD_DPG_*`, `mmUVD_FW_VERSION`, and `mmVCN_FEATURES`.
- `uvd0_uvddec` at `0x1fa00`: main VCN decode control and firmware interface registers, including status, soft reset, clock gating, GPCOM firmware mailboxes, interrupts, master interrupt enable, job-done/context registers, multiple encode/decode ring descriptors, and many general-purpose scratch registers.
- `uvd0_ecpudec` at `0x1fd00`: VCPU cache windows, non-cache windows, VCPU control, trace, and indirect-register access.
- `uvd0_uvd_mpcdec`, `uvd0_uvd_rbcdec`, and `uvd0_lmi_adpdec` from `0x20310` through `0x20870`: MPC decode composition registers, the decode ring-buffer controller, semaphores/job-start controls, and a large set of LMI 64-bit BAR, VMID, latency, urgent, swap, prefetch, and memory-interface registers.
- `uvdctxind`: indirect context indexes for clock gating, software scratch, memcheck interrupts, and IH semaphore control.

The numeric gaps are meaningful reserved or unlisted hardware locations. Driver code should not treat the file as a dense register array except where hardware documentation explicitly defines repeated sequences such as ring base/size/pointer groups.

## Control Flow and State
This header has no control flow. Runtime behavior is created by consumers using these names in ordered MMIO sequences.

In `vcn_v3_0.c`, the offsets are used during VCN startup, DPG startup, reset, suspend/resume, idle checks, and MMSCH init-table construction. Typical flows write `mmUVD_STATUS` to mark the block busy, adjust `mmUVD_CGC_*` and `mmUVD_POWER_STATUS`, program VCPU cache windows through `mmUVD_LMI_VCPU_CACHE*_64BIT_BAR_*` plus `mmUVD_VCPU_CACHE_*`, release `mmUVD_VCPU_CNTL`, poll `mmUVD_STATUS`, then configure decode and encode ring registers. The decode ring uses `mmUVD_LMI_RBC_RB_64BIT_BAR_LOW/HIGH`, `mmUVD_RBC_RB_RPTR`, `mmUVD_RBC_RB_WPTR`, `mmUVD_RBC_RB_CNTL`, and `mmUVD_RBC_RB_WPTR_CNTL`. Encode rings use `mmUVD_RB_BASE_*`, `mmUVD_RB_SIZE*`, `mmUVD_RB_RPTR*`, and `mmUVD_RB_WPTR*`.

In `jpeg_v3_0.c`, the JPEG block uses this same offset namespace with the `JPEG` SOC15 IP base. Startup programs tiling with `mmJPEG_DEC_GFX10_ADDR_CONFIG` and `mmJPEG_ENC_GFX10_ADDR_CONFIG`, clears JMI reset through `mmUVD_JMI_CNTL`, enables JRBC interrupts through `mmJPEG_SYS_INT_EN`, and initializes the JPEG ring with `mmUVD_LMI_JRBC_RB_64BIT_BAR_LOW/HIGH`, `mmUVD_JRBC_RB_RPTR`, `mmUVD_JRBC_RB_WPTR`, `mmUVD_JRBC_RB_CNTL`, and `mmUVD_JRBC_RB_SIZE`.

## State and Persistence Behavior
The header itself holds no state and persists no data. Its values are compiled into the driver as constants. The state affected through these constants lives in hardware registers, firmware-visible shared memory, ring buffers, doorbells, and GPU memory BAR windows.

Stateful categories exposed by this map include power-gating state (`mmUVD_PGFSM_*`, `mmUVD_POWER_STATUS`, `mmUVD_DPG_*`), firmware and VCPU boot state (`mmUVD_VCPU_*`, `mmUVD_STATUS`, `mmUVD_FW_VERSION`), command submission state (`mmUVD_RBC_*`, `mmUVD_RB_*`, `mmUVD_JRBC_*`), interrupt state (`mmUVD_*_INT_*`, `mmJPEG_SYS_INT_*`), virtualization state (`mmMMSCH_GPUIOV_*`, `mmUVD_IOV_*`, `mmUVD_JPEG_IOV_*`), memory translation/protection state (`*_VMID`, `*_64BIT_BAR_*`, `mmJPEG_MEMCHECK_*`, `mmUVD_SECURITY_REG_VIO_REPORT`), and diagnostics/performance state (`*_SCRATCH*`, `*_LAT_CNTR`, `*_PERFMON_*`, `mmUVD_TSC_*`).

These register values are generally volatile across GPU reset, power gating, driver unload, and suspend/resume. Consumers reprogram critical registers during hardware initialization and resume, and use readbacks such as `RREG32_SOC15(..., mmUVD_STATUS)` to flush posted writes or poll hardware readiness.

## Dependencies and Integration Points
This header depends on the SOC15 register-access model used by AMDGPU. `SOC15_REG_ENTRY_STR()` stores `reg##_BASE_IDX` and `reg` for register dumps, while `SOC15_REG_OFFSET(ip, inst, reg)` combines the chosen hardware IP, instance, base index, and offset into a final address. The correctness of every macro therefore depends on matching the VCN 3.0.0 base-address tables registered for the device.

Key integration points are:

- `amdgpu/vcn_v3_0.c`: VCN 3.0 decode/encode IP setup, firmware boot, DPG, MMSCH init table generation, idle polling, reset, interrupt routing, and ring pointer access.
- `amdgpu/jpeg_v3_0.c`: JPEG 3.0 ring setup, power/clock gating, interrupt enablement, register dump lists, and JPEG ring read/write pointer operations.
- `vcn_3_0_0_sh_mask.h`: field shifts and masks used with the offsets in this file.
- SOC15 register helpers in `soc15.h` and related AMDGPU MMIO helpers.
- Firmware/shared-memory protocols in VCN startup paths, where register offsets select the hardware windows backing firmware cache, stack, context, and ring state.
- SR-IOV and MMSCH support, where `mmMMSCH_*`, `mmUVD_IOV_*`, and `mmMMSCH_GPUIOV_*` registers mediate mailbox and scheduling state.

## Risks
The main risk is silent misaddressing. A wrong offset or wrong `_BASE_IDX` can still target a valid MMIO location, so failures may look like firmware boot timeouts, stuck ring pointers, lost interrupts, memory faults, hangs during suspend/resume, or corruption in unrelated VCN/JPEG state.

Cross-generation include mistakes are especially dangerous. The same names exist in VCN 1.x, 2.x, 2.5, and 3.0 headers but with different offsets. For example, `mmUVD_STATUS` and `mmUVD_RBC_RB_CNTL` are present across generations, but this file maps them to the VCN 3.0.0 layout. Code compiled with the wrong offset header may build cleanly while programming the wrong hardware registers.

Another risk is confusing direct offsets with indirect indexes. `mm...` symbols are used through SOC15 MMIO helpers, while `ix...` symbols at the end are indexes into an indirect context space. Treating one namespace like the other would address the wrong path.

Because this file is generated-style hardware ABI data, manual edits are high blast radius. Any change must be validated against the ASIC register specification and the paired shift/mask header.

## Test Signals
Useful validation signals include:

- VCN 3.0 driver loads without VCPU boot timeouts and `mmUVD_STATUS` reaches the expected ready/idle values during `vcn_v3_0_start()`.
- Decode ring initialization shows stable `mmUVD_RBC_RB_RPTR`/`mmUVD_RBC_RB_WPTR` behavior, correct `mmUVD_RBC_RB_CNTL` buffer sizing, and successful fence progress on decode jobs.
- Encode ring setup correctly programs `mmUVD_RB_BASE_*`, `mmUVD_RB_SIZE*`, `mmUVD_RB_RPTR*`, and `mmUVD_RB_WPTR*` for all enabled rings.
- JPEG 3.0 initialization can enable `mmJPEG_SYS_INT_EN`, program `mmUVD_JRBC_*` registers, process JPEG jobs, and receive JPEG decode interrupts.
- Suspend/resume, GPU reset, and DPG transitions complete without hangs, with power and clock registers reprogrammed as expected.
- Register dump/debugfs output for VCN/JPEG 3.0 contains addresses matching the `mm...` offsets and their `_BASE_IDX` selections.
- SR-IOV environments exercise MMSCH mailbox/GPUIOV paths without mailbox timeouts or incorrect active-function reporting.
