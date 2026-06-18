# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.h

## Purpose
This header defines the descriptor contract between Realtek DHC SoC-specific pinctrl data files and the shared core in `pinctrl-rtd.c`. It provides structures for groups, functions, mux alternatives, electrical config metadata, special config metadata, suspend register ranges, and the top-level SoC descriptor, plus macros that make large static SoC tables concise.

## Important APIs, Types, and Functions
- `NA` is the sentinel value for unsupported offsets or current type.
- `PADDRI_4_8` and `PADDRI_2_4` encode two supported drive-strength selector models.
- `struct rtd_pin_group_desc` describes a named group and its pin list.
- `struct rtd_pin_func_desc` describes a named mux function and groups that support it.
- `struct rtd_pin_mux_desc` describes one mux function name and register value for a pin.
- `struct rtd_pin_config_desc` describes per-pin electrical config register offset, base bit, pull enable/select offsets, current, Schmitt, power, input voltage, slew rate, and high-VIL offsets.
- `struct rtd_pin_sconfig_desc` describes special per-pin/group fields such as duty cycle and separate N/P drive strengths.
- `struct rtd_reg_range` and `struct rtd_pin_range` describe register ranges saved/restored by PM hooks.
- `struct rtd_pin_desc` describes a pin's mux register offset, mask, and possible functions.
- `struct rtd_pin_reg_list` is a register/value pair for SoC data use.
- `RTK_PIN_MUX`, `RTK_PIN_CONFIG`, `RTK_PIN_CONFIG_V2`, `RTK_PIN_CONFIG_I2C`, `RTK_PIN_SCONFIG`, and `RTK_PIN_FUNC` generate descriptor initializers.
- `struct rtd_pinctrl_desc` is the top-level SoC descriptor passed to `rtd_pinctrl_probe()`.
- The header declares `rtd_pinctrl_probe()` and `realtek_pinctrl_pm_ops`.

## Control Flow
There is no executable control flow in the header. SoC-specific source files use the macros to build static arrays, then pass an `rtd_pinctrl_desc` to the core probe. The core indexes these arrays to answer pinctrl queries, set mux registers, apply pinconf register updates, and optionally save/restore PM ranges.

## State and Persistence
The header defines static descriptor state and the PM range schema. Runtime state is allocated in `pinctrl-rtd.c`. `struct rtd_pin_range` and `struct rtd_reg_range` are the persistence contract for suspend/resume register save/restore.

## Dependencies and Integration Points
The header is intended for Realtek pinctrl core and SoC descriptor files. It relies on kernel integer types, pinctrl descriptors from including C files, and platform-device declarations for `rtd_pinctrl_probe()`. The exported PM ops declaration lets SoC platform drivers attach the common suspend/resume handlers.

## Risks and Edge Cases
- There is no include guard in this snapshot, so multiple inclusion in one translation unit would redeclare structures/macros.
- Descriptor arrays are assumed by the core to be indexed by pin number for muxes and configs; SoC files must size and order them carefully.
- `NA` is `0xffffffff`; fields using unsigned offsets must compare against it before arithmetic, or overflow can produce invalid bit positions.
- The macros use compound literals for function arrays inside static initializers. This is valid in GNU C kernel style but makes lifetime and section placement dependent on compiler behavior accepted by the kernel.
- `SHIFT_LEFT()` does no masking and can overflow if caller values exceed field width.

## Test Signals
Compile all Realtek SoC descriptor files that include this header. Descriptor-focused tests should verify array sizes against pin numbers, that unsupported fields are `NA`, that mux masks include every `RTK_PIN_FUNC()` value, and that PM register ranges are 4-byte aligned because the core saves/restores `len / 4` entries.
