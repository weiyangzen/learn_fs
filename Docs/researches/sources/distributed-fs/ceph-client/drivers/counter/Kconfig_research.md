# sources/distributed-fs/ceph-client/drivers/counter/Kconfig

## Purpose
This Kconfig file defines the generic Counter subsystem and individual counter-device driver options.

## Important APIs, Types, And Functions
`config I8254` is a hidden tristate library option selecting `COUNTER` and `REGMAP`. `menuconfig COUNTER` enables generic Counter device support. Under it, options include `104_QUAD_8`, `FTM_QUADDEC`, `INTEL_QEP`, `INTERRUPT_CNT`, `MICROCHIP_TCB_CAPTURE`, `RZ_MTU3_CNT`, `STM32_LPTIMER_CNT`, `STM32_TIMER_CNT`, `TI_ECAP_CAPTURE`, and `TI_EQEP`. Each option declares platform dependencies, selected support libraries, and module names in help text.

## Control Flow
Kconfig exposes individual drivers only when `COUNTER` is enabled. Dependency expressions limit hardware-specific drivers to matching architectures or `COMPILE_TEST`. Selection clauses pull in required libraries such as `REGMAP_MMIO`, `ISA_BUS_API`, or `REGMAP`.

## State And Persistence
No runtime state exists. The selected config persists in the kernel build configuration and controls object inclusion.

## Dependencies And Integration Points
It integrates with `drivers/counter/Makefile`, Linux architecture/platform symbols, and the generic Counter subsystem. The `104_QUAD_8` option specifically depends on PC/104 x86 or compile testing plus I/O port mapping.

## Risks And Edge Cases
Incorrect dependencies can expose drivers on platforms without required I/O resources or hide compile-test coverage. Library options like `I8254` are hidden and selected by consumers, so dependency loops or missing selects can break builds. Help text module names should remain synchronized with Makefile object names.

## Test Signals
Configuration matrix tests should cover `COUNTER=n/m/y`, compile-test builds, platform-gated visibility, selected helper symbols, and expected module object names.
