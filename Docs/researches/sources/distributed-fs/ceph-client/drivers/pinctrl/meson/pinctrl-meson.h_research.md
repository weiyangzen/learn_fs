# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson.h

## Purpose
This header defines the shared data model and helper macros used by Amlogic Meson pinctrl SoC descriptions and mux backends. It is the contract between table-only SoC files, common pinctrl/pinconf/GPIO code, and pinmux implementations.

## Important APIs, Types, and Macros
- `struct meson_pmx_group` names a pin group, lists its pins, and carries backend-specific mux data in `data`.
- `struct meson_pmx_func` maps a function name to its supported group names.
- `struct meson_reg_desc` and `enum meson_reg_type` describe bank-local register/bit starts for pull-enable, pull, direction, output, input, and drive-strength.
- `enum meson_pinconf_drv` defines encoded drive-strength values for 500 uA, 2500 uA, 3000 uA, and 4000 uA.
- `struct meson_bank` maps a contiguous pin range to register descriptors and IRQ metadata.
- `struct meson_pinctrl_data` packages SoC static data, mux ops, mux-private data, and optional DT parse hook.
- `struct meson_pinctrl` is the per-device runtime state shared by the core and backends.
- `FUNCTION()`, `BANK_DS()`, `BANK()`, and `MESON_PIN()` reduce boilerplate in SoC table files.
- Function declarations expose shared mux enumeration helpers, common probe, and parse hooks.

## Control Flow
This file has no executable control flow. Its structures drive runtime control flow elsewhere: SoC probe match data points to `meson_pinctrl_data`, common pinconf uses `meson_bank.regs`, and mux backends interpret `meson_pmx_group.data`.

## State and Persistence
The header defines the lifetime-bearing `struct meson_pinctrl`; actual allocation occurs in `meson_pinctrl_probe()`. Static SoC data generally has built-in or module lifetime. Hardware state persists in registers referenced by regmaps in `struct meson_pinctrl`.

## Dependencies and Integration Points
It includes Linux GPIO, pinctrl, platform device, regmap, types, and module headers. It is included by Meson common code, first-generation mux code, AXG mux code, and SoC data files.

## Risks
Macro argument order in `BANK_DS()` and `BANK()` is dense and easy to misuse; an offset transposition changes pinconf or GPIO behavior across a bank. `struct meson_pmx_group.data` is untyped, so each backend must cast it consistently. Drive-strength encodings and bit stride assumptions must remain synchronized with `meson_bit_strides` in the core.

## Test Signals
Compiler coverage across all Meson SoC files is the primary signal for structural compatibility. Runtime signals come from successful probe, correct group/function enumeration, and pinconf/GPIO behavior on representative SoCs using different mux backends and register-sharing parse hooks.
