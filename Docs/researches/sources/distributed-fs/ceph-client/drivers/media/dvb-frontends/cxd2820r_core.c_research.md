# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_core.c

Purpose: core CXD2820R driver layer. It owns probing, regmap setup for the two I2C register banks, DVB frontend operation dispatch, custom search behavior, I2C gate control, optional GPIO chip registration, legacy attach wrapping, and resource cleanup.

Important APIs and functions: shared helpers include `cxd2820r_wr_reg_val_mask_tab()` and `cxd2820r_gpio()`. DVB frontend callbacks dispatch to per-system files: `cxd2820r_set_frontend()`, `read_status()`, `get_frontend()`, `sleep()`, and `get_tune_settings()`. `cxd2820r_search()` implements custom DVB-T/T2 fallback. `cxd2820r_probe()` allocates `struct cxd2820r_priv`, initializes regmaps, validates chip ID `0xe1`, creates dummy client for the second I2C address, registers GPIOs if requested, copies `cxd2820r_ops`, and publishes `get_dvb_frontend`.

Control flow: legacy `cxd2820r_attach()` creates an I2C client named `cxd2820r`; normal I2C probing performs hardware validation and frontend setup. Runtime DVB operations switch on `dtv_property_cache.delivery_system`. Search alternates between DVB-T and DVB-T2 after failed locks, waits 1s for T/C or 2s for T2 in 50 ms steps, and returns success/again/error. Release unregisters the primary client for legacy attach; direct I2C users have `release = NULL`.

State and persistence: `struct cxd2820r_priv` tracks clients, regmaps, frontend, config flags, GPIO cache, cumulative BER, active delivery system, and `last_tune_failed`. State is volatile and freed on remove.

Dependencies and integration: Linux I2C, regmap range windows, DVB frontend core, GPIOLIB when enabled, and the per-system C/T/T2 translation units.

Risks and test signals: probe depends on platform data and a valid `gpio_chip_base` indirection. The legacy attach path must handle `i2c_new_client_device()` failures. Search mutates `delivery_system` to alternate T/T2, so frontend cache semantics are important. Test chip-ID rejection, second-client creation failure, GPIO registration/fallback, direct vs legacy release, I2C gate bit toggling, dispatch for invalid delivery systems, and T/T2 retry behavior.
