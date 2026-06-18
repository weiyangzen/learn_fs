# subset-b-005102 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77995.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77995.c

## Purpose

This file describes the Renesas R-Car R8A77995 (R-Car D3) PFC hardware block to the shared Renesas `sh_pfc` pinctrl driver. It does not probe hardware by itself. Instead it exports `r8a77995_pinmux_info`, a `struct sh_pfc_soc_info` consumed by the Renesas PFC core to expose GPIO-capable pins, non-GPIO pins, mux functions, pin groups, register layouts, pull-bias support, and POC voltage-control lookup.

The source is mostly declarative SoC data. It maps GPSR/IPSR/MOD_SEL register fields to logical functions such as display output, VIN4, EtherAVB0, CAN/CAN-FD, MMC/RPC/QSPI, SCIF/HSCIF/MSIOF, I2C, PWM, SSI/audio clocks, MLB, USB0 control, NAND, and TPU/TMU signals. The file also contains a small amount of SoC-specific control logic for POC lookup and for a pull-bias bit swap on NAND `NFRE#`/`NFWE#`.

## Important APIs, Types, and Data

- `CPU_ALL_GP(fn, sfx)` and `CPU_ALL_NOGP(fn)` define the pin inventory. GPIO ports are GP0 with 9 pins, GP1/GP2/GP4 with 32 pins each, GP3 with 10 pins, GP5 with 21 pins, and GP6 with 14 pins. Most pins advertise pull-up/down; GP3 also advertises 1.8/3.3 V I/O voltage, and the non-GPIO `VDDQ_AVB0` pin advertises 2.5/3.3 V I/O voltage.
- `GPSR*`, `IP*`, and `MOD_SEL*` macros encode alternate-function information. The same macros are expanded differently to build function IDs, mark IDs, data entries, and register field tables.
- The top-level enum creates `PINMUX_DATA_*`, `PINMUX_FUNCTION_*`, and `PINMUX_MARK_*` ID ranges. These IDs must remain coherent with `pinmux_data[]`, `pinmux_config_regs[]`, and the group mux arrays.
- `pinmux_data[]` links GPIO/function selections to marks using `PINMUX_SINGLE`, `PINMUX_IPSR_GPSR`, and `PINMUX_IPSR_MSEL`. MSEL entries bind a function alternative to a MOD_SEL choice, for example A/B choices for SCIF, I2C, CAN, EtherAVB AVTP, PWM, TMU, HSCIF, MSIOF, and SSI routes.
- `pinmux_pins[]` is generated from `PINMUX_GPIO_GP_ALL()` and `PINMUX_NOGP_ALL()`, giving the PFC core the full pin list including JTAG/reset/reference/non-GPIO voltage pins.
- `pinmux_groups[]` lists board-requestable pin groups with helper macros such as `SH_PFC_PIN_GROUP`, `SH_PFC_PIN_GROUP_ALIAS`, `BUS_DATA_PIN_GROUP`, and `SH_PFC_PIN_GROUP_SUBSET`. Deprecated `avb0_mdc` is kept as an alias for `avb0_mdio`.
- `pinmux_functions[]` maps function names to their group arrays: `audio_clk`, `avb0`, `can0`, `can1`, `can_clk`, `canfd0`, `canfd1`, `du`, `i2c0` through `i2c3`, `mlb_3pin`, `mmc`, `msiof0` through `msiof3`, `pwm0` through `pwm3`, `qspi0`, `qspi1`, `rpc`, `scif0` through `scif5`, `scif_clk`, `ssi`, `usb0`, and `vin4`.
- `pinmux_config_regs[]` defines the PFC register map. GPSR0-6 live at `0xe6060100` through `0xe6060118`; IPSR0-13 live at `0xe6060200` through `0xe6060234`; MOD_SEL0/1 live at `0xe6060500` and `0xe6060504`. Variable-width macros model reserved fields in sparse registers.
- `pinmux_ioctrl_regs[]` exposes `POCCTRL0`, `POCCTRL2`, and `TDSELCTRL` at `0xe6060380`, `0xe6060388`, and `0xe60603c0`.
- `pinmux_bias_regs[]` maps PUEN/PUD register pairs `PUEN0..PUEN5` to pins. It includes GPIO and non-GPIO pins, with explicit `SH_PFC_PIN_NONE` holes for reserved bits.
- `r8a77995_pin_to_pocctrl()`, `r8a77995_pinmux_get_bias()`, and `r8a77995_pinmux_set_bias()` are the only custom behavior beyond table data. They are installed through `r8a77995_pfc_ops`.

## Control Flow

Registration is data-driven. Platform match code elsewhere selects `r8a77995_pinmux_info`; the common PFC core reads its `.pins`, `.groups`, `.functions`, `.cfg_regs`, `.bias_regs`, `.ioctrl_regs`, and `.pinmux_data` members and creates pinctrl/GPIO-facing objects from them.

When a client requests a function/group, the core matches the function name to `pinmux_functions[]`, resolves a group from `pinmux_groups[]`, reads the group's mux marks, and programs GPSR/IPSR/MOD_SEL fields according to `pinmux_data[]` and `pinmux_config_regs[]`. Selection of multiplexed A/B/C variants is carried by `PINMUX_IPSR_MSEL()` entries and the MOD_SEL register definitions.

Bias operations go through the SoC operations table instead of the generic helpers. `r8a77995_pinmux_get_bias()` calls `r8a77995_pin_to_bias_reg()`, reads the PUEN bit to decide enabled/disabled, and reads the PUD bit to distinguish pull-up from pull-down. `r8a77995_pinmux_set_bias()` clears or sets the enable bit and writes the direction bit before enabling when needed. The helper delegates normal bit mapping to `rcar_pin_to_bias_reg()` but remaps `NFRE#` and `NFWE#` because those two NAND pins use opposite PUD bit positions from their PUEN bits.

POC voltage-control lookup is narrow. `r8a77995_pin_to_pocctrl()` returns bits in `POCCTRL0` for GP3 pins 0 through 9, mapping them to bits 29 down to 20, and returns bit 0 in `POCCTRL2` for `PIN_VDDQ_AVB0`; every other pin returns `-EINVAL`.

## State and Persistence

Runtime state is entirely in PFC hardware registers, not in heap objects owned by this file. Mux state persists in GPSR/IPSR/MOD_SEL registers after the core writes them. Bias state persists in PUEN/PUD registers. POC state persists in POCCTRL registers selected by the custom lookup. The exported `sh_pfc_soc_info` and all tables are `static const` or `const` and immutable after compilation.

There is no file I/O, dynamic allocation, firmware parsing, locking, or persistent storage in this source. Synchronization and register unlock/write sequencing are handled by the shared PFC core using the `.unlock_reg = 0xe6060000` PMMR address.

## Dependencies and Integration Points

The file depends on Linux kernel headers for `-EINVAL`, `BIT()`, and `ARRAY_SIZE()` style support, plus Renesas-local `core.h` and `sh_pfc.h`. Most of its macros and types are defined in the shared Renesas pinctrl infrastructure: `struct sh_pfc_soc_info`, `struct sh_pfc_soc_operations`, `struct sh_pfc_pin`, `struct sh_pfc_pin_group`, `struct sh_pfc_function`, `struct pinmux_cfg_reg`, `struct pinmux_bias_reg`, `struct pinmux_ioctrl_reg`, `RCAR_GP_PIN()`, `PORT_GP_CFG_*`, `PIN_NOGP_CFG()`, `PINMUX_*`, `SH_PFC_PIN_GROUP*`, and `BUS_DATA_PIN_GROUP()`.

Externally visible integration is the exported `const struct sh_pfc_soc_info r8a77995_pinmux_info`. Device-tree compatible matching and platform-driver registration live outside this file. Board device trees interact with the data indirectly through pinctrl function and group names such as `avb0_mii`, `du_rgb888`, `i2c3_a`, `qspi0_data4`, `rpc_clk2`, `scif5_data_b`, or `vin4_data24`.

## Risks and Maintenance Notes

- The file is dense table data, so off-by-one register bit positions, wrong GP coordinates, or mismatched pin/mux array lengths are the dominant failure modes.
- `NFRE#` and `NFWE#` are special: PUEN and PUD bit positions differ. Removing or bypassing the custom bias helpers would silently invert or misprogram pull direction for those NAND pins.
- `PINMUX_CFG_REG_VAR()` reserved-field widths must match hardware documentation. A wrong negative reserved width shifts every later field.
- Group names are ABI-like for device trees. Renaming groups or removing the deprecated `avb0_mdc` alias can break existing board descriptions.
- POC lookup only supports GP3 and `VDDQ_AVB0`. Adding voltage-capable pins requires updating both pin capabilities and `r8a77995_pin_to_pocctrl()`.
- The file lacks drive-strength data, so drive-strength requests should be rejected or ignored by the common core unless another path supplies them.

## Test Signals

Useful validation includes building the Renesas pinctrl driver with this file, checking that every `*_pins[]` array has the same element count as its `*_mux[]` array, verifying every group referenced by a function exists in `pinmux_groups[]`, and boot-testing an R8A77995 board with pinctrl debugfs enabled. Runtime signals include successful muxing for AVB0, DU, VIN4, QSPI/RPC, MMC, SCIF/MSIOF/I2C, and CAN/CAN-FD, correct `pinctrl` bias get/set behavior for ordinary pins and NAND `NFRE#`/`NFWE#`, and successful POC voltage selection for GP3 and `VDDQ_AVB0` without `-EINVAL` for supported pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77995.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779a0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779a0.c -->
