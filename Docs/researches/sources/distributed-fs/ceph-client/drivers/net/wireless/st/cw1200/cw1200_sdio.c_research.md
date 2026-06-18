# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/cw1200_sdio.c

Purpose: SDIO bus front-end for CW1200 hardware. It powers the module, subscribes SDIO or GPIO IRQs, implements `hwbus_ops`, and calls the shared CW1200 core.

Important APIs and functions: Exports `cw1200_sdio_set_platform_data`. Defines `struct hwbus_priv`, SDIO ID table, bus copy functions, SDIO claim/release locking, IRQ handlers, `cw1200_sdio_on/off`, `cw1200_sdio_align_size`, PM wake control, `cw1200_sdio_probe`, `cw1200_sdio_disconnect`, suspend/resume hooks, and module init/exit.

Control flow: Module init powers on platform resources and registers the SDIO driver. Probe accepts function 1, allocates `hwbus_priv`, enables the SDIO function, subscribes IRQs, then calls `cw1200_core_probe`. Disconnect reverses IRQ subscription, core release, function disable, and allocation. IRQs call `cw1200_irq_handler`, either from SDIO function IRQ or a platform GPIO IRQ.

State and persistence: Uses a global platform-data pointer and global optional GPIO descriptors, so the implementation supports only one device per system. Per-device `hwbus_priv` stores SDIO function, core pointer, and platform data.

Dependencies and integration: Depends on MMC/SDIO APIs, GPIO descriptors, platform data from `linux/platform_data/net-cw1200.h`, shared `hwbus_ops`, and PM callback `cw1200_can_suspend`.

Risks: The single-device global platform-data/GPIO design is a limitation. Probe ignores the return from `cw1200_sdio_irq_subscribe` before calling core probe, which can hide IRQ setup failure. Platform-specific reset polarity and timing are critical. Suspend only requests keep-power; resume is a no-op.

Test signals: SDIO enumeration, IRQ delivery via both SDIO and GPIO modes, firmware load through aligned SDIO transfers, suspend with `MMC_PM_KEEP_POWER`, module unload/reload, and board-specific power/reset sequencing.
