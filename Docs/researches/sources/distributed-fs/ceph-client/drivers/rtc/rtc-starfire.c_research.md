# sources/distributed-fs/ceph-client/drivers/rtc/rtc-starfire.c

Purpose: built-in Starfire platform RTC reader for SPARC systems using OpenBoot PROM calls. It exposes read-time only.

Important APIs/types/functions: `starfire_get_time()` builds an OBP Forth command string pointing at a static `unix_tod`, calls `prom_feval()`, and returns the resulting Unix seconds. `starfire_read_time()` converts seconds to `rtc_time`. `starfire_rtc_probe()` allocates/registers an RTC with `range_max = U32_MAX`.

Control flow/state/persistence: the driver is registered by `builtin_platform_driver_probe()`, so it probes once and cannot be unbound like a normal module. State is owned by firmware; the Linux driver has no set-time, alarm, or persistent software state.

Dependencies/integration: SPARC `asm/oplib.h`, platform device name `rtc-starfire`, RTC core. It is firmware-dependent and has no OF table in this file.

Risks/test signals: static command/time buffers are not synchronized, though normal RTC core access is serialized enough for typical use. Firmware failures are not reported; zero time would be returned. Test on Starfire firmware, confirm year-2038/2106 behavior from U32 range, and ensure absence of set/alarm features is accepted.
