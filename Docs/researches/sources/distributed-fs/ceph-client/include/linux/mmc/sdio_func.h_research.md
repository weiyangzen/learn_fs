# sources/distributed-fs/ceph-client/include/linux/mmc/sdio_func.h

## Purpose
`mmc/sdio_func.h` defines the Linux SDIO function device model and driver API. It exposes function descriptors, driver registration helpers, host claim/release, function enable/disable, block-size setup, IRQ registration, aligned transfer sizing, byte/word/dword I/O, buffer I/O, function-0 I/O, PM flags, and retune controls.

## Important APIs, Types, And Functions
Key types are `sdio_irq_handler_t`, `struct sdio_func_tuple`, `struct sdio_func`, and `struct sdio_driver`. Matching helpers are `SDIO_DEVICE()` and `SDIO_DEVICE_CLASS()`. Registration helpers include `sdio_register_driver()`, `__sdio_register_driver()`, `sdio_unregister_driver()`, and `module_sdio_driver()`. I/O APIs include `sdio_claim_host()`, `sdio_release_host()`, `sdio_enable_func()`, `sdio_disable_func()`, `sdio_set_block_size()`, `sdio_claim_irq()`, `sdio_release_irq()`, `sdio_align_size()`, `sdio_readb/w/l()`, `sdio_memcpy_fromio()`, `sdio_readsb()`, `sdio_writeb/w/l()`, `sdio_writeb_readb()`, `sdio_memcpy_toio()`, `sdio_writesb()`, `sdio_f0_readb()`, and `sdio_f0_writeb()`.

## Control Flow And State
An SDIO driver registers a `struct sdio_driver` with probe/remove/shutdown callbacks and an ID table. The core creates one `struct sdio_func` per enumerated function and tracks card pointer, function number, class/vendor/device IDs, max/current block sizes, enable timeout, presence state, DMA-capable scratch buffer, revision/info strings, and unknown CIS tuples. Drivers claim the host before sequences of I/O, enable the function, set block size, perform CMD52/CMD53-backed I/O, optionally claim IRQs, set PM flags, and release retune holds when done.

## Dependencies And Integration Points
Dependencies include the device model, module device tables, and MMC PM flags. Integration points include SDIO bus matching, SDIO IDs, MMC host claiming, retuning, suspend/resume, SDIO IRQ thread/work handling, and function drivers such as WLAN, Bluetooth, GPS, and vendor-specific devices.

## Risks And Test Signals
Risks include unclaimed-host I/O, IRQ handler lifetime races, DMA-unsafe buffers, block size larger than function maximum, leaked CIS tuples, PM flags unsupported by host, and retune held across long operations. Test signals include SDIO driver probe/remove, host claim lockdep checks, function enable/disable, byte/block I/O, IRQ storms and release races, suspend wake tests, retune hold/release tests, and module registration/unregistration.
