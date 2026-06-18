# sources/distributed-fs/ceph-client/drivers/watchdog/mtk_wdt.c

## Purpose
`mtk_wdt.c` is the common MediaTek watchdog driver. It controls the TOPRGU watchdog, optional bark/pretimeout IRQ mode, system restart, and an integrated reset-controller interface for SoC reset lines.

## Important APIs, types, and functions
`struct mtk_wdt_dev` embeds `watchdog_device`, MMIO base, reset-controller device, lock, and DT option flags. `struct mtk_wdt_data` provides per-compatible reset counts and `WDT_SWSYSRST_EN` support. Key functions are `mtk_wdt_start`, `mtk_wdt_stop`, `mtk_wdt_ping`, `mtk_wdt_set_timeout`, `mtk_wdt_set_pretimeout`, `mtk_wdt_restart`, `mtk_wdt_isr`, and reset-controller callbacks `toprgu_reset_assert/deassert/reset`.

## Control flow
Probe maps registers, optionally requests a bark IRQ, selects watchdog info with or without pretimeout, initializes timeouts and restart priority, detects already-running hardware, registers the watchdog, registers a reset controller when match data exists, then reads DT flags controlling external reset and TOPRGU reset source selection. Start programs length, toggles IRQ/dual mode based on `pretimeout`, applies DT mode bits, and enables the watchdog. Pretimeout mode sets the hardware bark at half timeout. Restart clears IRQ reset mode and loops writing the software-reset key.

## State and persistence
State exists in watchdog length/mode/reset registers, reset-controller software-reset registers, `WDOG_HW_RUNNING`, pretimeout fields, and DT-derived booleans. Hardware state can survive firmware handoff; no nonvolatile software persistence exists. The spinlock protects shared software reset registers.

## Dependencies and integration points
It integrates watchdog core, restart handler priority, OF compatibles for many MediaTek SoCs, DT reset bindings, optional IRQ pretimeout notification, Linux reset-controller consumers, and platform PM suspend/resume.

## Risks and test signals
Risks include global `orion_wdt_info`-style option mutation avoided here but shared hardware reset registers require strict locking, half-timeout pretimeout semantics that ignore requested exact pretimeout values, writing key-protected registers incorrectly, and registering reset controller before DT flags are fully applied. Test signals include IRQ/no-IRQ probe, all compatible match-data reset counts, reset-controller assert/deassert with `has_swsysrst_en`, inherited running watchdog, restart path, suspend/resume, and DT flags `mediatek,disable-extrst` and `mediatek,reset-by-toprgu`.
