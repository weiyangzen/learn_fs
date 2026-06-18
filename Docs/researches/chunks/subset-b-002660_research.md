# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 27130-29635

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It starts inside the mask definitions for `CGTS_CU14_TCPI_CTRL_REG`, contains complete definitions for many clock-gating, VM, virtualization, microcode, RLC, and GC CAC register groups, and ends inside `GC_CAC_OVRD_TCC` immediately after the `GC_CAC_OVRD_TA` override fields. The range contains 2,152 `#define` macros, including 1,074 `__SHIFT` constants and 1,080 `_MASK` constants, plus register/address-block comment anchors.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bit positions and masks for GC 9.2.1 graphics-core registers used by the AMDGPU kernel driver and Vega12 PowerPlay support. This slice describes fields for shader/graphics clock gating and test overrides, VM and SR-IOV per-VF aperture/ATS controls, privileged command-processor and RLC microcode windows, GPU IOV scheduling/status registers, and graphics-core CAC counters and override selectors.

The file has no executable behavior. Its purpose is to keep C code from embedding raw bit positions when building or decoding hardware register values. Companion offset definitions in `gc_9_2_1_offset.h` provide the matching `mm...` or `ix...` register numbers, and driver code combines those offsets with these masks through SOC15 MMIO helpers, indirect-register helpers, and register-field macros.

## Important API Surface

- `CGTS_CU15_TCPI_CTRL_REG` and the preceding tail of `CGTS_CU14_TCPI_CTRL_REG` define TCPI control, override, busy, load/store, SIMDBUSY, and reserved bits for compute-unit test/clock-control state.
- `CGTT_*_CLK_CTRL`, `CGTX_SPI_DEBUG_CLK_CTRL`, `SQ_*_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_CGTT_CLK_CTRL`, `GRBM_CGTT_CLK_CNTL`, and `GCEA_CGTT_CLK_CTRL` expose clock-gating delay, hysteresis, soft-stall override, core/group override, RAM FGCG, read/write-clock override, and register override fields for most GC sub-blocks.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15` provide per-virtual-function framebuffer size and offset fields. `MC_VM_MARC_BASE_*`, `MC_VM_MARC_RELOC_*`, and `MC_VM_MARC_LEN_*` describe MARC base, relocation, and length windows. `VM_IOMMU_CONTROL_REGISTER`, `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, `VM_PCIE_ATS_CNTL`, and `VM_PCIE_ATS_CNTL_VF_*` define IOMMU and PCIe ATS enable/optimization fields.
- `CP_HYP_*_UCODE_ADDR`, `CP_*_UCODE_DATA`, `CP_ME_RAM_*`, `CP_CE_UCODE_*`, `CP_MEC_ME*_UCODE_*`, and related checksum registers define fields for loading or inspecting PFP, ME, CE, and MEC microcode through hypervisor-visible and normal command-processor windows.
- `GRBM_GFX_INDEX_SR_*`, `GRBM_GFX_CNTL_SR_*`, `GRBM_CAM_*`, and `GRBM_HYP_CAM_*` expose SR selection/data and CAM index/data fields used around graphics register-broadcast, shadowing, or virtualization contexts.
- `RLC_GPU_IOV_*`, `RLC_RLCV_TIMER_*`, `RLC_HYP_SEMAPHORE_*`, `RLC_CLK_CNTL`, and `RLC_GPU_IOV_SDMA*_STATUS/BUSY_STATUS` define SR-IOV scheduling, VF enable/mask, active function, timer interrupt/status, doorbell status/set/clear, scratch, firmware, reset, SDMA, SMU/RLC response, interrupt disable/force, semaphore, and clock-control fields owned by the RLC/virtualization path.
- `GC_CAC_CNTL`, `GC_CAC_OVR_SEL`, `GC_CAC_OVR_VAL`, `GC_CAC_WEIGHT_*`, `GC_CAC_ACC_*`, and `GC_CAC_OVRD_*` define graphics-current/activity counter configuration, per-block signal weights, 32-bit or split 40-bit accumulators, and per-block override select/value fields for BCI, CB, CP, DB, GDS, IA, LDS, PA, PC, SC, SPI, CU, SQ, SX, SXRB, TA, and the beginning of TCC.

There are no C types, functions, structs, or inline helpers in this chunk. The exported interface is the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Control Flow

There is no direct control flow in the header. Runtime consumers follow a consistent pattern:

1. Select a register offset from `gc_9_2_1_offset.h`, such as `mmCGTT_SPI_PS_CLK_CTRL`, `mmMC_VM_FB_SIZE_OFFSET_VF0`, `mmCP_HYP_PFP_UCODE_ADDR`, or indirect CAC offsets such as `ixGC_CAC_CNTL`.
2. Read or compose a 32-bit register value.
3. Clear or test bits with `REGISTER__FIELD_MASK`.
4. Insert or extract field values by shifting with `REGISTER__FIELD__SHIFT`, commonly through `REG_SET_FIELD` and `REG_GET_FIELD`.
5. Write through SOC15 MMIO helpers, command-processor upload paths, PowerPlay/CGS register helpers, or GC CAC indirect-index/data helpers.

The repeated families imply table-driven or indexed consumers: clock-gating setup can walk many `CGTT_*` registers; SR-IOV code can iterate VF-specific `MC_VM_FB_SIZE_OFFSET_VFn` and `VM_PCIE_ATS_CNTL_VF_n` fields; microcode loaders stream words through address/data windows; CAC/powertune code programs selector, weight, accumulator, and override registers through `mmGC_CAC_IND_INDEX`/`mmGC_CAC_IND_DATA`.

## State and Persistence

The macros are stateless compile-time constants, but they describe persistent GPU hardware state. Register values remain in effect until another driver path, firmware sequence, power transition, virtualization event, GPU reset, or context restore rewrites them.

Clock-gating controls affect live power and timing behavior for SPI, PC, BCI, VGT, IA, WD, PA, SC, SQ, SX, TD, TA, TCP, TCI, GDS, DB, CB, TCC, TCA, CP, CPF, CPC, RLC, RMI, SE CAC, GC CAC, GRBM, and EA blocks. VM and IOMMU fields persist as per-function aperture, relocation, MARC, and ATS state. CP and RLC microcode address/data registers are transient access windows but are part of a persistent firmware-load sequence. GC CAC weight, selector, accumulator, and override registers persist as power/activity telemetry and control state used by power-management code.

The AMDGPU SOC15 layer exposes locked GC CAC indirect accessors in `soc15.c` using `mmGC_CAC_IND_INDEX` and `mmGC_CAC_IND_DATA`, so CAC register programming is serialized at the software access point. The masks in this chunk do not provide locking, validation, range checking, or ordering; those responsibilities belong to the callers.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.2.1 register specification and must remain synchronized with `gc_9_2_1_offset.h`, where this range maps to offsets such as `mmCGTS_CU15_TCPI_CTRL_REG`, `mmCGTT_SPI_PS_CLK_CTRL`, `mmMC_VM_FB_SIZE_OFFSET_VF0`, `mmCP_HYP_PFP_UCODE_ADDR`, `ixGC_CAC_CNTL`, and `ixGC_CAC_OVRD_TA`.
- Included by `amdgpu/gfxhub_v1_1.c` for GC 9.2.1 graphics-hub register access and by `pm/powerplay/hwmgr/vega12_inc.h`, which aggregates Vega12 THM, MP, GC, and NBIO generated register headers for power-management code.
- Integrates with SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- CAC registers integrate with indirect access paths in `soc15_gc_cac_rreg()` and `soc15_gc_cac_wreg()` and with PowerPlay/CGS code paths that use `CGS_IND_REG_GC_CAC`.
- VM/IOMMU and per-VF fields integrate with SR-IOV and XGMI/GMC setup code. CP and RLC microcode fields integrate with firmware upload and virtualization sequences in neighboring GFX generations and the same generated register model.

## Risks

- Bitfield drift is the highest risk. If any `__SHIFT` or `_MASK` value diverges from the GC 9.2.1 hardware spec or companion offset header, the driver can silently program the wrong bits.
- The chunk is boundary-partial. It begins after the start of `CGTS_CU14_TCPI_CTRL_REG` and ends before the full `GC_CAC_OVRD_TCC` group, so merge tooling should not treat those two register groups as completely covered here.
- Clock-gating override mistakes can cause power regressions, performance loss, timing-sensitive hangs, or blocks that fail to wake because `SOFT_STALL_OVERRIDE`, `CORE*_OVERRIDE`, `GRP*_OVERRIDE`, `REG_OVERRIDE`, delay, and hysteresis fields are hardware-control bits.
- VM and SR-IOV fields have high isolation risk. Incorrect per-VF framebuffer size/offset, MARC relocation/length, IOMMU, ATS, VF mask, active-function, scheduler, doorbell, or reset fields can break guest isolation, route traffic to the wrong aperture, or cause VM faults.
- Microcode address/data window fields have sequencing risk. Writing the wrong CP/RLC address, checksum, data, or firmware-version field can corrupt firmware loading or leave engines running incompatible code.
- GC CAC weights, accumulators, and overrides affect power telemetry and control decisions. Incorrect selectors or override values can mis-measure block activity, skew power-tuning data, or force activity states that hide real workload behavior.

## Test Signals

- Build coverage: compile AMDGPU with GC 9.2.1/Vega12 support to catch syntax errors, duplicate macros, missing includes, and consumers that expect a different field name.
- Generated-header validation: compare this range against the GC 9.2.1 register source/spec and `gc_9_2_1_offset.h`; verify every field has the intended width, shift, mask, and `mm`/`ix` register pairing.
- Runtime register smoke: boot a Vega12/GC 9.2.1 system, exercise suspend/resume, runtime power management, display plus graphics workloads, and check for GPU hangs, VM faults, bad power-state transitions, or clock-gating warnings.
- Virtualization coverage: on SR-IOV-capable hardware, validate VF framebuffer apertures, ATS/IOMMU behavior, VF scheduling/masks, doorbell status, virtual reset requests, and SDMA busy/status reporting.
- Firmware-path coverage: verify CP/RLC firmware upload, checksum/version programming, and post-load command submission on systems using the hypervisor-visible microcode windows.
- Power/CAC validation: compare GC CAC accumulator readings and Powertune behavior against known-good driver traces, especially `GC_CAC_CNTL`, `GC_CAC_WEIGHT_*`, `GC_CAC_ACC_*`, and `GC_CAC_OVRD_*` accesses through the GC CAC indirect register path.
