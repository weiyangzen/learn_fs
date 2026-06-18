# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/conf.h

Purpose: Defines wl12xx private configuration structures and Soft Gemini coexistence parameter indexes.

Important APIs and types: `CONF_TX_PWR_COMPENSATION_LEN_2`, `CONF_TX_PWR_COMPENSATION_LEN_5`, `struct wl12xx_conf_rf`, `struct wl12xx_priv_conf`, and `enum wl12xx_sg_params`.

Control flow: Header only. The enum indexes into `wlcore_conf.sg.params`, and the RF arrays feed extended radio parameter commands.

State and persistence: No storage here. `main.c` creates default instances using these types, and `cmd.c` reads them while building firmware commands.

Dependencies and integration points: Used by `main.c`, `cmd.c`, and `cmd.h`. Ties wl12xx-specific SG and RF values to generic wlcore configuration.

Risks: SG enum order is an ABI between default config and firmware ACX configuration. Changing enum order without updating defaults changes coexistence behavior. RF compensation lengths must match firmware expectations.

Test signals: Bluetooth/WLAN coexistence behavior, scan under BT traffic, extended radio parameter command success, and compile-time bounds checks in `main.c`.
