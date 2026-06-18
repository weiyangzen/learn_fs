# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 9916-11685

## Scope

This chunk is the final slice of the generated AMDGPU GC 11.0.0 register-offset header. It contains C preprocessor constants only. Each `reg*` symbol gives a SOC15 GC register offset and is usually followed by a matching `<name>_BASE_IDX` constant; each `ix*` symbol gives an indexed-register address used through an indirect register aperture rather than direct MMIO.

The range starts at `regRLC_SERDES_RD_INDEX` and runs through the closing include guard. It covers the latter part of the RLC direct register map, dedicated RLC sub-blocks, PF/VF RLC virtualization controls, power/hypervisor/PSP-facing GC blocks, the GFX IMU register map, and indexed CAC/RTAVFS/SQ wave debug spaces.

## Purpose

The purpose of this header slice is to publish ASIC-specific register addresses for GC 11.0.0-family AMD GPUs. Driver code includes this file instead of hard-coding numeric offsets when it initializes graphics firmware, uploads RLC and IMU microcode, reads shader wave state, configures low-level power/clock/debug features, and accesses indirect counter/control spaces.

This is source-level hardware interface data, not executable logic. The names are the API. Consumers such as `gfx_v11_0.c`, `imu_v11_0.c`, `mes_v11_0.c`, KFD v11 code, SDMA v6 code, display code, and SOC21 setup include `gc/gc_11_0_0_offset.h` and pass these macros to AMDGPU register helpers including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, and `WREG32`.

## Register Families Covered

The first part continues the main RLC direct-register block. It includes `regRLC_SERDES_*` read/control/data/busy registers; `regRLC_GPM_GENERAL_0..16`; static power-gating and delay/status registers; GPM interrupt disable/force/stat registers; SRM control, command status, indexed address/data windows, and status registers; UTCL1 control/status/error registers for SPM/GPM threads; 3D clock-gating/ramp controls; RLC semaphores; PACE interrupt/timer controls; RLCV doorbell range/control/status and per-doorbell data registers; shader profiling controls/status; SMU message/argument/response registers; RLC GPM/CPM/IMU bootload registers; and `regRLC_GPM_UCODE_ADDR`/`regRLC_GPM_UCODE_DATA` for RLCG firmware upload.

The `gc_rlcsdec` block starts at line 10346 and exposes RLC secure/save-restore style controls. It includes RLCS decoder start/dump registers, exception registers, CGCG and deep-sleep controls, duplicated `regRLC_GPM_STAT`/`regRLC_RLCS_GPM_STAT` aliases at the same offset, IOV and VM busy status, GRBM soft reset, power-gating change status/readback, interrupt and semaphore surfaces, WGP status/readback, CP/SPM interrupt info, bootload status and ID status, power-brake controls, idle/busy status, general and auxiliary registers, SPM/SQTT mode, source-ID controls, GCR data/status, UTCL2 controls, secure-mode controls, FED status registers, and debug/value-stable status surfaces.

The `gc_pfvfdec_rlc` block provides PF/VF RLC virtualization doorbell and interrupt-window registers such as `regRLC_PF_VF_INT_STATUS`, `regRLC_VF_DOORBELL_START`, `regRLC_VF_DOORBELL_STATUS`, and related enable/status fields. These offsets are relevant to SR-IOV and virtual function command/doorbell routing.

The `gc_pwrdec`, `gc_hypdec`, and `gc_pspdec` blocks expose GC power control, hypervisor, and PSP-facing registers. They include power-brake controls and thermal-reset delay, CGTT controls/status/debug, hypervisor PM status and intruder/debug placeholders, PSP debug and mailbox registers for CPC/CPG/RLC, command-response/status data, secure-event queue ring base/size/read/write pointers, and PSP ring entry registers.

The `gc_gfx_imu_gfx_imudec` and `gc_gfx_imu_gfx_imu_pspdec` blocks map the GFX IMU. They include IMU version/status/scratch registers, core and reset controls, C2PMSG/P2CMSG message windows, access controls, RAM index/address/data windows, interrupt/status fields, DFT/BIST controls, GFX scheduler control, bootloader address/size registers, D/I RAM address/data apertures, and PSP-loaded RLC bootloader registers. `imu_v11_0.c` directly uses many of these offsets while loading IMU IRAM/DRAM and starting the IMU core.

The indexed `gccacind` block defines GC CAC indirect addresses. It starts with `ixGC_CAC_ID` and `ixGC_CAC_CNTL`, then lists accumulator indexes for CP, EA, UTCL2 router/VML/walker, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC, followed by release/stall/power-brake lookup tables, fixed-pattern performance counters, and `ixHW_LUT_UPDATE_STATUS`. These values are used through the GC CAC indirect index/data aperture rather than direct SOC15 register offsets.

The `secacind` block contains the SE CAC ID/control indexed registers. The `grtavfsind` block defines a linear indexed RTAVFS register bank, `ixRTAVFS_REG0` through `ixRTAVFS_REG194`. The `sqind` block defines SQ indirect wave/debug registers including local debug status/control, wave active/valid/mode/status/trap status, PC, GPR/LDS allocation, IB status/debug, scratch, HW IDs, scheduler mode, shader cycles, temporary registers `ixSQ_WAVE_TTMP0..15` with `TTMP2` absent in this slice, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_EXEC_LO/HI`.

## Important APIs, Types, and Macros

This file defines no C functions, structs, enums, or variables. Its important API surface is the macro convention:

- `regNAME` is a direct GC register offset consumed by SOC15 helpers.
- `regNAME_BASE_IDX` selects the register base index for SOC15 address calculation. In this chunk the main late-RLC, RLCS, PF/VF, power, hypervisor, PSP, and IMU direct registers use base index `1`.
- `ixNAME` is an indexed register number for an indirect aperture such as GC CAC, RTAVFS, or SQ wave debug.
- Address-block comments, for example `// addressBlock: gc_rlcsdec` and `// base address: 0x3b980`, preserve generated hardware grouping and help reviewers compare the output to AMD register databases.

The downstream helper contract is compile-time name stability. For example, `gfx_v11_0_load_rlcg_microcode()` writes `regRLC_GPM_UCODE_ADDR` and `regRLC_GPM_UCODE_DATA` through `WREG32_SOC15`; `imu_v11_0_load_microcode()` writes `regGFX_IMU_I_RAM_ADDR`, `regGFX_IMU_I_RAM_DATA`, `regGFX_IMU_D_RAM_ADDR`, and `regGFX_IMU_D_RAM_DATA`; and `gfx_v11_0_read_wave_data()` reads SQ wave state by passing `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI` to an SQ indirect read helper.

## Control Flow

There is no control flow inside this header. It influences control flow at inclusion sites:

- During graphics initialization, `gfx_v11_0.c` enables and monitors RLC/RLCS state, uploads RLCG microcode through the GPM ucode address/data registers, configures SRM with `regRLC_SRM_CNTL`, and waits for RLCS bootload completion through `regRLC_RLCS_BOOTLOAD_STATUS` or ASIC-specific aliases.
- During IMU initialization, `imu_v11_0.c` requests IMU firmware, writes IMU IRAM and DRAM through the IMU address/data windows, sets debug and scratch controls, releases core reset, waits on `regGFX_IMU_GFX_RESET_CTRL`, and writes RLC RAM golden values through the IMU RLC RAM aperture.
- During shader debugging and GPU reset diagnostics, GFX code selects SQ indirect indexes and reads wave registers from the `sqind` space. The values collected from `ixSQ_WAVE_*` form the wave dump returned to higher-level debug paths.
- During indirect CAC access, generic AMDGPU helpers write an index register such as `mmGC_CAC_IND_INDEX` and read or write `mmGC_CAC_IND_DATA`; this chunk supplies the `ixGC_CAC_*` payload indexes for those transactions.
- During virtualization and PSP-mediated flows, PF/VF RLC and PSP mailbox/ring offsets provide the register endpoints for command status, doorbells, secure events, and firmware handoff.

## State and Persistence

The macros are compile-time constants and hold no state. The registers they name are volatile GPU hardware state. Many are reset by GPU reset, power transitions, or firmware ownership changes and then reprogrammed during probe, resume, or reset recovery.

Some register writes create persistent device state for the current hardware session. RLC and IMU firmware upload registers persist loaded microcode in hardware RAM or firmware-owned memory until reset or reload. IMU scratch, access-control, RAM-valid, and core-control registers affect whether the IMU can start and whether later power-management handoff works. RLC SRM, GPM, PACE, SMU, doorbell, and profiling controls can affect ongoing power, interrupt, save/restore, and debug behavior until overwritten.

Some registers are status or latch surfaces. RLCS exception, bootload, FED status, GCR, UTCL1/UTCL2 error, idle/busy, PF/VF interrupt status, PSP command/status, CAC accumulator, RTAVFS, and SQ wave registers expose transient hardware state. Reads can be used for diagnostics or polling, and some associated control/status bits may clear only through specific hardware-defined write sequences described outside this offset header.

## Dependencies and Integration Points

This chunk depends on the rest of the generated AMD ASIC register header set. The matching `gc_11_0_0_sh_mask.h` supplies bit masks and shifts for many of the same register names, while other offset/default headers cover neighboring blocks and reset defaults. The AMDGPU SOC15 register layer combines HWIP, instance, base index, and these offsets to form MMIO addresses.

Important integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`, which includes this header and uses RLC/RLCS, SQ indirect, and IMU bootloader offsets during graphics initialization, firmware upload, and wave dumps.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c` and `imu_v11_0_3.c`, which include this header and program IMU RAM, reset, scratch, C2PMSG, and RLC RAM windows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_reg_access.c`, `amdgpu.h`, and `amdgpu_cgs.c`, which provide generic indirect GC CAC read/write plumbing used by `ixGC_CAC_*` style indexes.
- KFD and MES v11 components, which include the same GC 11 header to program queueing, dispatch, and scheduling-facing registers elsewhere in the file.
- PSP and firmware-loading paths, where PSP mailbox/ring offsets and RLC/IMU bootloader offsets connect kernel-side firmware blobs to hardware-side command processors.

## Risks

The dominant risk is silent hardware misaddressing. These constants compile to integers, so an incorrect offset or base index can build cleanly while writes hit the wrong register or reads poll an unrelated status bit. For initialization paths this can surface as GPU probe failure, firmware load timeout, failed resume, reset loops, or hangs under graphics/compute load.

High-risk direct registers in this chunk include `regRLC_GPM_UCODE_ADDR`/`DATA`, RLC SRM controls, RLCS bootload/status/FED/error registers, PF/VF doorbell and interrupt registers, PSP mailbox/ring entries, and IMU RAM/control/reset registers. Misprogramming these can break firmware upload, interrupt routing, virtualization isolation, PSP handoff, or IMU-managed power states.

High-risk indexed registers include `ixSQ_WAVE_*`, because debug and reset diagnostics depend on exact SQ indirect addresses; `ixGC_CAC_*`, because indirect CAC access can affect accumulator/counter and power-control lookup state; and `ixRTAVFS_REG*`, because the names are generic numeric slots with little semantic redundancy, making off-by-one errors hard to detect by review.

Because this file is generated from hardware definitions, manual edits are risky. Any change should be checked against the matching generated sh-mask/default headers and the driver code that uses the affected macro names. Apparently unused definitions may still be consumed by out-of-tree diagnostics, firmware tables, register dump tooling, or later ASIC-specific workarounds.

## Test Signals

Compile-time signals include successful AMDGPU builds for GC 11 paths. Renamed or deleted macros used by `gfx_v11_0.c`, `imu_v11_0.c`, KFD v11, MES v11, display, or SDMA v6 code should fail at compile time. Numeric drift, however, usually requires hardware validation.

Runtime signals include successful probe of GC 11.0.0-family devices, successful RLC and IMU firmware loading, no `BOOTLOAD_COMPLETE` timeout while polling RLCS boot status, clean suspend/resume and GPU reset recovery, working GFXOFF/power-management transitions, and stable graphics/compute workloads after initialization.

Diagnostic signals include sane SQ wave dumps using `ixSQ_WAVE_*`, correct IMU firmware version reporting and reset completion, absence of unexpected RLCS FED or UTCL error status, correct PSP mailbox/ring command progress, and consistent CAC/RTAVFS indirect register reads where supported by hardware and firmware state. Virtualization-specific validation should include PF/VF interrupt and doorbell behavior when SR-IOV paths are enabled.
