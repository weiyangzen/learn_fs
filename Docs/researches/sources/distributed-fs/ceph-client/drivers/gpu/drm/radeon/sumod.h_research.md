<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumod.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumod.h

## Purpose
`sumod.h` is the Sumo/Palm register definition header for DPM, clock gating, graphics power gating, RCU/SMU communication, voltage scaling, deep sleep, thermal interrupts, and a few hardware revision/address-config registers. It is the hardware map used by `sumo_dpm.c` and `sumo_smc.c`.

## Important APIs, types, and definitions
- RCU/SMU registers: firmware version, power-gating sequence/control registers, alt-VDDNB notify, LCLK scaling control, boost disable, M3 arbiter parameter/index registers, boost/throttle margins, GNB/TDP limits, and PCIe power-gating args.
- Mailbox bits: `GFX_INT_REQ`, `SERV_INDEX`, `INT_REQ`, `GFX_INT_STATUS`, `INT_ACK`, and `INT_DONE`.
- SCLK and DPM controls: `CG_SCLK_CNTL`, `CG_SCLK_STATUS`, `SCLK_PWRMGT_CNTL`, profile index fields, `CG_SCLK_DPM_CTRL*`, valid/divider fields, forced-state bits, thermal throttle masks, DPM enable, GNB slow/forced NB pstate bits, and bootup state fields.
- Timing/activity registers: `CG_GCOOR`, `CG_FTV`, `CG_FFCT_0`, `CG_GIT`, `CG_SSP`, `CG_AT_*`, `CG_BSP_0`, and related field helpers.
- Voltage and power-gating controls: `CG_CG_VOLTAGE_CNTL`, `CG_ACPI_VOLTAGE_CNTL`, `CG_DPM_VOLTAGE_CNTL`, `CG_PWR_GATING_CNTL`, and associated enable, level, period/unit, and gating parameter fields.
- Deep-sleep and thermal controls: `DEEP_SLEEP_CNTL`, `DEEP_SLEEP_CNTL2`, `CG_THERMAL_INT`, high/low interrupt masks, and scratch/address-config registers.

## Control flow and integration points
The file has no functions. `sumo_dpm.c` uses these definitions to program clocks, voltage, DPM levels, thermal interrupts, and gating. `sumo_smc.c` uses them for RCU mailbox traffic, M3 arbiter tables, boost/TDP programming, and firmware version readback.

## State and persistence behavior
All definitions refer to hardware state. MMIO/RCU writes persist in the GPU/SMU until overwritten, gated, or reset. Many registers are updated in multi-step sequences: for example graphics power gating stages RCU sequence and timing registers around SMU service calls, while DPM transitions program level values before toggling valid bits and forced mode.

## Dependencies and constraints
Consumers must use the correct access path: some offsets are RCU-space and are accessed through `RREG32_RCU/WREG32_RCU`, while others are normal MMIO. The file notes an address overlap between `RCU_PWR_GATING_CNTL_5` and `MCU_M3ARB_INDEX` spaces and between boost/parameter offsets depending on access path, so accessors matter. Field macros do shifting but not validation.

## Risks and test signals
Misusing an offset, accessor, shift, or mask can corrupt DPM levels, voltage selection, thermal IRQ thresholds, boost/TDP limits, or firmware mailbox state. Test signals include Sumo DPM enable/disable, forced performance levels, boost transitions, thermal interrupt programming, power-gating entry/exit, RCU firmware version readback, and register readback during debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/sumod.h -->
