# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779h0.c

## Purpose

`pfc-r8a779h0.c` is the Renesas R-Car V4M (`R8A779H0`) pin function controller description consumed by the common `sh_pfc`/Renesas pinctrl core. It does not register a platform driver itself; instead it exports `r8a779h0_pinmux_info`, a `struct sh_pfc_soc_info` instance that describes all GPIO-capable pins, non-GPIO voltage-domain pins, multiplexed functions, register layouts, drive-strength controls, bias controls, and IO-voltage controls for this SoC.

The file is table-driven. Its main job is to convert SoC manual data into kernel pinctrl data structures: GPIO pins become `RCAR_GP_PIN()` IDs, alternate functions become `*_MARK` and `FN_*` enum entries, and GPSR/IPSR/MOD_SEL register bitfields become `struct pinmux_cfg_reg` descriptors. Higher-level consumers select groups such as `avb0_rgmii`, `qspi0_data4`, `scif1_data_a`, or `i2c2`, and the common PFC core programs the described registers.

## Important APIs, types, and data

- `CFG_FLAGS` combines drive strength and pull-up/down support; selected port ranges add `SH_PFC_PIN_CFG_IO_VOLTAGE_18_33`.
- `CPU_ALL_GP()` expands the SoC's sparse GPIO banks. It defines banks 0 through 7, with reserved holes in several banks, and marks banks 0, early bank 3, and early bank 4 as 1.8/3.3 V capable.
- `CPU_ALL_NOGP()` defines non-GPIO voltage-domain pseudo-pins `VDDQ_AVB0`, `VDDQ_AVB1`, and `VDDQ_AVB2` with 1.8/2.5 V IO-voltage control.
- `GPSR*`, `IP*SR*`, and `MOD_SEL4_*` macros define the function-option universe. The file repeatedly redefines `F_()` and `FM()` to use the same macro inventory for enum generation, pinmux marks, and register tables.
- `pinmux_data[]` maps each selectable function mark to the corresponding IPSR/GPSR field and, where needed, a module-select bit via `PINMUX_IPSR_MSEL()`.
- `pinmux_pins[]` is built from `PINMUX_GPIO_GP_ALL()` plus the non-GPIO pins.
- `pinmux_groups[]` and `pinmux_functions[]` provide the modern pinctrl grouping interface for device-tree pinctrl states.
- `pinmux_config_regs[]` describes GPSR0-7, IPSR registers for banks 0-7, and `MOD_SEL4`.
- `pinmux_drive_regs[]` describes per-pin drive-strength bitfields in DRVxCTRLy registers. Widths vary: many pins have 3-bit drive selectors, while some pins such as QSPI/RPC/PWM/error pins have 2-bit selectors.
- `pinmux_bias_regs[]` maps pull enable (`PUEN*`) and pull direction (`PUD*`) registers to pins, using `SH_PFC_PIN_NONE` for reserved bits.
- `pinmux_ioctrl_regs[]` lists POC registers used for IO-voltage selection.
- `r8a779h0_pin_to_pocctrl()` is the only custom function. It maps a pin ID to a POC register address and bit number, returning `-EINVAL` for pins without POC control.
- `r8a779h0_pin_ops` wires `pin_to_pocctrl`, `rcar_pinmux_get_bias`, and `rcar_pinmux_set_bias` into the common SoC operation hooks.

## Control flow

There is no local probe or interrupt flow. Runtime control is inverted through `r8a779h0_pinmux_info`: the common Renesas PFC driver receives a pinctrl or GPIO request, looks up a group/function/pin in these arrays, and writes the registers described here.

The generated flow is:

1. A consumer requests a named function/group, such as `avb1_rgmii` or `msiof2_txd`.
2. The common core finds the group in `pinmux_groups[]`, then applies the corresponding mux marks from the group `*_mux[]` array.
3. Each mark resolves through `pinmux_data[]` to GPSR/IPSR/MOD_SEL enum IDs.
4. Register descriptors in `pinmux_config_regs[]` tell the core which memory-mapped bitfield to update.
5. Optional pin configuration requests, such as drive strength, pull-up/down, or IO voltage, use `pinmux_drive_regs[]`, `pinmux_bias_regs[]`, and `r8a779h0_pin_to_pocctrl()`.

The function grouping is broad: audio clock; three Ethernet AVB instances; CAN FD 0-3 and CAN clock; HSCIF0-3; I2C0-3; external interrupts; MMC; MSIOF0-5; PCIe clock request; PWM0-4; QSPI0-1; SCIF0, SCIF1, SCIF3, SCIF4 and external SCIF clocks; SSI; and TPU outputs. AVB0/1 have both MII and RGMII groups; AVB2 has RGMII only. MMC and QSPI data groups use bus-width helper groups (`mmc_data1/4/8`, `qspi*_data2/4`).

## State and persistence behavior

The file has no mutable C state. Persistence is entirely hardware register state owned by the PFC block. The register descriptors point at memory-mapped PFC addresses in the `0xE605xxxx` and `0xE606xxxx` ranges. Once the common core writes GPSR/IPSR/MOD_SEL, drive, bias, or POC registers, that state persists in the controller until changed by another pinctrl/GPIO operation or reset. The `.unlock_reg = 0x1ff` field indicates the common R-Car PFC path must use the PMMR write-protection unlock sequence for protected registers.

## Dependencies and integration points

The file depends on `linux/errno.h`, `linux/io.h`, `linux/kernel.h`, and the local `sh_pfc.h` macro and type layer. Most behavior relies on the common Renesas PFC framework: macros such as `PORT_GP_CFG_*`, `PINMUX_CFG_REG`, `PINMUX_DRIVE_REG`, `PINMUX_BIAS_REG`, `SH_PFC_PIN_GROUP`, `BUS_DATA_PIN_GROUP`, and runtime helpers such as `rcar_pinmux_get_bias()`/`rcar_pinmux_set_bias()`.

The exported `r8a779h0_pinmux_info` is the integration point used by the SoC match table elsewhere in the Renesas pinctrl driver. Device-tree pinctrl states must use group and function names exactly matching the arrays in this file. GPIO numbering and pin configuration capabilities come from the generated pin tables and flags.

## Risks and edge cases

- The file is dense, macro-generated hardware data. A single wrong enum ordering, register address, bit offset, or group/mux pairing can silently configure the wrong physical pin.
- Sparse banks require care. Bank 2 omits pins 16 and 18, bank 4 has holes around 16-20 and 22, and multiple registers use `GROUP()` negative widths for reserved fields. Off-by-one mistakes in these reserved fields would misalign all following entries.
- `r8a779h0_pin_to_pocctrl()` supports only GP0[0:18], GP1[0:28], GP3[0:12], GP4[0:13], and the three AVB VDDQ pseudo-pins. Pins marked with IO voltage capability must stay aligned with this function, otherwise voltage configuration requests can fail with `-EINVAL` or hit the wrong POC bit.
- Some bias comments deserve review: in `PUEN5`, bit 1 maps `RCAR_GP_PIN(5, 1)` but the comment says `AVB0_AVTP_CAPTURE`; the surrounding bank 5 entries are AVB2 signals, so the comment appears inconsistent. This is comment-level unless generated documentation uses comments as truth.
- Shared pins are intentionally exposed under multiple logical groups, for example SCIF and HSCIF variants or PWM alternatives on CAN/I2C/audio pins. Board pinctrl states must avoid incompatible simultaneous selections.
- Non-GPIO VDDQ pins are configuration pseudo-pins, not normal GPIOs; users must not assume all `pinmux_pins[]` entries map to data registers.

## Test signals

Useful validation signals are compile-time and hardware/DT oriented. Build coverage should compile this file with the Renesas pinctrl driver enabled and catch enum or initializer mismatches. Static checks should verify that every group has matching pin and mux array lengths, every group named in a function exists, every `*_MARK` used in a mux appears in `pinmux_data[]`, and every pin with IO-voltage flags is accepted by `r8a779h0_pin_to_pocctrl()`. Runtime tests on R8A779H0 hardware should request representative pinctrl states for AVB0/1/2, QSPI, MMC, I2C, SCIF/HSCIF, CAN FD, bias, drive strength, and IO voltage, then confirm the expected GPSR/IPSR/MOD_SEL/DRV/PUEN/PUD/POC registers change.
