## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-rtc.c

### Purpose
`opal-rtc.c` provides boot-time RTC reading and platform-device creation for OPAL RTC/TPO services.

### Important APIs, Types, And Functions
Key functions are `opal_to_tm()`, exported-by-declaration `opal_get_boot_time()`, and initcall `opal_time_init()`.

### Control Flow
`opal_get_boot_time()` checks for the `OPAL_RTC_READ` token, loops through `OPAL_BUSY` and `OPAL_BUSY_EVENT` with millisecond delays and event polling, decodes OPAL's BCD year/month/day and hour/minute/second fields, and converts the result to `time64_t`. `opal_time_init()` creates an OF-backed `opal-rtc` platform device if `/ibm,opal/rtc` exists; otherwise it registers a simple device if RTC read or TPO read tokens are present.

### State, Persistence, And Dependencies
The file keeps no persistent state. Time is firmware-backed. Dependencies include OPAL RTC/TPO tokens, BCD conversion, RTC time helpers, OF platform-device creation, and busy-event polling.

### Integration Points
The platform RTC driver binds to `opal-rtc`. Early boot time code can call `opal_get_boot_time()` to seed system time.

### Risks
Invalid BCD values are not separately validated before conversion. Busy loops use `mdelay()` because this is init/early behavior. If token checks fail, boot time silently returns zero.

### Test Signals
Test valid BCD decoding across century/month boundaries, absent tokens, OPAL busy and busy-event loops, failure returns, DT-backed versus simple platform device registration, and TPO-only fallback.
