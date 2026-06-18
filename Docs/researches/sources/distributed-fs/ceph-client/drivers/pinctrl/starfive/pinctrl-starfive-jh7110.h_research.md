# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.h

## Purpose
This header defines the contract between the common JH7110 pinctrl driver and the SYS/AON instance files. It contains shared runtime state, per-instance register descriptions, callback hooks, and exported helper declarations.

## Important APIs, types, and functions
`struct jh7110_pinctrl` stores device, gpiochip, pin range, raw spinlock, MMIO base, pinctrl device, group-registration mutex, SoC info, and optional saved register buffer. `struct jh7110_gpio_irq_reg` describes IRQ register offsets. `struct jh7110_pinctrl_soc_info` supplies pins, GPIO count, DOUT/DOEN/GPI/GPIOIN register bases and masks, IRQ registers, saved-register count, and callbacks for one-pin muxing, padcfg base lookup, chained IRQ handling, and IRQ hardware init. Declared exports are `jh7110_set_gpiomux()`, `jh7110_pinctrl_probe()`, `jh7110_from_irq_desc()`, and `jh7110_pinctrl_pm_ops`.

## Control flow
Instance files instantiate `jh7110_pinctrl_soc_info` and attach it to OF match data. The common probe consumes that structure, and later calls the function pointers while serving pinmux, GPIO, IRQ, and PM operations.

## State and persistence behavior
The header defines but does not allocate state. The presence of `saved_regs` and `nsaved_regs` establishes the suspend/resume persistence model used by the common implementation.

## Dependencies and integration points
The header includes Linux pinconf and pinmux definitions and is included by all JH7110 source files. It is the integration point that lets SYS and AON vary register layout without duplicating common pinctrl/gpio/irq logic.

## Risks
The callback contract allows NULL callbacks, and the common implementation sometimes treats missing callbacks as no-op success. Register masks and bases are trusted, so a bad `jh7110_pinctrl_soc_info` can corrupt unrelated registers. `saved_regs` is a flat prefix copy, so instance files must choose `nsaved_regs` carefully.

## Test signals
Compile tests should include both instance files and the common file. Review checks should verify every `jh7110_pinctrl_soc_info` fills all fields required by enabled features, especially IRQ register bases, GPIO masks, saved register count, and padcfg callback behavior.
