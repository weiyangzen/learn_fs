# subset-b-003736 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.h

## Purpose
`rv770_dpm.h` is the private dynamic power-management contract for R7xx Radeon ASICs and closely related descendants that reuse the RV770 SMC/DPM model. It defines the CPU-side state containers used by `rv770_dpm.c`, RV730/RV740 helpers, Cypress/BTC/NI/SI reuse paths, and the SMC upload layer. The file bridges three domains: BIOS/driver power states, hardware clock/voltage register snapshots, and packed SMC state-table structures from `rv770_smc.h`.

## Important APIs, types, and functions
The central state type is `struct rv7xx_power_info`, stored through `rdev->pm.dpm.priv` by the implementation. It records feature flags for memory type, PCIe Gen2 policy, voltage and MVDD control, spread spectrum, clock gating, thermal protection, display gap handling, DC ODT, and ULPS. It also persists register snapshots, voltage masks, voltage tables, ODT thresholds, boot and ACPI values, response-time tunables, SMC SRAM offsets (`state_table_start`, `soft_regs_start`, `sram_end`), and a scratch `RV770_SMC_STATETABLE`.

Clock data is split by ASIC: `struct rv770_clock_registers` captures RV770 SPLL/MPLL/DLL registers, `struct rv730_clock_registers` captures the RV730/RV710 MPLL layout, and `union r7xx_clock_registers` lets common code carry either shape. `struct rv7xx_pl` describes one performance level with sclk, mclk, vddc, optional vddci, flags, and a PCIe generation enum; `struct rv7xx_ps` groups high/medium/low levels plus DC compatibility. `struct vddc_table_entry` and constants such as `MAX_NO_VREG_STEPS`, `MAX_NO_OF_MVDD_VALUES`, `MVDD_LOW_INDEX`, and `MVDD_HIGH_INDEX` define voltage lookup and SMIO programming capacity.

The prototypes expose the full DPM helper surface. RV730/RV710 functions populate SCLK/MCLK SMC values, read clock registers, create ACPI/initial SMC states, program memory timing and DC ODT, and start/stop DPM. RV740 variants add memory-clock spread-spectrum and DLL helper calculations. RV770 common functions handle voltage and MVDD conversion, sequence selection, memory refresh, SMC state construction, voltage SMIO reads, memory-type and module discovery, PCIe Gen2 status, ACPI PM, CGCG restore, voltage/backbias/thermal toggles, throttle sources, BSP/GIT/TP/TPP/SSTP/VC programming, firmware upload, SMC halt/resume, SW/boot state switching, power-table parsing, UVD clock sequencing, spread-spectrum discovery, and soft-register writes.

## Control flow and integration points
This header has no executable control flow, but it defines the call graph shape used by Radeon ASIC hooks. Initialization parses AtomBIOS power tables into `rv7xx_power_info`, captures clock and voltage baselines, uploads SMC firmware via `rv770_upload_firmware`, constructs `RV770_SMC_STATETABLE`, and copies it into SMC SRAM. Runtime power transitions build or restrict performance levels, write SMC soft registers, send SMC messages, and sequence UVD, voltage, memory clock, engine clock, PCIe, and display-gap behavior.

Integration is broad: `rv770_dpm.c`, `rv730_dpm.c`, `rv740_dpm.c`, `cypress_dpm.c`, `btc_dpm.h`, and later DPM implementations reuse the types and prototypes. It depends on `radeon.h` for core device, DPM, and PCIe types, and on `rv770_smc.h` for the packed firmware ABI.

## State and persistence behavior
The header-owned structures model persistent runtime state, but storage is allocated by implementation code. Values in `rv7xx_power_info` survive across DPM transitions and are used to restore or recompute hardware programming after suspend/resume, display changes, forced-level changes, and SMC resets. The SMC offsets are especially important because all SMC table and soft-register writes are range-checked against the SRAM end discovered for the active ASIC/firmware.

## Dependencies, risks, and test signals
The main risks are ABI drift between `rv770_dpm.h`, `rv770_smc.h`, and the implementation, incorrect assumptions across RV770/RV730/RV740 layouts, and stale shared declarations used by Evergreen/Northern/Southern Islands code. Incorrect voltage table sizes, SMC offsets, or clock-register unions can cause failed DPM enablement, bad voltage selection, memory-clock instability, thermal-policy failures, or SMC message errors. Build coverage across RV770, RV730, RV740, Cypress/BTC, NI, and SI DPM users is the first test signal. Runtime signals include DPM init/enable/disable, AC/DC switching, forced performance levels, suspend/resume, UVD clock transitions, thermal interrupt behavior, debugfs current clocks, and absence of SMC upload or state-switch failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.c

## Purpose
`rv770_smc.c` implements the host-side SMC SRAM, reset/clock, firmware-load, interrupt-vector, and mailbox-message operations used by RV770-family Radeon dynamic power management. It is the low-level transport layer beneath the DPM code: higher-level code prepares firmware blobs, SMC state tables, and soft-register values, while this file safely moves bytes and dwords into SMC address space and coordinates with the microcontroller through MMIO registers.

## Important APIs and functions
The file includes Linux firmware support plus Radeon core, RV770 register definitions, DPM declarations, SMC table declarations, AtomBIOS helpers, and firmware metadata. It defines static interrupt-vector byte arrays for RV770, RV730, RV710, RV740, Evergreen (`CEDAR`, `REDWOOD`, `JUNIPER`, `CYPRESS`/`HEMLOCK`), Northern Islands/BTC (`BARTS`, `TURKS`, `CAICOS`), and Cayman. `FIRST_SMC_INT_VECT_REG` and `FIRST_INT_VECT_S19` define the relevant high SMC vector/register area.

`rv770_set_smc_sram_address` is the private address gate: it requires 4-byte alignment, rejects dword accesses beyond `limit`, sets `SMC_SRAM_AUTO_INC_DIS`, and writes `SMC_SRAM_ADDR`. `rv770_copy_bytes_to_smc` copies an arbitrary byte count into SMC SRAM with big-endian dword packing and a read-modify-write tail for non-multiple-of-four lengths. It serializes access with `rdev->smc_idx_lock`. `rv770_program_interrupt_vectors` writes big-endian vector dwords into `SMC_ISR_FFD8_FFDB` and skips any vector data before `FIRST_SMC_INT_VECT_REG`.

Lifecycle helpers are direct MMIO bit updates: `rv770_start_smc`, `rv770_reset_smc`, `rv770_stop_smc_clock`, `rv770_start_smc_clock`, and `rv770_is_smc_running` manipulate or inspect `SMC_IO` bits `SMC_RST_N`, `SMC_CLK_EN`, and `SMC_STOP_MODE`. `rv770_send_msg_to_smc` writes a `PPSMC_Msg` into `SMC_MSG`, polls `HOST_SMC_RESP` up to `rdev->usec_timeout`, and returns a `PPSMC_Result`. `rv770_wait_for_smc_inactive` polls stop mode when the SMC is running. `rv770_clear_smc_sram` zeros the SRAM window in aligned dword steps. `rv770_load_smc_ucode` chooses per-family firmware start/size and interrupt-vector metadata, clears SRAM, copies `rdev->smc_fw->data`, and programs the vectors. `rv770_read_smc_sram_dword` and `rv770_write_smc_sram_dword` provide locked aligned dword accessors.

## Control flow
Firmware load starts by rejecting a missing `rdev->smc_fw`, clearing SRAM up to the caller-provided `limit`, selecting ucode and vector constants based on `rdev->family`, copying the firmware payload into SMC SRAM, then programming interrupt vectors. Unknown families log `DRM_ERROR` and call `BUG()`, reflecting that this path is only valid for known ASIC tables. Message flow first verifies the SMC is out of reset with its clock enabled, then writes the host message and busy-waits in microsecond increments for firmware response.

## State and persistence behavior
Persistent state lives in hardware: SMC SRAM contents, SMC interrupt-vector registers, `SMC_IO` reset/clock/stop bits, and `SMC_MSG` mailbox fields. Driver state consumed by this file includes `rdev->smc_fw`, `rdev->family`, `rdev->usec_timeout`, and `rdev->smc_idx_lock`. SRAM writes persist until cleared, overwritten, reset, or power-cycled, and DPM later relies on these contents for firmware execution and state-table interpretation.

## Dependencies and integration points
The implementation depends on register macros from `rv770d.h`, SMC ucode location/size constants from `radeon_ucode.h`, firmware ownership in `struct radeon_device`, and SMC message/result enums from `ppsmc.h` through `rv770_smc.h`. `rv770_dpm.c`, `cypress_dpm.c`, and later DPM code call these helpers to upload firmware, write state tables and soft registers, halt/resume the SMC, switch states, and inspect SRAM.

## Risks and test signals
High-risk areas are endianness, alignment, SRAM bounds, per-family ucode constants, interrupt-vector offsets, timeout handling, and lock coverage around the SMC SRAM index register. A bad copy or vector table can prevent DPM from starting; an incorrect limit can corrupt adjacent SMC data; a missing response can stall state transitions. Test signals include successful SMC firmware upload, `PPSMC_Result_OK` for halt/resume/state-switch messages, no `unknown asic` path, stable DPM enable/disable, suspend/resume, forced-level changes, and register/SRAM readback on hardware with RV7xx/Evergreen/NI/Cayman variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.h

## Purpose
`rv770_smc.h` defines the packed host-to-SMC data ABI for RV770-family dynamic power management and declares the SMC transport functions implemented in `rv770_smc.c`. It is shared by DPM table construction code and by the low-level SRAM/message implementation, so it fixes exact table layout, field order, register-value containers, voltage masks, soft-register offsets, and mailbox helper prototypes.

## Important APIs, types, and definitions
The file includes `ppsmc.h` for SMC message/result definitions and wraps the SMC data structures in `#pragma pack(push, 1)` to match firmware layout exactly. `RV770_SMC_TABLE_ADDRESS` defines the base table address (`0xB000`), and `RV770_SMC_PERFORMANCE_LEVELS_PER_SWSTATE` fixes each software state at three hardware performance levels.

Clock and voltage ABI types are `RV770_SMC_SCLK_VALUE`, `RV770_SMC_MCLK_VALUE`, `RV730_SMC_MCLK_VALUE`, `RV770_SMC_VOLTAGE_VALUE`, and `RV7XX_SMC_MCLK_VALUE`. They carry precomputed register images and decoded clock/voltage values for firmware to apply. `RV770_SMC_HW_PERFORMANCE_LEVEL` combines arbiter, sequence/AC index, display watermark, PCIe Gen2 controls, backbias, strobe, memory-controller flags, activity thresholds, SCLK/MCLK register blocks, VDDC/MVDD/VDDCI values, and state flags. `SMC_STROBE_*` and `SMC_MC_*` constants define packed hardware-level flags for strobe, EDC, RTT, and memory stutter.

`RV770_SMC_SWSTATE` groups three hardware levels behind software-state flags. `RV770_SMC_VOLTAGEMASKTABLE` carries high and low SMIO masks for VDDC, MVDD, VDDCI, and an unused slot. `RV770_SMC_STATETABLE` is the top-level firmware table: thermal/system flags, max VDDC index, high/low SMIO arrays, voltage mask table, and the four SMC states `initialState`, `ACPIState`, `driverState`, and `ULVState`. Soft-register offsets such as `mclk_chg_timeout`, `baby_step_timer`, voltage/backbias/ACPI delays, `seq_index`, `mvdd_chg_time`, `mclk_switch_lim`, `mc_block_delay`, `uvd_enabled`, and `is_asic_lombok` define the runtime tunables written relative to `RV770_SMC_SOFT_REGISTERS_START`.

The function prototypes expose byte copy, SMC start/reset/clock control, running-state detection, message send, inactive wait, SRAM dword read/write, and firmware load.

## Control flow and integration points
This header contains no executable logic. DPM code fills the packed structures, usually converting multi-byte register values to the SMC's expected endian representation before upload, then calls `rv770_copy_bytes_to_smc` or `rv770_write_smc_sram_dword` to place them in firmware SRAM. Runtime control uses `rv770_send_msg_to_smc` with `PPSMC_Msg` values from `ppsmc.h` after firmware is loaded and started.

## State and persistence behavior
The structures are transient in CPU memory until copied to SMC SRAM, where they become persistent firmware inputs. Once uploaded, the SMC interprets them to change clocks, voltages, memory behavior, PCIe state, thermal behavior, UVD awareness, and ULV/ACPI/driver power states. The soft-register offsets identify persistent firmware variables, while the transport functions mutate SMC hardware state through `struct radeon_device`.

## Dependencies, risks, and test signals
This file is an ABI boundary. Packing, field order, union size, endian conversion expectations, table base, level count, and soft-register offsets must match the firmware binary selected by `rv770_smc.c`. `MAX_NO_VREG_STEPS` is also defined in `rv770_dpm.h`; mismatches would corrupt table construction. Risks include firmware reading wrong fields, voltage masks addressing wrong SMIO entries, bad level transitions, or memory-clock failures. Test signals include successful table upload, SMC state switches, voltage/MVDD changes, memory stutter and display watermark behavior, thermal protection messages, UVD soft-register toggles, and build coverage for every consumer that includes this ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770d.h

## Purpose
`rv770d.h` is the RV770/R7xx hardware definition header for the Radeon driver. It maps ASIC limits, MMIO register addresses, bit masks, field shifts, packet constructors, PCIe indirect registers, display/audio registers, UVD registers, memory-controller fields, shader/graphics-pipeline controls, VM registers, DMA packet encodings, and SMC/power-management registers. Implementation files include it to turn high-level driver policy into exact MMIO writes and command-stream words.

## Important APIs, types, and definitions
The file starts with R7xx resource caps: maximum shader GPRs, temporary GPRs, threads, stack entries, render backends, SIMDs, and pipes. Power and clock definitions cover UPLL, SMC SRAM/data/IO/message registers, SPLL/MPLL control/status, general power management, SCLK/MCLK power management, DLL, display gap, spread spectrum, clock-gating local controls, BIOS scratch, memory type detection, memory arbitration, and thermal registers. These are the definitions directly consumed by RV770 DPM and SMC code.

Core graphics and memory definitions include color-buffer bases, backend and TCC disable registers, memory size and channel/remap configuration, command processor microcode/ring registers, tiling configuration, GRBM/SRBM status and reset, shader pipe/resource management, SPI/SQ/SX/TA/TCP/VGT state, scratch registers, HDP coherency, PA/SC raster state, VM L1/L2/context registers, and wait/status registers. Async DMA definitions provide ring pointers and packet constructors/opcodes for write, copy, indirect buffer, semaphore, fence, trap, constant fill, and NOP.

Display and audio sections define DCE 3.2 HDMI and AFMT packet/control/status registers, AVI/MPEG/audio infoframe fields, ACR values, generic packet slots, ELD audio descriptors, hot-plug/audio-enable bits, and primary/secondary scanout addresses. PCIe sections define link power, width, speed, retraining, Gen2 support/status, and config-write control. PM4 `PACKET0` and `PACKET3` helpers construct command-processor packet headers. UVD definitions provide semaphore, command, LMI/cache, ring, and context registers.

## Control flow and integration points
There is no executable control flow. The header is integrated wherever Radeon RV770-family code performs MMIO, constructs PM4/DMA packets, configures power states, initializes rings, sets up VM/memory, handles display/audio, or controls UVD. In this work item, `rv770_smc.c` uses `SMC_SRAM_ADDR`, `SMC_SRAM_DATA`, `SMC_IO`, `SMC_MSG`, `SMC_ISR_FFD8_FFDB`, and their bitfields; `rv770_dpm.c` uses the clock, voltage, thermal, spread-spectrum, memory, and PCIe definitions declared here.

## State and persistence behavior
The header owns no storage. Every definition names hardware state that persists in registers, indirect PCIe config space, command rings, SMC SRAM, display/audio blocks, VM engines, or media engines once programmed by callers. Packet helpers create values that mutate GPU state only when submitted to the command processor or DMA engine. Because many registers are sticky across runtime power transitions until reset or explicitly reprogrammed, callers often snapshot values in DPM structures or restore them during resume.

## Dependencies and constraints
Consumers must provide Radeon packet constants such as `RADEON_PACKET_TYPE0`/`RADEON_PACKET_TYPE3`, MMIO accessors, and Linux integer types through surrounding driver headers. Field helpers mostly shift caller-provided values without semantic validation, and masks are supplied separately. Callers are responsible for applying masks, respecting register block ownership, ordering reset/clock/power writes correctly, and using indirect PCIe accessors for PCIe registers.

## Risks and test signals
This file is a hardware contract. Any wrong address, mask, shift, packet opcode, or resource limit can cause GPU hangs, broken modesets, invalid VM translations, corrupted command streams, failed SMC/DPM enablement, PCIe retraining failures, UVD/audio regressions, or display underruns. Test signals include RV770 probe and ring tests, SMC firmware load and message response, DPM clock/voltage transitions, thermal interrupt behavior, modeset and HDMI/DP audio validation, UVD playback, VM fault stress, async DMA copy tests, suspend/resume, and register readback against known-good hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770d.h -->
