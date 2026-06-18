# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.h

`sdio.h` defines the conditional SDIO interface used by b43 core code. It provides real declarations when `CONFIG_B43_SDIO` is enabled and stubs otherwise.

With SDIO enabled, `struct b43_sdio` embeds `struct ssb_bus` and stores an IRQ opaque pointer plus callback. The header declares `b43_sdio_request_irq()`, `b43_sdio_free_irq()`, `b43_sdio_init()`, and `b43_sdio_exit()`. Without SDIO support, request IRQ returns `-ENODEV`, init returns success, and free/exit do nothing.

The header has no runtime control flow beyond inline stub behavior and no persistent state except the structure contract implemented in `sdio.c`. It includes `linux/ssb/ssb.h`, forward-declares `struct b43_wldev`, and is consumed by b43 main init/exit and interrupt setup.

Risks include callers mistaking stub init success for SDIO availability. Test signals are build coverage with `CONFIG_B43_SDIO` enabled and disabled, ensuring common b43 code can call the hooks in both configurations.
