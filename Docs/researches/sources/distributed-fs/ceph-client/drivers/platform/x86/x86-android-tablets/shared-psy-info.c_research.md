# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.c

Purpose: shared power-supply, battery, charger, regulator, and USB-ID platform data for x86 Android tablet board-description files. It avoids duplicating common simple-battery software nodes, fuel-gauge supplier links, bq24190 VBUS regulator setup, module preload lists, and generic `intel-int3496` platform-device properties.

Important APIs/types/functions: exports `tusb1211_chg_det_psy`, `bq24190_psy`, `bq25890_psy`, `fg_bq24190_supply_node`, `fg_bq25890_supply_node`, `generic_lipo_4v2_battery_node`, `generic_lipo_4v2_battery_swnodes`, `generic_lipo_hv_4v35_battery_node`, `generic_lipo_hv_4v35_battery_swnodes`, `bq24190_pdata`, `bq24190_modules`, and `int3496_pdevs`. Internally it defines OCV capacity tables for 4.2 V and 4.35 V LiPo packs and a regulator consumer supply that maps bq24190 VBUS to `intel-int3496`.

Control flow: no runtime control flow exists in this file; board files reference the exported arrays and nodes during DMI-selected device instantiation. When a bq24190 client is registered with `bq24190_pdata`, its VBUS regulator is exposed with constraints that allow status changes by the `intel-int3496` consumer. `int3496_pdevs` provides a ready-made platform device with Bay Trail GPIOs for VBUS, mux, and ID pin handling.

State and persistence: state is static kernel data. Battery OCV tables and software-node properties are read by downstream drivers at device registration time. Hardware persistence is indirect through regulator framework consumers and power-supply relationships.

Dependencies/integration: depends on Linux property/software-node APIs, regulator machine constraints, bq24190 charger platform data, platform-device info, GPIO software nodes from `x86-android-tablets`, and power-supply driver conventions for `supplied-from` and `monitored-battery`.

Risks: exported power-supply names must match actual driver names, especially `bq25890-charger-0` and `bq24190-charger`. OCV tables are generic approximations; using the wrong battery node can skew reported capacity. `int3496_pdevs` hardcodes Bay Trail GPIO references and is suitable only for boards with that wiring. Module preload strings must remain synchronized with driver names needed for IRQ and VBUS regulator availability.

Test signals: check that fuel gauges show correct `supplied_from` links, charger drivers bind with monitored-battery data, `intel-int3496` can enable/disable bq24190 VBUS, USB-ID role changes work on boards using `int3496_pdevs`, and battery capacity curves look plausible across charge/discharge.
