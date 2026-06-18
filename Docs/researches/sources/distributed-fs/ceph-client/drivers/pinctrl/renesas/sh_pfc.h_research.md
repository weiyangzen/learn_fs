# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/sh_pfc.h

## Purpose

`sh_pfc.h` is the shared data-model and macro header for the Renesas SuperH/R-Mobile/R-Car Pin Function Controller stack. It defines the generic SoC description structures consumed by the SH-PFC core and pinctrl layer, the enum/data-register representations used to describe pinmux topology, and a large set of macros that let per-SoC files declare thousands of pins, groups, functions, data registers, bias registers, drive-strength fields, and GPIO aliases in a compact and compile-time-checked form.

## Important APIs, Types, And Macros

`struct sh_pfc` is the central runtime object: device pointer, `struct sh_pfc_soc_info`, spinlock, mapped MMIO windows, IRQs, pin ranges, GPIO chip pointer, and saved registers. `struct sh_pfc_soc_info` is the primary static SoC contract. It contains optional operations, GPIO input/output/function ranges, IRQ maps, pin arrays, group arrays, function arrays, config registers, drive registers, bias registers, IO control registers, data registers, pinmux data, and an unlock register.

The header defines pin capability flags such as `SH_PFC_PIN_CFG_INPUT`, `OUTPUT`, pull-up/down, IO-voltage ranges, drive-strength, and `NO_GPIO`. Pin topology structures include `struct sh_pfc_pin`, `sh_pfc_pin_group`, `sh_pfc_function`, `pinmux_func`, `pinmux_cfg_reg`, `pinmux_drive_reg`, `pinmux_bias_reg`, `pinmux_data_reg`, `pinmux_irq`, `pinmux_range`, and `sh_pfc_window`. `struct sh_pfc_soc_operations` provides optional callbacks for init, bias get/set, POCCTRL lookup, and PORTCR lookup.

Macros such as `SH_PFC_PIN_GROUP`, `SH_PFC_PIN_GROUP_SUBSET`, `BUS_DATA_PIN_GROUP`, `SH_PFC_FUNCTION`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `PINMUX_DATA_REG`, `PINMUX_DRIVE_REG`, `PINMUX_BIAS_REG`, and `PINMUX_IRQ` build static descriptions with array-size validation. The `PINMUX_IPSR_*` family describes common R-Car IPSR/GPSR/MOD_SEL/physical-selector relationships. The `PORT_GP_*`, `PINMUX_GPIO_GP_ALL()`, `PINMUX_DATA_GP_ALL()`, `GP_ASSIGN_LAST()`, `PORT_*`, `PINMUX_DATA_ALL()`, `PORT_ASSIGN_LAST()`, `GPIO_FN()`, and `PINMUX_NOGP_ALL()` macro families generate repetitive port and GPIO data from per-SoC `CPU_ALL_*` macros.

## Control Flow And Use Pattern

Per-SoC files include this header, define enums and `CPU_ALL_GP`/`CPU_ALL_PORT`/`CPU_ALL_NOGP` expansion macros as needed, use the helper macros to build static arrays, and export a `const struct sh_pfc_soc_info`. The SH-PFC core selects one such `soc_info` for a platform device, maps windows and initializes `struct sh_pfc`, then the pinctrl layer uses the arrays and callbacks to register pinctrl, pinmux, pinconf, GPIO, and IRQ behavior.

The macros are deliberately declarative. For example, a mux function is represented in `pinmux_data` as a mark followed by all enum IDs needed to select it, terminated by zero. Config/data register macros encode field widths and enum choices so the core can translate a mark into register writes. Bias, drive, and voltage support are opt-in per pin through capability flags plus matching register/callback data.

## State And Persistence

This header defines state shapes but owns no storage. Runtime state is allocated by core C files in `struct sh_pfc`; static SoC data is usually read-only. Persistence across suspend/resume depends on the core's use of `saved_regs` and platform-specific behavior, not on this header.

## Dependencies And Integration Points

The header depends on Linux bit helpers, pinconf generic enums, spinlocks, and stringification. It declares many external `sh_pfc_soc_info` objects for supported Renesas SoCs and declares bias helper functions implemented in `pinctrl.c`. It is the contract between SoC table files, the SH-PFC core, the pinctrl integration layer, and optional GPIO support.

## Risks

Most correctness is compile-time and table-driven. Macro misuse can create wrong enum order, wrong field widths, or mismatched pin/mux arrays that still compile if not caught by the embedded `BUILD_BUG_ON_ZERO` checks. Several macros depend on externally defined `CPU_ALL_*` expansion contracts, which can be hard to inspect. The dense data representation makes review difficult: a single wrong enum ID can route a peripheral to the wrong register field. Capability flags must agree with actual bias/drive/voltage register data or pinconf will either reject valid configs or permit invalid ones.

## Test Signals

Build coverage is a major signal because the macros intentionally embed static assertions. Runtime signals include successful `sh_pfc_register_pinctrl()` on SoCs using GP, PORT, and NOGP styles; pinmux state application across IPSR/GPSR/MOD_SEL patterns; bias helper behavior for both R-Car and R-Mobile register layouts; and pinconf support only where the declared capability flags and register tables agree.
