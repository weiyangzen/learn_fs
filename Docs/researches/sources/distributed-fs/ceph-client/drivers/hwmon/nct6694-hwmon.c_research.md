# sources/distributed-fs/ceph-client/drivers/hwmon/nct6694-hwmon.c

## Purpose

`nct6694-hwmon.c` is the hwmon child driver for the Nuvoton NCT6694 USB-attached multifunction controller. It exposes voltage, temperature, fan, and PWM channels through the modern `hwmon_ops` interface while delegating USB command transport to the parent NCT6694 MFD device via `nct6694_read_msg()` and `nct6694_write_msg()`.

## Important APIs, Types, and Functions

- `struct nct6694_hwmon_control` mirrors the HWMON control payload containing enable bitmaps and PWM frequency registers.
- `struct nct6694_hwmon_alarm` mirrors voltage, temperature, and fan limit/alarm configuration plus `smi_ctrl`.
- `struct nct6694_pwm_control` holds manual PWM enable/value fields for the PWM command module.
- `union nct6694_hwmon_rpt` represents single report-channel reads for voltage, temperature, fan, PWM, or status bytes.
- `struct nct6694_hwmon_data` stores the parent `struct nct6694`, mutex, cached enable/frequency control block, and reusable report/message buffers.
- `nct6694_in_read/write()`, `nct6694_temp_read/write()`, `nct6694_fan_read/write()`, and `nct6694_pwm_read/write()` implement type-specific hwmon attributes.
- `nct6694_read()`, `nct6694_write()`, and `nct6694_is_visible()` are the hwmon operation dispatchers.
- `nct6694_hwmon_init()` reads initial enable/frequency state, reads the alarm block, selects realtime interrupt/alarm mode, and writes it back.
- `nct6694_hwmon_probe()` allocates state and buffers, initializes the mutex, initializes hardware policy, and registers `nct6694_chip_info`.

## Control Flow

The platform probe obtains the parent MFD state from `pdev->dev.parent`, allocates one shared report buffer and one shared command payload union, stores the parent pointer, and initializes `data->lock`. `nct6694_hwmon_init()` reads the hardware monitor control block, then reads the alarm block, changes `smi_ctrl` to realtime mode, and writes the updated alarm block.

After registration, hwmon core calls `nct6694_is_visible()` to expose fixed permissions for every declared channel. Enable attributes are read from the cached `hwmon_en` bitmaps. Input/alarm reads build `struct nct6694_cmd_header` values for either the report module (`NCT6694_RPT_MOD`) or the HWMON/PWM command modules and serialize the transaction under `data->lock`. Writes either edit `hwmon_en` and write the full control block, or read-modify-write the full alarm/PWM-control structure before returning.

## State and Persistence Behavior

The enable state and PWM frequency bytes are cached in `data->hwmon_en` after probe and updated in memory before each successful control write. Limit and manual PWM structures are not long-term cached; they are read into `data->msg` for each read-modify-write path. Report data in `data->rpt` is a temporary shared buffer. The mutex serializes these buffers and parent command traffic for this child driver. Persistent effects live in the NCT6694 device firmware/configuration; the driver itself has no disk persistence and no PM callbacks.

## Dependencies and Integration Points

The file integrates with the NCT6694 MFD interface from `<linux/mfd/nct6694.h>`, platform driver binding via `MODULE_ALIAS("platform:nct6694-hwmon")`, Linux hwmon channel-info registration, bitfield helpers, endian helpers for fan limit/report values, and devm allocation. It assumes the parent MFD owns USB transport and command framing beyond the child driver-provided command headers.

## Risks and Edge Cases

- `nct6694_temp_write()` for `hwmon_temp_max_hyst` calls `nct6694_read_msg()` but does not check `ret` before using and writing `data->msg->hwmon_alarm`, so a failed read can propagate stale buffer contents.
- Enable writes update the cached `hwmon_en` before the device write result is known; if `nct6694_write_msg()` fails, memory and hardware state can diverge.
- Every limit update writes a full alarm block, so stale or concurrent state outside this driver could be overwritten if the parent has other clients changing the same block.
- `nct6694_is_visible()` exposes all declared channels regardless of enable bits; disabled channels appear with `*_enable=0` rather than being hidden.
- Temperature input conversion sign-extends an 11-bit value built from `msb` and three high bits of `lsb`; any firmware format change would silently corrupt readings.
- PWM frequency is clamped to 100-25000 Hz and quantized through an 8-bit register, so round-trip reads may not equal the requested value.

## Test Signals

Tests should cover init command ordering, realtime alarm mode write, visibility modes for each attribute, voltage scaling/clamping, signed temperature conversion and hysteresis encoding, fan big-endian values, PWM duty/frequency conversions, enable-bit updates for channels above and below bit 8, failed parent read/write paths including cache divergence, and concurrent sysfs reads/writes proving `data->lock` protects the shared buffers.
