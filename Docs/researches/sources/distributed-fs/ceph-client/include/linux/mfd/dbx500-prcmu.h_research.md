# sources/distributed-fs/ceph-client/include/linux/mfd/dbx500-prcmu.h

Purpose: This header is the generic Ux500 PRCMU public API wrapper. It defines common PRCMU constants, firmware version metadata, wakeup and EPOD identifiers, OPP and DDR power-state enums, and inline wrappers that dispatch to DB8500 implementations when `CONFIG_UX500_SOC_DB8500` is enabled.

Important APIs, types, and functions: Important definitions include `PRCMU_WAKEUP()` and `enum prcmu_wakeup_index`, EPOD IDs and EPOD states, CLKOUT source IDs, watchdog IDs, APE/ARM/DDR OPP enums, firmware project IDs, and `struct prcmu_fw_version`. Inline wrappers include `prcmu_early_init`, `prcmu_set_power_state`, `prcmu_get_power_state_result`, `prcmu_set_epod`, `prcmu_enable_wakeups`, `prcmu_disable_wakeups`, ABB event helpers, and many additional wrappers/prototypes later in the file for clocks, resets, regulator-like domains, watchdog, modem, thermal, and IRQ registration. If DB8500 support is disabled, the API provides stubs or `-ENOSYS` style behavior where applicable.

Control flow, state, and persistence: This header has wrapper control flow only. The real state machine is the PRCMU firmware backend, but callers see stable generic names. Wakeup masks, EPOD state, OPP state, DDR power state, firmware version data, and watchdog state are persistent hardware/firmware state, not stored in this header.

Dependencies and integration points: It includes interrupt, notifier, err, device-tree clock IDs, and the DB8500-specific header. It integrates platform code with clock, reset, power-domain, regulator, suspend, and thermal subsystems while hiding DB8500 backend names.

Risks and test signals: Risks include building callers against generic APIs when the backend is disabled, stale project IDs, conflicts with unprefixed EPOD IDs, and diverging DB8500 wrapper signatures. Test signals include compile coverage with and without DB8500 config, suspend/resume and wakeup tests, EPOD/clock/reset smoke tests, and firmware version parsing for DB8500 versus DBX540 offsets.
