
# sources/distributed-fs/ceph-client/drivers/hwmon/shtc1.c

Purpose: I2C hwmon driver for Sensirion SHTC1, SHTW1, and SHTC3 humidity and temperature sensors. It exposes read-only temperature and relative humidity attributes using the older hwmon groups API.

Important APIs, types, and functions: `struct shtc1_data` contains the client, `update_lock`, cache validity, selected command, nonblocking wait time, platform or device-tree setup, chip type, and cached readings. `shtc1_update_values()` sends the selected two-byte measurement command and reads six response bytes. `shtc1_update_client()` serializes updates, caches for `HZ / 10`, and converts raw big-endian words. `shtc1_select_command()` chooses blocking/nonblocking and high/low precision command variants.

Control flow, state, and persistence: probe requires plain I2C, reads and validates the chip ID with chip-specific masks, allocates data, defaults to nonblocking high precision, then overrides options from `sensirion,blocking-io`, `sensirion,low-precision`, or platform data. Runtime state is volatile cache only; no configuration is restored on remove.

Dependencies and integration points: uses I2C transfers rather than SMBus, hwmon groups, OF matching, and optional `linux/platform_data/shtc1.h`. I2C ids cover `shtc1`, `shtw1`, and `shtc3`; OF compatibles mirror those names.

Risks and test signals: the driver does not validate the two CRC bytes in measurement responses, so corrupted readings can pass through. Blocking I/O can hold the bus while the device stretches clock. Test detection for all IDs, DT/platform option selection, nonblocking delays, failed send/receive paths, cache reuse within 100 ms, and conversion formulas for temperature and humidity.
