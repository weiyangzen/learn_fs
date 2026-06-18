# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vpe/vpe_6_1_0_offset.h

## Purpose
This generated AMDGPU register-offset header names the VPE 6.1.0 register map. It does not implement executable logic; it provides preprocessor constants that the driver can combine with an IP instance base address to read and write VPE hardware registers. The file is guarded by `_vpe_6_1_0_OFFSET_HEADER` and consists almost entirely of `reg...` offset macros plus matching `..._BASE_IDX` macros, all currently `0`.

The first and largest section describes the VPE command processor/decoder block, `vpe_vpedec`, whose block comment gives base address `0x46000`. Later sections describe VPEP display-pipeline sub-blocks at offset ranges for color conversion, scaling, gamut and gamma LUTs, blending, output formatting, CRC, clock/reset/power controls, memory power controls, timeout status, and performance counters.

## Important APIs, Types, And Functions
There are no C functions, structs, enums, or runtime APIs in this file. Its public surface is the macro namespace:

- `regVPEC_*`: VPE command processor, firmware loading, queue scheduling, ring/IB/CMDIB pointers, interrupts, status, CRC, scratch RAM, public dummy registers, and eight repeated queue register banks.
- `regVPCNVC_*`: VPDPP color/format conversion and pre-CSC controls.
- `regVPDSCL_*`: scaler coefficient RAM, tap control, filter ratios/initial phases, recout, line-buffer, and scaler memory power controls.
- `regVPCM_*`: post-CSC, gamut remap, gamma correction LUT, HDR multiplier, memory power, and test/debug controls.
- `regVPDPP_*`: VPDPP top-level control, soft reset, CRC, and host read control.
- `regVPMPCC_*` and `regVPMPC_*`: MPC composition, output gamma, movable color-management shaper, 3D LUT, 1D LUT, output CSC, CRC, bypass background, clock, reset, pending status, and memory power controls.
- `regVPFMT_*`, `regVPOPP_*`: output formatter clamp/dither/bit-depth registers, pipe control, pipe CRC, and top clock control.
- `regVPEP_*`, `regVPCDC_*`: VPEP clock gating, CDC soft reset, front-end/back-end surface and viewport setup, global sync, vready status, memory power requests, and RBBM interface timeout controls.
- `regPERFCOUNTER_*`, `regPERFMON_*`: VPCDC performance-counter and perfmon registers.

The paired `*_BASE_IDX` constants are part of AMD's generated register-header convention. In the observed consumers, the actual MMIO address is produced by adding the register offset to `adev->reg_offset[VPE_HWIP][inst][0]` through `vpe_get_reg_offset()`.

## Control Flow
The header has no control flow. Its constants participate in control flow in `drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c` and `amdgpu_vpe.c`:

- Firmware loading uses `regVPEC_F32_CNTL` to halt/reset VPE threads, then writes firmware words through `regVPEC_UCODE_ADDR` and `regVPEC_UCODE_DATA`. PSP firmware loading instead records the resolved `regVPEC_F32_CNTL` address/value in the VPE command buffer for `amdgpu_vpe_psp_update_sram()`.
- Ring startup configures queue 0 through `regVPEC_QUEUE0_RB_CNTL`, `RB_BASE`, `RB_RPTR`, `RB_WPTR`, `RB_RPTR_ADDR_*`, `MINOR_PTR_UPDATE`, `DOORBELL_OFFSET`, `DOORBELL`, and `IB_CNTL`, then validates the ring with `amdgpu_ring_test_helper()`.
- Ring stop resets queue 0 through `regVPEC_QUEUE_RESET_REQ` and waits for the reset bit to clear with `SOC15_WAIT_ON_RREG()`.
- Interrupt setup uses `regVPEC_CNTL` to enable or disable trap interrupts; trap processing then advances VPE fences.
- Runtime pointer paths in `amdgpu_vpe.c` use the `vpe->regs` fields initialized from queue 0 offsets to read or write ring pointers when doorbells are not used.

Only a subset of the header is directly referenced by the current VPE 6.1 driver. The VPEP/display-pipeline offsets are still part of the hardware contract exposed to driver code and firmware, but this tree's direct C references are concentrated on the `regVPEC_*` command processor and queue 0 register set.

## State And Persistence Behavior
The header itself is stateless and persistent only as generated source. The state it names is hardware state:

- Firmware SRAM address/data ports and F32 control state.
- Queue state for up to eight queues, including RB base addresses, read/write pointers, doorbell offsets, indirect-buffer pointers, command-IB pointers, context-save addresses, context status, preemption, and doorbell logs.
- Interrupt, watchdog, timestamp, status, error-log, CRC, performance-counter, clock-gating, power, and memory-power registers.
- Display-processing pipeline state for color conversion, scaling coefficients, LUT contents, gamut remap matrices, dither/clamp controls, CRCs, reset controls, and sync/status registers.

The driver writes these registers during hardware initialization, firmware load, ring start/stop, DPM setup, and interrupt enablement. Values generally live in MMIO hardware state and are not persisted by this header; persistence across suspend, reset, or firmware reload depends on the AMDGPU IP block initialization paths reprogramming them.

## Dependencies
This file has no include dependencies beyond the C preprocessor. Its meaningful dependencies are generated-header peers and AMDGPU register helpers:

- `vpe_6_1_0_sh_mask.h` supplies field shifts and masks such as `VPEC_F32_CNTL__HALT_MASK`, `VPEC_QUEUE0_RB_CNTL__RB_ENABLE_MASK`, and `VPEC_CNTL__TRAP_ENABLE_MASK`.
- `vpe_v6_1.c` includes this header with `soc15_common.h`, `amdgpu_vpe.h`, and VPE IRQ source definitions.
- `RREG32()`, `WREG32()`, `REG_SET_FIELD()`, `SOC15_WAIT_ON_RREG()`, and the VPE function table translate these numeric offsets into actual MMIO reads/writes.
- The AMDGPU device's `reg_offset[VPE_HWIP][instance][0]` table supplies the per-instance base address added to each offset.

The header is ASIC/IP-version specific. `vpe_v6_1.c` carries local overrides for VPE 6.1.1 offsets such as `regVPEC_CNTL_6_1_1`, `regVPEC_QUEUE_RESET_REQ_6_1_1`, and `regVPEC_PUB_DUMMY2_6_1_1`, showing that consumers must account for register-layout drift between closely related VPE revisions.

## Integration Points
The direct integration point is AMDGPU VPE 6.1 support:

- `vpe_v6_1_set_regs()` stores key queue and DPM offsets from this header into `struct amdgpu_vpe::regs`, abstracting later generic VPE ring helpers from the raw macro names.
- `vpe_v6_1_get_reg_offset()` resolves a macro offset into an instance-specific MMIO address.
- `amdgpu_vpe.c` uses those stored offsets to implement ring read/write pointer access, doorbell writes, and ring tests.
- PSP integration uses resolved VPE register addresses during SRAM update when firmware loading is delegated to PSP.
- SMU/DPM integration uses selected dummy-register offsets as firmware-visible control mailboxes for VPE dynamic power management.

The VPEP display-processing register groups are integration points for code that configures VPE image processing: surface format, CSC matrices, scaler coefficients, LUTs, output format, CRC validation, clock gating, reset, and memory power. Even when not referenced by current host C code, these constants document the register ABI available for firmware or future driver plumbing.

## Risks
The main risk is silent hardware misprogramming. These are raw numeric offsets; a wrong value can write to an adjacent register, corrupt queue state, hang firmware, break interrupts, or misconfigure display-processing data paths. The 6.1.1 local overrides demonstrate that using a 6.1.0 offset against another revision can be unsafe unless explicitly validated.

Queue register repetition is another risk area. The header defines queues 0 through 7 with regular-looking strides, but current driver code programs queue 0 and selected dummy registers from queues 5 through 7 for DPM. Code that assumes all queue banks are interchangeable must still verify field masks, firmware expectations, doorbell allocation, and collaboration mode behavior.

Because the header only defines offsets, field semantics must come from `vpe_6_1_0_sh_mask.h` and hardware documentation. Updating one generated header without the matching mask header can produce compile-successful but behaviorally wrong register writes.

## Test Signals
Useful validation signals are mostly integration and hardware bring-up signals:

- Build coverage that includes `vpe_v6_1.c` and `amdgpu_vpe.c` catches missing or renamed offset macros.
- VPE firmware load succeeds, including halt/unhalt and ucode data writes, or PSP SRAM update succeeds when PSP loading is active.
- `amdgpu_ring_test_helper()` and VPE ring test paths pass after queue 0 RB, IB, pointer, and doorbell registers are programmed.
- Trap interrupts produce fence progress through `amdgpu_fence_process()` without interrupt storms or missed completions.
- Queue reset completes before `SOC15_WAIT_ON_RREG()` times out.
- DPM configuration does not warn and VPE clock/power telemetry remains sane under load.
- Debugfs/register dumps show expected values in `regVPEC_STATUS*`, queue pointer registers, context status, error log, and clock-gating/power status after init, workload, reset, and suspend/resume.
- For VPEP image-processing paths, CRC/perfmon registers and visual/format validation should match expected scaler, CSC, LUT, dither, and output-format behavior.
