# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779a0.c

## Purpose

This file describes the Renesas R-Car R8A779A0 PFC hardware block to the shared Renesas `sh_pfc` pinctrl driver. It exports `r8a779a0_pinmux_info`, which is selected by SoC match code outside this file and used by the PFC core to create pinctrl functions, groups, GPIO ranges, bias controls, drive-strength controls, and POC voltage-control support.

Compared with smaller R-Car PFC descriptions, this file has a broad multi-bank layout. It covers QSPI/RPC and MMC pins on GP0, serial/MSIOF/display/address/data-style alternatives on GP1/GP2, eight CAN-FD channels on GP3, six AVB/RGMII-style Ethernet banks on GP4 through GP9, plus HSCIF/SCIF, I2C0-6, external interrupts, DU, PWM, TMU, TPU, and non-GPIO debug/reset/reference pins.

## Important APIs, Types, and Data

- `CFG_FLAGS` combines drive-strength and pull-up/down capability, and `CPU_ALL_GP(fn, sfx)` applies it across the GPIO banks. Selected GP0/GP1/GP2 pins also advertise 1.8/3.3 V I/O voltage, while the first 18 pins of each AVB bank GP4-GP9 advertise 2.5/3.3 V I/O voltage.
- `CPU_ALL_NOGP(fn)` defines non-GPIO pins: `PRESETOUT#`, `EXTALR`, `DCUTRST#_LPDRST#`, `DCUTCK_LPDCLK`, `DCUTMS`, and `DCUTDI_LPDI`.
- GPSR macros describe ten banks: GP0 for QSPI/RPC/MMC/SD, GP1 for HSCIF/MSIOF/IRQ, GP2 for IPC/I2C/FXR/TPU/TMU, GP3 for CAN-FD, GP4 for AVB0 plus PCIe clock request and AVS pins, and GP5-GP9 for AVB1 through AVB5.
- IPSR macros are split by bank-style names such as `IP0SR1`, `IP1SR2`, `IP0SR4`, and `IP2SR5`. They encode alternative functions for serial ports, display, external bus address/data pins, I2C physical aliases, CAN-FD alternatives, and AVB RGMII/MII subfunctions.
- `MOD_SEL2` encodes selectable routing for I2C0-6 and SCIF1. The data table uses `PINMUX_IPSR_MSEL()` and `PINMUX_IPSR_PHYS()` for cases where logical I2C pins share physical GP coordinates with generic GP or external bus labels.
- `pinmux_data[]` is the central mapping between generated function IDs and marks. It includes many `PINMUX_SINGLE()` entries for direct GPSR functions, plus IPSR mappings for banked alternatives.
- `pinmux_pins[]` combines all GPIO and non-GPIO pins. The preceding enum uses `GP_ASSIGN_LAST()` and `NOGP_ALL()` to place non-GPIO identifiers after GPIO assignments.
- `pinmux_groups[]` exposes groups for AVB0-AVB5, CAN-FD0-7, CAN clock, DU, HSCIF0-3, I2C0-6, external interrupt pins, MMC, MSIOF0-5, PWM0-4, QSPI0/1, SCIF0/1/3/4 plus SCIF clock, TMU clocks, and TPU outputs.
- `pinmux_functions[]` maps public function names to group arrays. These names are what board pinctrl states reference.
- `pinmux_config_regs[]` describes GPSR0-9, IPSR registers for GP1/GP2/GP3/GP4/GP5, and `MOD_SEL2`. Register addresses are split across `0xe605....` for GP0-GP3 style banks and `0xe606....` for AVB banks.
- `pinmux_drive_regs[]` is a large drive-strength map covering QSPI/RPC/MMC/SD, serial/MSIOF, GP2/FXR/TPU, CAN-FD, PCIe/AVS, and AVB0-AVB5 pins. Entries give the pin, bit offset, and field width, mostly 2-bit or 3-bit fields.
- `pinmux_ioctrl_regs[]` exposes POC registers `POC0`, `POC1`, `POC2`, and `POC4` through `POC9`, plus `TD1SEL0`.
- `r8a779a0_pin_to_pocctrl()` is the SoC-specific POC lookup function. Bias operations use the generic `rcar_pinmux_get_bias` and `rcar_pinmux_set_bias` helpers.

## Control Flow

The file is loaded as static data by the common Renesas PFC platform path. Once `r8a779a0_pinmux_info` is selected, the core registers pins, functions, and groups with Linux pinctrl. A client request for a function/group is resolved through `pinmux_functions[]` and `pinmux_groups[]`, then the core uses marks from the group mux arrays plus `pinmux_data[]` and `pinmux_config_regs[]` to write GPSR, IPSR, and MOD_SEL fields.

I2C routing is a notable path through the data. Several GP2 pins have generic GP labels or external data labels in the same IPSR field, while logical `SCLx`/`SDAx` signals are represented with `PINMUX_IPSR_PHYS()` and MOD_SEL values. This lets the core select the physical I2C function while preserving the register field's alternate-function encoding.

Drive-strength requests flow through common PFC code using `.drive_regs = pinmux_drive_regs`. The core finds the requested pin in the table, reads the register, updates the specified bit field, and writes it back through the shared unlock/write machinery.

Bias requests flow through `rcar_pinmux_get_bias` and `rcar_pinmux_set_bias`, using `pinmux_bias_regs[]` PUEN/PUD mappings. Unlike the R8A77995 file, there is no SoC-specific remapping of PUEN versus PUD bits.

POC requests call `r8a779a0_pin_to_pocctrl()`. The function computes `bit = pin & 0x1f`, then checks supported ranges in order: GP0 pins 15-27 use `POC0`; GP1 pins 0-30 use `POC1`; GP2 pins 2-15 use `POC2`; GP4-GP9 pins 0-17 use their corresponding POC registers. Unsupported pins return `-EINVAL`.

## State and Persistence

This file owns no mutable software state. Hardware state persists in PFC registers programmed by the common core: GPSR/IPSR/MOD_SEL for muxing, drive-control registers for output strength, PUEN/PUD for bias, and POC registers for voltage control. All tables are compile-time constants.

There is no dynamic allocation, workqueue, interrupt handler, or file-backed persistence in this source. Register locking and protected writes are handled by the shared PFC layer. The `.unlock_reg = 0x1ff` value is a PMMR mask for this SoC generation rather than a normal MMIO address, so it is part of the common-core integration contract.

## Dependencies and Integration Points

The file includes Linux `errno`, `io`, and `kernel` headers and Renesas `sh_pfc.h`. It depends heavily on Renesas PFC macros and types for table generation: `PORT_GP_CFG_*`, `PIN_NOGP_CFG`, `RCAR_GP_PIN`, `PINMUX_SINGLE`, `PINMUX_IPSR_GPSR`, `PINMUX_IPSR_MSEL`, `PINMUX_IPSR_PHYS`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `PINMUX_DRIVE_REG`, `PINMUX_BIAS_REG`, `SH_PFC_PIN_GROUP`, `BUS_DATA_PIN_GROUP`, and `SH_PFC_FUNCTION`.

The exported integration point is `const struct sh_pfc_soc_info r8a779a0_pinmux_info`. Board device trees consume it indirectly through group/function names such as `avb3_rgmii`, `canfd7_data`, `hscif2_ctrl`, `i2c6`, `mmc_data8`, `msiof5_txd`, `qspi1_data4`, `scif1_data_b`, `tmu_tclk4`, or `tpu_to3`.

The POC, drive-strength, bias, and mux register maps integrate with the same common core, so adding a new pin or function normally requires coordinated changes across pin inventory, enum generation, pinmux data, group arrays, config registers, and optional bias/drive/POC maps.

## Risks and Maintenance Notes

- The file has many repeated AVB banks. Copy/paste drift between AVB0-AVB5 group arrays, mux marks, drive registers, bias registers, and POC ranges is a major risk.
- `pinmux_drive_regs[]` and `pinmux_bias_regs[]` must agree with the pin capability flags from `CPU_ALL_GP()`. Advertising drive strength or voltage control without table support can produce failed or confusing pinconf behavior.
- `r8a779a0_pin_to_pocctrl()` intentionally supports only voltage-capable ranges. Extending voltage flags to a new range without updating this function will cause POC lookup failures.
- I2C physical aliases use MOD_SEL and `PINMUX_IPSR_PHYS()`; those entries are easier to break than direct `PINMUX_IPSR_GPSR()` mappings because the logical signal name and field-visible function name differ.
- Reserved fields in `PINMUX_CFG_REG_VAR()` protect sparse hardware registers. Incorrect reserved widths shift later bit fields and can make unrelated functions program the wrong hardware.
- Group and function names form a device-tree-facing contract. Renames can break board pinctrl states even if the numeric register data remains valid.
- The `.unlock_reg = 0x1ff` PMMR-mask convention differs from older files that pass an address. Treating it like a regular unlock register would be a core integration bug.

## Test Signals

Compile-time validation should include building this driver and checking that every pin group has matching pin and mux array lengths, every group referenced from a function exists, and generated enum marks match all group mux entries. Runtime validation on R8A779A0 hardware should exercise QSPI/RPC/MMC boot media pins, all enabled AVB RGMII banks, CAN-FD channels, HSCIF/SCIF/MSIOF serial paths, I2C0-6 physical selections, DU output groups, PWM/TMU/TPU groups, bias get/set via pinconf, drive-strength get/set via pinconf, and POC voltage selection for GP0/GP1/GP2/GP4-GP9 supported ranges. `debugfs` pinctrl dumps and absence of `-EINVAL` for supported POC pins are useful signals.
