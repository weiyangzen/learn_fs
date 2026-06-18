# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.c

`sdio.c` is the SDIO transport glue that lets b43 operate over an SSB bus backed by an SDIO function. It handles probing, chip-id extraction, SSB bus registration, interrupt dispatch, and SDIO driver registration.

Important functions include `b43_sdio_get_quirks()`, `b43_sdio_request_irq()`, `b43_sdio_free_irq()`, `b43_sdio_probe()`, `b43_sdio_remove()`, `b43_sdio_init()`, and `b43_sdio_exit()`. Probe parses tuple code `0x80` for `HNBU_CHIPID`, sets a 64-byte block size, enables the SDIO function, allocates `struct b43_sdio`, and registers an SSB SDIO bus with any vendor/device quirk. IRQ dispatch ignores interrupts before `B43_STAT_STARTED`, releases the SDIO host while invoking the b43 handler, then reclaims it.

Runtime state is `struct b43_sdio` stored with `sdio_set_drvdata()`, including the embedded `ssb_bus` and IRQ callback state. Resource cleanup unwinds through labels to release host claims, disable the function, unregister SSB, and free memory. Integration points are Linux MMC/SDIO APIs, SSB SDIO registration, and b43 module init/interrupt paths in `main.c`.

Risks include tuple bounds assumptions, host-claim imbalance, IRQ teardown races, and SDIO deadlocks if the release/reclaim pattern changes. Test signals include `CONFIG_B43_SDIO` builds, probe/remove fault injection, IRQ delivery after start only, and module load/unload.
