# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_thermal.c

Purpose: registers the adapter as a Linux thermal zone and reports firmware-provided board temperature and optional critical trip temperature.

Important APIs/functions: `cxgb4_thermal_init`, `cxgb4_thermal_remove`, internal `cxgb4_thermal_get_temp`, `cxgb4_thermal_ops`, and global `trip` configured as `THERMAL_TRIP_CRITICAL`.

Control flow: init queries firmware for max temperature threshold; if unavailable it registers with zero trips, otherwise it stores the threshold in millidegrees Celsius. It registers a thermal zone named `cxgb4_<adapter-name>`, enables it, and unwinds registration on enable failure. The get-temp callback queries firmware diagnostic temperature and returns millidegrees Celsius.

State and persistence: `adap->ch_thermal.tzdev` holds the registered thermal zone pointer. Firmware values are queried on demand; no temperature history is stored.

Dependencies/integration: depends on Chelsio `t4_query_params` firmware parameters and Linux thermal zone APIs. Called from adapter bring-up and removal paths.

Risks: `cxgb4_thermal_get_temp` returns `-1` instead of a specific errno for firmware failure or zero value. The global `trip` object is shared across adapters and its temperature is overwritten at init time. Enable failure unregisters but does not explicitly clear `tzdev`.

Test signals: firmware threshold present/absent, temperature query failure, multiple adapters with different thresholds, thermal zone registration and removal, and driver unload with registered zone.
