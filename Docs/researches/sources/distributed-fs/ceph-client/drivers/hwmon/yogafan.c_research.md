# sources/distributed-fs/ceph-client/drivers/hwmon/yogafan.c

## Purpose
This platform hwmon driver exposes fan RPM readings for selected Lenovo Yoga, Legion, and IdeaPad laptops by evaluating ACPI EC methods matched through DMI. It applies a passive first-order lag and slew-rate limiter to smooth low-resolution EC tachometer samples.

## Important APIs, Types, And Functions
- `struct yogafan_config` describes a DMI-specific multiplier, expected fan count, and ACPI method paths.
- `struct yoga_fan_data` stores resolved ACPI handles, per-fan filtered values, per-fan last sample time, multiplier, and active fan count.
- `apply_rllag_filter()` implements raw-RPM sanitation, sampling interval gating, autoreset after long gaps, first-order lag, and slew limiting.
- `yoga_fan_read()` evaluates the ACPI method for a channel, applies scaling/filtering, and returns `hwmon_fan_input`.
- `yoga_fan_is_visible()` exposes only active fan channels.
- `yoga_fan_init()` registers the platform driver and a simple platform device only on matching DMI systems.

## Control Flow
Module init checks DMI first, registers the platform driver, and creates a platform device named `yogafan`. Probe finds the first matching DMI configuration, allocates state, resolves each configured ACPI EC path, counts only successfully resolved handles, and registers a hwmon device with `hwmon_chip_info`. Runtime fan reads evaluate the channel's ACPI object and pass the scaled raw RPM through the filter before returning it.

## State And Persistence
The only mutable state is per-fan filter state: `filtered_val[]` and `last_sample[]`. It is updated lazily on userspace reads, so there is no background polling and no persistence across unload. If raw RPM is below `RPM_FLOOR_LIMIT`, the output snaps to zero. If sampling gaps exceed `MAX_SAMPLING`, the filter resets to raw RPM.

## Dependencies And Integration Points
The driver integrates with DMI matching, ACPI handle lookup and integer evaluation, the modern hwmon `read`/`is_visible` API, platform driver/device registration, `ktime_get_boottime()`, and 64-bit division helpers. It supports up to eight fan channels in the static hwmon channel descriptor.

## Risks
- ACPI method paths are hard-coded per broad DMI product family, so firmware naming variations can leave supported systems without fans or expose only a subset.
- The filter is read-driven; sparse or very frequent polling changes smoothing behavior by design.
- No explicit locking protects filter state. Concurrent sysfs reads of the same fan can race updates.
- `fan_count` can be less than the configured count if handles fail; visibility handles this, but unexpected DMI matches may hide hardware.

## Test Signals
Validate DMI matching for Yoga/Legion/IdeaPad, ACPI handle discovery for each configured path, behavior when no handles resolve, raw 8-bit multiplier versus 16-bit dual-fan configs, filter reset on first/late sample, minimum sampling suppression, slew-rate limiting, zero snap behavior, and concurrent read race detection with lockdep/KCSAN if available.
