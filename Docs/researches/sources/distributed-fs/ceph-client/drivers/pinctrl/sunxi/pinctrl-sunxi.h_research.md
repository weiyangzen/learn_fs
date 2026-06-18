<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.h

## Purpose
Defines the shared descriptor and register-layout contract for Allwinner/sunxi pinctrl drivers. It gives SoC-specific files the macros and types needed to describe pins, functions, IRQ mappings, variants, IO-bias behavior, and controller initialization.

## Important APIs, Types, And Functions
Important constants define bank bases `PA_BASE` through `PN_BASE`, bank/register sizes, mux/data/drive/pull field widths, IRQ register offsets, debounce offsets, mux values for input/IRQ/disabled, variant flags, IO-bias registers, and the bank K extended offset. Core types are `struct sunxi_desc_function`, `struct sunxi_desc_pin`, `struct sunxi_pinctrl_desc`, `struct sunxi_pinctrl_function`, `struct sunxi_pinctrl_group`, `struct sunxi_pinctrl_regulator`, and `struct sunxi_pinctrl`. Descriptor macros include `SUNXI_PIN`, `SUNXI_PIN_VARIANT`, `SUNXI_FUNCTION`, `SUNXI_FUNCTION_VARIANT`, `SUNXI_FUNCTION_IRQ`, and `SUNXI_FUNCTION_IRQ_BANK`. Inline helpers compute IRQ config/control/status/debounce and group config registers.

## Control Flow
The header has no standalone execution. SoC files populate `struct sunxi_pinctrl_desc` and call `sunxi_pinctrl_init` or `sunxi_pinctrl_init_with_flags`; dynamic DT-table users call `sunxi_pinctrl_dt_table_init`. Runtime code uses the inline IRQ helpers when programming or handling each interrupt.

## State And Persistence Behavior
The descriptor structs are usually static, read-only SoC data. `struct sunxi_pinctrl` is the mutable per-device state container for MMIO, pinctrl/gpio/IRQ registrations, function/group tables, regulator references, locks, flags, and calculated layout parameters. The header also encodes persistent hardware ABI expectations such as bank numbering and bitfield widths.

## Dependencies And Integration Points
Depends on Linux pinctrl descriptors, spinlocks, regulators, irqdomains, gpiochips, and device/platform data. It is consumed by `pinctrl-sunxi.c` and many Allwinner SoC pin description files.

## Risks And Edge Cases
Changing constants or packed assumptions here affects every sunxi pinctrl implementation. `SUNXI_PINCTRL_MAX_BANKS` and the fixed `regulators[11]` array must stay aligned with supported bank counts. Variant mask bits share `flags` with layout-control bits, so new variants must not collide with `SUNXI_PINCTRL_NEW_REG_LAYOUT`, `PORTF_SWITCH`, or `ELEVEN_BANKS`.

## Test Signals
Compile all sunxi pinctrl users, probe controllers with legacy and new layouts, validate bank K and eleven-bank offsets, exercise IRQ bank maps, variant-only pins/functions, IO-bias variants, and generated DT-table initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.h -->
