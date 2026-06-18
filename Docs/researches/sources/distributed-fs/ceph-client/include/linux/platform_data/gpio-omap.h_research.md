
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpio-omap.h

## Purpose
This header defines register offsets and platform data for OMAP GPIO banks across OMAP1, OMAP7xx, OMAP16xx, OMAP2+, and OMAP4 variants. It lets one GPIO driver handle multiple register layouts and PM capabilities.

## Important APIs And Types
The file declares many register offset constants for MPUIO and SoC-specific GPIO revisions, `OMAP34XX_NR_GPIOS`, and `OMAP_MAX_GPIO_LINES`. `struct omap_gpio_reg_offs` maps logical operations to actual register offsets and includes `irqenable_inv`. `struct omap_gpio_platform_data` supplies bank type, bank width, bank stride, debounce clock requirement, context-loss behavior, MPUIO flag, non-wakeup GPIO mask, register-offset table, and optional context-loss callback.

## Control Flow, State, And Persistence
The header is declarative. The GPIO driver uses the offset table to read/write data, direction, debounce, IRQ status/mask, wakeup, edge/level detect, and set/clear dataout registers. Runtime state includes configured GPIO direction/value/IRQ modes and saved context for banks that lose context.

## Dependencies And Integration Points
It integrates OMAP platform devices, memory-mapped I/O, GPIO, IRQ, debounce clock, and PM context-loss handling. The assembler guard allows register constants to be reused outside C contexts.

## Risks And Test Signals
Risks include wrong offset table for a bank, inverted IRQ enable semantics, missing debounce clock, non-wakeup GPIO mask errors, and failed context restore after idle/suspend. Test signals include GPIO line read/write, IRQ edge and level detection, debounce behavior, wakeup source tests, MPUIO-specific register access, and suspend/resume context restoration.
