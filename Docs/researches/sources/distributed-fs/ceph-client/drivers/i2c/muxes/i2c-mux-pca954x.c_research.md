# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca954x.c

Purpose: I2C mux/switch driver for NXP PCA954x/PCA984x and compatible Maxim parts. It exposes downstream channels as child adapters, writes the single mux register through the parent I2C bus, supports regulator and reset resources, optional nested IRQ domains, sysfs idle-state policy, and resume reinitialization.

Important APIs/types/functions: `enum pca_type`, `struct chip_desc`, and `chips[]` describe channel count, mux/switch mode, enable bits, IRQ support, and optional device identity. `struct pca954x` stores `last_chan`, `idle_state`, client, IRQ domain, supply, reset, and chip data. `pca954x_reg_write()` uses `__i2c_smbus_xfer()` to avoid recursive adapter locking. `pca954x_select_chan()`, `pca954x_deselect_mux()`, `pca954x_irq_setup()`, `pca954x_irq_handler()`, `pca954x_init()`, `pca954x_probe()`, and `pca954x_resume()` are the main behavior.

Control flow: Probe checks SMBus byte capability, allocates an `i2c_mux_core`, enables supply, deasserts reset, selects chip data from firmware or ID table, validates device ID for PCA984x, reads idle policy, initializes the register, sets up nested IRQs, adds one adapter per channel, requests the threaded IRQ, and creates `idle_state`. Transfers select/deselect through mux callbacks. Resume calls `pca954x_init()` to restore hardware.

State and persistence: Hardware state is the mux register plus optional MAX7357 config. Software caches `last_chan` and `idle_state`; sysfs updates use `READ_ONCE/WRITE_ONCE` and parent segment locking. IRQ mappings live until cleanup, and regulator enable is balanced in cleanup.

Dependencies/integration: I2C core, `i2c-mux`, SMBus, firmware properties, regulator, reset/GPIO, IRQ domain, and PM sleep ops. Integrates with OF and I2C ID matching.

Risks: Direct SMBus access must remain non-recursive. `last_chan` must be cleared on failed writes and disconnect. IRQ status decoding assumes interrupt bits start at offset 4 and child IRQs are level-low. MAX7357 enhanced features silently degrade if byte-data SMBus is unsupported.

Test signals: Expected child adapter count per compatible; valid and invalid `idle_state`; suspend/resume restoration; IRQ routing for interrupt-capable chips; error paths for missing regulator, bad ID, unsupported SMBus, and adapter-add rollback.
