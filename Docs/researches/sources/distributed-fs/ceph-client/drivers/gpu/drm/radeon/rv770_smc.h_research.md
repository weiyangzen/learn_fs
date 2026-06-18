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
