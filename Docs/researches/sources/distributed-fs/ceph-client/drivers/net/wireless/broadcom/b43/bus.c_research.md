# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.c

This file implements b43’s bus abstraction by wrapping BCMA and SSB devices in a common `struct b43_bus_dev`. The rest of b43 uses the vtable in that object instead of directly calling BCMA or SSB APIs.

For BCMA, wrappers call core enable/disable, enabled-state, 16/32-bit MMIO, and block I/O APIs; `b43_bus_dev_bcma_init()` fills bus type, native device, callbacks, Linux device/DMA device, IRQ, board/chip/core IDs, SPROM pointer, and a BCM47XX BCM4716 write-flush quirk. BCMA bus powerdown/powerup currently return 0 with native calls commented out. For SSB, equivalent wrappers call SSB bus power, device enable/disable, MMIO, and block I/O APIs; `b43_bus_dev_ssb_init()` copies the corresponding metadata from `struct ssb_device`.

`b43_bus_get_wldev()` and `b43_bus_set_wldev()` bridge native bus drvdata to b43 core state. State is one allocated `b43_bus_dev` per core plus copied metadata; nothing is persisted on disk.

Dependencies are BCMA, SSB, optional BCM47XX platform data, and b43 core headers. Risks are incorrect DMA device/IRQ/SPROM metadata, incomplete BCMA power-management semantics, wrong host quirk detection, or using the wrong native union member. Test signals include BCMA and SSB probe, drvdata round-trips, register I/O through b43 wrappers, correct board/chip/core IDs, and the BCM47XX write-flush path on affected hardware.
