<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.c

Purpose: implements the Rockchip RK3288/RK3328/RK3399 crypto accelerator platform driver, device list, runtime PM, IRQ completion, debugfs stats, and algorithm registration.

Important APIs and functions: `get_rk_crypto()` rotates the global device list and returns a device for algorithm requests. `rk_crypto_get_clks()` bulk-gets clocks and downclocks named variant clocks above allowed maximums. Runtime PM suspend disables clocks and asserts reset; resume enables clocks and deasserts reset. `rk_crypto_irq_handle()` acknowledges interrupts, records DMA error status, and completes the active request. `rk_crypto_register()` registers all skcipher and ahash engine algorithms; `rk_crypto_unregister()` reverses this.

Control flow: probe allocates device state, fetches variant data, resets hardware, maps MMIO, gets clocks/IRQ, allocates and starts a crypto engine, initializes runtime PM, adds the device to a global list, and registers algorithms/debugfs only for the first device. Remove deletes the device and unregisters algorithms/debugfs when the last device is gone.

State and persistence: global `rocklist` stores devices and optional debugfs dentries. Each `rk_crypto_info` stores clocks, reset, MMIO, IRQ, engine, completion, status, and request count. Algorithm templates store per-algorithm stats and a pointer to the first registered device.

Dependencies and integration: OF compatibles, reset controls, clocks, runtime PM, IRQs, crypto engine, debugfs, and extern algorithm templates from skcipher/ahash files.

Risks and test signals: unregister unwind has index mistakes (`rk_cipher_algs[i]` used inside a loop over `k`) and may unregister wrong entries after partial failure. Algorithm templates keep one `dev` pointer even when requests rotate across devices. Test multi-device probe/remove, runtime PM autosuspend, IRQ timeout/error, debugfs output, partial registration failure, and all registered algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.c -->
