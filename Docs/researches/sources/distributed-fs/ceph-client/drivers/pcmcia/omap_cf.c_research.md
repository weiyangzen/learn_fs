# sources/distributed-fs/ceph-client/drivers/pcmcia/omap_cf.c

Purpose: Implements the OMAP16xx CompactFlash socket controller. It exposes CF as a static PCMCIA socket with fixed memory/attribute/I/O layout, basic reset control, IRQ/poll card detection, and OMAP1 pinmux/chipselect programming.

Important APIs and functions: Socket ops are `omap_cf_ss_init()`, `omap_cf_ss_suspend()`, `omap_cf_get_status()`, `omap_cf_set_socket()`, `omap_cf_set_io_map()`, and `omap_cf_set_mem_map()`. Runtime event functions are `omap_cf_timer()` and `omap_cf_irq()`. Probe/remove are `omap_cf_probe()` and `omap_cf_remove()`.

Control flow: Module init only registers on OMAP16xx. Probe reads platform chipselect from `platform_data`, gets IRQ and memory resource, requests a shared IRQ, remaps I/O space, reserves the CF memory region, configures OMAP CF pinmux, writes CF chipselect config, fills socket fields, and registers the socket. The timer polls card detect every two seconds while active; IRQ also calls the timer path. Socket status reports CF as ready, powered, detected, and 3.3V when present. Reset writes `CF_CONTROL_RESET`.

State and persistence: `struct omap_cf_socket` stores present/active bits, timer, platform device, physical CF base, IRQ, resource, and socket. OMAP CF controller registers and pinmux settings persist while configured.

Dependencies and integration points: Depends on OMAP1 I/O, OMAP16xx CPU detection, OMAP mux helpers, PCI I/O remap for PCMCIA-style port access, `pccard_static_ops`, and the PCMCIA socket core.

Risks: The controller only supports CF memory-card-style timing; other I/O cards may not work without external logic. Platform data is cast to an integer chipselect. Remove is in exit text because `platform_driver_probe()` prevents runtime unbind. CF conflicts with MMC1 pinmux.

Test signals: OMAP16xx boot/probe, chipselect programming, card detect polling and IRQ, reset control, static memory/attribute/I/O mapping, CF storage driver bind, and unload path for module builds.
