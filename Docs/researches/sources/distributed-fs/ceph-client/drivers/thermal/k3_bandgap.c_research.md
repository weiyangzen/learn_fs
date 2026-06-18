# sources/distributed-fs/ceph-client/drivers/thermal/k3_bandgap.c

Purpose: TI K3 AM654 VTM bandgap thermal driver. It maps the VTM register block, discovers the hardware sensor count from `K3_VTM_DEVINFO_PWR0_OFFSET`, enables each temperature sensor, registers one OF thermal zone per sensor, and exposes hwmon sysfs for userspace monitoring.

Important APIs/types/functions: `struct k3_bandgap` stores the MMIO base; `struct k3_thermal_data` stores per-sensor offsets and thermal-zone state. `vtm_get_best_value()` implements the silicon erratum workaround by averaging the closest pair of three consecutive ADC samples. `k3_bgp_read_temp()` masks the 10-bit `DTEMP` field, validates it against `K3_VTM_ADC_BEGIN_VAL..K3_VTM_ADC_END_VAL`, and indexes `k3_adc_to_temp[]`. `k3_thermal_get_temp()` is the thermal framework callback. `k3_bandgap_probe()` allocates state, maps resources, enables runtime PM, programs sensor control bits, registers zones, and adds hwmon.

Control flow: probe validates lookup-table length, maps MMIO, powers the device with `pm_runtime_get_sync()`, reads the sensor count, allocates per-sensor data, sets `SOC`, `CLRZ`, and `CLKON_REQ`, clears `CBIASSEL`, then calls `devm_thermal_of_zone_register()` for each ID. Runtime reads go thermal zone -> `k3_thermal_get_temp()` -> `k3_bgp_read_temp()` -> MMIO samples -> table conversion.

State/persistence: only MMIO enable bits and runtime PM usage persist while the driver is bound; per-sensor state is devm-managed. Remove drops runtime PM. Dependencies/integration: platform driver matched by `ti,am654-vtm`, thermal OF trip parsing, `thermal_hwmon.h`, MMIO resources, runtime PM.

Risks: invalid hardware ADC codes return `-EINVAL`; sensor count is trusted from hardware; no explicit IRQ/trip programming is present. Table consistency is guarded at probe. Test signals include successful zone registration for all sensor IDs, valid hwmon entries, boundary ADC-code handling, runtime PM failure cleanup, and stable readings under the erratum workaround.
