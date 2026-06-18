# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/sdio.c

Purpose: Provides the SDIO bus binding for the wl1251 core driver, including SDIO memory access, ELP access, interrupts, power/runtime PM, probe/remove, and module registration.

Important APIs and functions: Core bus operations are `wl1251_sdio_read()`, `wl1251_sdio_write()`, `wl1251_sdio_read_elp()`, `wl1251_sdio_write_elp()`, `wl1251_sdio_set_power()`, IRQ enable/disable variants, and `wl1251_sdio_probe()/remove()`. `struct wl1251_sdio` stores the `sdio_func` and cached ELP value.

Control flow: Probe allocates wl1251 hw, allocates bus-private data, enables the SDIO function, sets block size, configures optional OF EEPROM flag and dedicated IRQ, selects dedicated line IRQ or SDIO IRQ operations, initializes/registers mac80211, stores drvdata, and drops runtime PM usage. Power on gets runtime PM, enables function, and power off disables function and puts runtime PM. Interrupt callbacks queue wl1251 IRQ work.

State and persistence: Maintains `wl->if_priv`, dynamic `wl1251_sdio`, `wl->irq`, `wl->use_eeprom`, and the cached `elp_val` required for SDIO RAW ELP reads. No persistent storage.

Dependencies and integration points: Implements `wl1251_if_operations` for the shared core in `main.c`. Integrates with Linux MMC/SDIO, OF IRQ lookup, runtime PM, and mac80211 registration.

Risks: `wl1251_sdio_ops` is a static struct mutated at probe time to choose IRQ operations, which can be unsafe for multiple devices with different IRQ modes. Some SDIO enable/disable return values are not checked in power paths. Remove always calls `sdio_release_irq()` even when dedicated line IRQ was used.

Test signals: SDIO probe/remove, runtime suspend/resume, dedicated IRQ and SDIO IRQ variants, ELP wake on SDIO, firmware boot, and repeated start/stop cycles.
