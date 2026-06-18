# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/Makefile

## Purpose
The SH4A `Makefile` selects subtype setup, clock, pinmux, SMP, perf, and hardware breakpoint support for SH4A CPUs.

## Important APIs, Types, And Functions
It maps CPU subtypes SH7757, SH7763, SH7770, SH7780, SH7785, SH7786, SH7343, SH7722, SH7723, SH7724, SH7734, SH7366, and SHX3 to setup objects. It maps the same family to clock objects, pinmux objects under `CONFIG_GPIOLIB`, `smp-shx3.o` under SMP, `perf_event.o`, and `ubc.o`.

## Control Flow
Kbuild selects exactly the objects matching Kconfig. Clock objects are always appended through `obj-y += $(clock-y)`, while pinmux/perf/ubc are gated by feature configs.

## State And Persistence
No runtime state; it controls link composition.

## Dependencies And Integration Points
It integrates SH4A Kconfig with setup, clock, pinmux, SMP, perf, and UBC subsystems. SH7786 and SHX3 also pull `intc-shx3.o`.

## Risks
Object selection errors are boot-critical because setup and clock files define required `plat_*` and `arch_clk_init` hooks. Pinmux gating by `CONFIG_GPIOLIB` can change board peripheral behavior.

## Test Signals
Subtype build matrix coverage, link checks for each CPU, and boot smoke tests per subtype validate this file.
