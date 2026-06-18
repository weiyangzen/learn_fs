<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/rtc.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/rtc.c

Purpose: This file registers the Dreamcast AICA RTC through the generic RTC platform driver, translating between the AICA 1950 epoch and Unix time.

Important APIs/types/functions: It defines `TWENTY_YEARS`, AICA high/low seconds register addresses, `aica_rtc_gettimeofday`, `aica_rtc_settimeofday`, `rtc_generic_ops`, and initcall `aica_time_init`.

Control flow: Read loops until two consecutive 32-bit seconds reads from high/low 16-bit registers match, subtracts the 20-year epoch offset, casts into the 1970-2106 range, and converts to `rtc_time`. Set adds the offset, writes high and low halves, and repeats until readback is stable. Init registers a `rtc-generic` platform device with these ops.

State and persistence: Persistent state is the hardware RTC seconds counter. Kernel platform-device registration persists for RTC driver binding.

Dependencies and integration points: It depends on raw I/O accessors, generic RTC class ops, and Dreamcast hardware addresses.

Risks and test signals: The 32-bit counter and epoch conversion limit valid time range. Split-register reads/writes require stable double-read loops. Tests include RTC read/set, rollover around low-half changes, dates near 1970 and 2106, and driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/rtc.c -->
