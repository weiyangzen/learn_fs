# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra-bpmp-thermal.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra-bpmp-thermal.c` is the firmware-backed thermal driver for Tegra SoCs where the BPMP coprocessor owns thermal sensing, notably Tegra186-compatible systems. It registers thermal zones for BPMP-reported sensors and forwards temperature/trip requests over MRQ_THERMAL. The source was read as a complete 328-line file.

## Important APIs, Types, and Functions

Key types are `struct tegra_bpmp_thermal` and `struct tegra_bpmp_thermal_zone`. Important functions are `tegra_bpmp_thermal_probe()`, `__tegra_bpmp_thermal_get_temp()`, `tegra_bpmp_thermal_set_trips()`, `tegra_bpmp_thermal_get_num_zones()`, `tegra_bpmp_thermal_trips_supported()`, `bpmp_mrq_thermal()`, `tz_device_update_work_fn()`, and `tegra_bpmp_thermal_remove()`. Thermal ops are selected with or without `.set_trips` depending on BPMP ABI support.

## Control Flow

Probe obtains the parent BPMP handle, queries whether `CMD_THERMAL_SET_TRIP` is supported, queries the number of zones, allocates a zone pointer array, and iterates every BPMP zone index. It probes each zone by requesting a temperature; errors other than `-EAGAIN` skip that zone. Successfully mapped zones are registered through `devm_thermal_of_zone_register()`, get a work item for updates, and are retained in `tegra->zones`. Finally the driver registers an MRQ handler. Runtime `.get_temp` sends `CMD_THERMAL_GET_TEMP`; `.set_trips` sends `CMD_THERMAL_SET_TRIP`. BPMP host-trip notifications are validated, matched to a zone index, acknowledged, and converted to `thermal_zone_device_update()` from process context via workqueue.

## State and Persistence Behavior

The driver maintains an in-memory list of registered zones and the BPMP handle. Trip state is persistent only inside BPMP firmware/hardware after `SET_TRIP` requests. Work items are per-zone and scheduled on BPMP notifications. Remove unregisters the MRQ handler but does not explicitly flush pending work in this file.

## Dependencies and Integration Points

It depends on `soc/tegra/bpmp.h`, BPMP ABI structures, parent device driver data, Device Tree thermal-zone registration, and the thermal core. It matches `nvidia,tegra186-bpmp-thermal`.

## Risks and Edge Cases

Powergated sensors can return `-EAGAIN` and are still registered, so users may see transient read failures. Zones not described in DT are skipped unless probe defers. Firmware ABI errors are collapsed to `-EINVAL`, limiting diagnostics. Pending work after MRQ unregister should be considered when changing remove paths. If BPMP does not support host trips, the driver intentionally omits `.set_trips`, so interrupt-driven updates may be reduced.

## Test Signals

Useful tests include BPMP ABI query success/failure, systems with unsupported `SET_TRIP`, powergated-zone reads returning `-EAGAIN`, MRQ host-trip notification delivery, zone registration count matching firmware, and remove/unbind tests with no later MRQ callbacks.
