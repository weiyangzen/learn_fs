# sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken2.c

Purpose: HID hwmon driver for NZXT Kraken X42/X52/X62/X72 coolers. It exposes coolant temperature, fan speed, and pump speed from asynchronous USB HID status reports.

Important APIs/types/functions: `struct kraken2_priv_data` stores HID/hwmon devices, last parsed temperature/RPM values, and update jiffies. Main entry points are `kraken2_raw_event()`, `kraken2_read()`, `kraken2_read_string()`, `kraken2_probe()`, and `kraken2_remove()`.

Control flow: probe parses HID descriptors, starts HID hardware with hidraw enabled, opens the device so input reports flow, and registers hwmon. The raw-event hook accepts report id `0x04` with at least seven bytes, converts coolant temperature as integer plus tenths, parses big-endian fan and pump RPM fields, and refreshes `updated`. Hwmon reads return cached values only if a recent report arrived within the two-second validity window.

State and persistence: no hardware configuration is changed. Cached sensor data persists in memory until stale; `updated` is initialized in the past so initial reads return `-ENODATA` until a real report arrives.

Dependencies and integration: depends on HID, hidraw coexistence, hwmon chip info, jiffies, and unaligned big-endian helpers. The HID id table matches NZXT vendor 0x1e71 product 0x170e.

Risks: there is no locking around raw-event writes and sysfs reads, relying on naturally aligned scalar updates. The device cannot answer status Get_Report requests, so missing asynchronous reports make readings unavailable. Temperature fractional interpretation is inferred from observed firmware behavior.

Test signals: HID probe/open/remove, report parsing with correct ID and size, stale-data `-ENODATA`, hidraw coexistence with userspace tools, label strings, and endian-correct RPM values.
