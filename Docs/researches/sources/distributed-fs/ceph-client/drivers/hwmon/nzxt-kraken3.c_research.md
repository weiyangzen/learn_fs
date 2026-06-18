# sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken3.c

Purpose: HID hwmon driver for NZXT Kraken X53/X63/X73, Z53/Z63/Z73, and 2023/Elite coolers. It reports coolant temperature, pump/fan speeds, PWM duty, manual and curve controls, firmware debugfs data, and reset-resume reinitialization.

Important APIs/types/functions: `struct kraken3_data` owns HID state, hwmon/debugfs devices, command buffer, completions, locks, per-channel control info, sensor values, device kind, firmware version, and fault state. Important functions include `kraken3_write_expanded()`, `kraken3_read_x53()`, `kraken3_read_z53()`, `kraken3_read()`, `kraken3_write_curve()`, `kraken3_write_fixed_duty()`, `kraken3_write()`, curve sysfs store helpers, `kraken3_raw_event()`, init/firmware helpers, debugfs setup, probe, remove, and reset-resume.

Control flow: probe opens HID, classifies product kind, allocates a 64-byte output buffer, initializes locks/completions, sends interval and init commands, requests firmware version, registers hwmon with extra curve attributes, and creates debugfs if firmware is known. X-series receives periodic status asynchronously; Z-series/2023 reads explicitly send a status request and wait for the raw-event completion. PWM writes program a 40-point curve; manual duty is represented by a flat curve with 100 percent at the critical point.

State and persistence: in-memory state tracks last reported duty, fixed duty, curve points, mode, firmware, fault flag, and freshness. Hardware state persists in the cooler after output reports. Resume replays initialization but does not reconstruct all user curves.

Dependencies and integration: depends on HID, hwmon, extra hwmon-sysfs attributes, completions, mutexes, spinlocks, debugfs, and product-specific report layouts.

Risks: report layouts are reverse engineered and product-dependent. Fault reports with `0xff` temperature bytes suppress readings. X-series cannot request fresh status, so stale data blocks reads. Concurrency between hidraw/user sysfs/report completions is delicate. Pump duty is clamped to 20 percent minimum except forced 100 percent for off mode.

Test signals: product-ID kind mapping, init and firmware command success, X-series first-report wait, Z-series request/response path, stale timeout handling, fault report handling, PWM enable transitions 0/1/2, curve attribute visibility, debugfs firmware output, and reset-resume.
