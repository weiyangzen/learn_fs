<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mlx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mlx_wdt.c`

Purpose: Mellanox/NVIDIA watchdog driver for platform-data-described regmap watchdog blocks, supporting main reset watchdogs and auxiliary alarm-only watchdogs across three hardware types.

Important APIs, types, and functions: `struct mlxreg_wdt` stores watchdog core state, parent platform data, regmap, register indices, value size, and type. `mlxreg_wdt_config()` discovers action/timeout/timeleft/ping/reset registers by label. Timeout setting differs by type: type1 uses power-of-two milliseconds, type2 writes seconds, type3 writes 16-bit seconds across one or two regmap bytes. `mlxreg_wdt_check_card_reset()` reads reset-cause register for main watchdogs.

Control flow: probe obtains platform data/regmap, validates regmap value size, configures info/ops/bounds from platform identity and version, applies NOWAYOUT/start-at-boot feature flags, initializes timeout from platform health counter, optionally starts and marks `WDOG_HW_RUNNING`, checks bootstatus, and registers with stop-on-reboot/unregister.

State and persistence: state lives in parent CPLD/regmap registers. Platform data labels determine all register semantics. Type1 rounds timeout down to the actual closest power-of-two interval. Start-at-boot feature means Linux immediately enables and owns the watchdog.

Dependencies and integration points: depends on `mlxreg_core_platform_data`, regmap, platform features, watchdog core, and board-specific label conventions.

Risks and test signals: risks include missing/mislabeled platform data, timeout rounding for type1, 16-bit byte-order handling for type3, reset-cause mask semantics, and restart on active timeout change. Test all three types, main versus aux info flags, feature flags, timeleft reads, timeout restart behavior, and bootstatus detection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mlx_wdt.c -->
