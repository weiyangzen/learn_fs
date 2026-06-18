# sources/distributed-fs/ceph-client/drivers/pcmcia/pxa2xx_sharpsl.c

Purpose: Provides Sharp SL-C7xx/Zaurus board-specific PCMCIA/CF control using SCOOP companion-chip registers. It supplies low-level socket operations for the generic PXA2xx PCMCIA driver, with an alternate Collie path using SA11xx base glue.

Important APIs and functions: Key callbacks are `sharpsl_pcmcia_hw_init()`, `sharpsl_pcmcia_socket_state()`, `sharpsl_pcmcia_configure_socket()`, `sharpsl_pcmcia_socket_init()`, and `sharpsl_pcmcia_socket_suspend()`. `sharpsl_pcmcia_init()` creates a `pxa2xx-pcmcia` platform device carrying `sharpsl_pcmcia_ops`; under `CONFIG_SA1100_COLLIE`, `pcmcia_collie_init()` calls `sa11xx_drv_pcmcia_probe()`.

Control flow: Init verifies `platform_scoop_config`, sets the socket count from its SCOOP device array, allocates a platform device, attaches low-level ops as platform data, sets the parent device, and adds it. Socket state reads SCOOP CPR/CSR, manages CDR and saved voltage-sense bits, then fills PCMCIA state flags. Configure validates Vcc/Vpp, computes new SCOOP MCR/CPR/CCR/IMR values, applies machine-specific power-bit differences for Spitz/Borzoi/Akita, and writes changed registers under local IRQ disable.

State and persistence: Persistent board state lives in SCOOP registers and per-SCOOP `keep_vs`/`keep_rd` fields used to preserve voltage-sense/reset behavior across power/card-detect transitions. The platform device persists until module exit.

Dependencies and integration points: Depends on Sharp SCOOP platform data, `machine_is_*()` board checks, `pxa2xx_base` or `sa11xx_base`, and common SoC PCMCIA callbacks.

Risks: Power controls are shared and board-specific, so incorrect socket index handling can affect the wrong slot. The code accepts 3.3V/5V Vcc but rejects independent Vpp; CF cards needing other Vpp modes are unsupported. IRQ masking is derived from current `skt->status`, so stale status could change event enables.

Test signals: Probe on supported Zaurus boards, correct socket count, card detect/eject, 3.3V and 5V power paths, reset sequencing, suspend powerdown, and Collie-specific SA11xx registration when configured.
