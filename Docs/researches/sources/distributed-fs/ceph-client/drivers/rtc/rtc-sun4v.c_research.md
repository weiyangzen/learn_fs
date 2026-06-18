# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sun4v.c

Purpose: SUN4V hypervisor-backed RTC driver for SPARC logical domains. It implements read and set time through hypervisor TOD calls.

Important APIs/types/functions: `hypervisor_get_time()` calls `sun4v_tod_get()` with retry handling for `HV_EWOULDBLOCK`. `hypervisor_set_time()` calls `sun4v_tod_set()` with the same retry policy and returns Linux errors for timeout or unsupported calls. RTC ops convert between `rtc_time` and seconds. Probe allocates/registers an RTC with `range_max = U64_MAX`.

Control flow/state/persistence: the driver is built in with `builtin_platform_driver_probe()`. No MMIO or software persistent state is maintained; the hypervisor owns the time source.

Dependencies/integration: SPARC `asm/hypervisor.h`, platform name `rtc-sun4v`, RTC core, microsecond delays for hypervisor busy retry.

Risks/test signals: read failures return zero time after warning rather than an error. Set can return `-EAGAIN` or `-EOPNOTSUPP`. Test hypervisor busy retry paths, unsupported TOD services, permission behavior for setting time, and U64 range handling.
