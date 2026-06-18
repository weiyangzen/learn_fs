<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pcmciamtd.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pcmciamtd.c

Purpose: PCMCIA memory-card MTD driver for linear flash, SRAM, or ROM cards, including cards larger than a single host memory window.

Important APIs, types, and functions: `struct pcmciamtd_dev` tracks the PCMCIA device, mapped window, current offset, map, MTD, VPP, and name. Module parameters control bank width, speed, forced size, VPP, and memory type. Key functions include `remap_window()`, remapping/direct read/write/copy hooks, `pcmciamtd_set_vpp()`, CIS tuple parsers, `card_settings()`, `pcmciamtd_config()`, `pcmciamtd_probe()`, and `pcmciamtd_detach()`.

Control flow: probe allocates device state and runs config. Config parses CIS/product data, sets map size/width/name, requests the largest possible common-memory window by shrinking on failure, ioremaps it, enables the PCMCIA device, probes RAM/ROM or JEDEC/CFI flash, switches to faster direct hooks if the whole MTD fits in the window, registers the MTD, and logs `mtdN`. Detach unregisters/destroys the MTD, releases the PCMCIA window/device, and frees state.

State and persistence: persistent state is card memory contents. Runtime state includes current remapped card offset, VPP refcount, module parameter choices, MTD pointer, and PCMCIA resource window.

Dependencies and integration points: PCMCIA core/CIS parsing, MTD map probes, map IO hooks, and optional anonymous card matching.

Risks: window remapping must be correct across reads/writes spanning window boundaries. VPP values can be dangerous. Card removal returns zero data or drops writes through DEV_REMOVED checks. Test signals are CIS parsing, forced RAM/ROM modes, large-card remap reads/writes, direct-mode switch, suspend/resume callbacks, and hot removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pcmciamtd.c -->
