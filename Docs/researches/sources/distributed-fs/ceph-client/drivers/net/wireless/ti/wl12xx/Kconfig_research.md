# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/Kconfig

Purpose: Defines the kernel configuration option for the wl12xx driver.

Important APIs and symbols: `config WL12XX` is a tristate named "TI wl12xx support"; it depends on `MAC80211` and selects `WLCORE`.

Control flow: No runtime control flow. Build selection determines whether the wl12xx module is compiled.

State and persistence: Kconfig state is build configuration, not runtime state. The help text explicitly excludes wl1251 support and points users to the separate wl1251 driver.

Dependencies and integration points: Integrates with the kernel wireless driver Kconfig tree and wlcore common library.

Risks: Missing `select WLCORE` would break linkage because wl12xx delegates most runtime logic to wlcore. Confusing wl12xx with wl1251 can lead to unsupported hardware selection.

Test signals: Kernel config resolution, module build, and dependency selection for `MAC80211`/`WLCORE`.
