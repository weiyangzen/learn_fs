# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-shx3.c

Purpose: registers the prototype SH-X3 PFC block with the SuperH PFC framework.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-shx3`; the resource maps `0xffc70000-0xffc7001f`.

Control flow: an `arch_initcall` publishes the pin-controller resource before `setup-shx3.c` requests GPIO function pins for IRQ mode.

State and persistence: local state is static metadata only; hardware PFC registers hold pin selection state.

Dependencies and integration points: used by SH-X3 serial/timer setup and `plat_irq_setup_pins()`, which requests `GPIO_FN_IRQ0` through `GPIO_FN_IRQ3` in IRQ mode.

Risks: the prototype CPU has a very small PFC window and likely limited validation; unsupported pin modes will fail at request time.

Test signals: `pfc-shx3` should probe, IRQ pin requests should succeed, and external IRQ/IRL board modes should produce interrupts.
