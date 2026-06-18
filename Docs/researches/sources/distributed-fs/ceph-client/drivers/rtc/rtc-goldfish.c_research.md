# sources/distributed-fs/ceph-client/drivers/rtc/rtc-goldfish.c

Purpose: implements the Android Goldfish emulator RTC using memory-mapped goldfish timer registers for wall-clock time and alarm interrupts.

Important APIs/types/functions: `struct goldfish_rtc` stores MMIO base, IRQ, and RTC pointer. `goldfish_rtc_read_time()`/`goldfish_rtc_set_time()` convert between nanosecond hardware registers and seconds-based `rtc_time`. `goldfish_rtc_read_alarm()`, `goldfish_rtc_set_alarm()`, and `goldfish_rtc_alarm_irq_enable()` manage timer alarm registers. `goldfish_rtc_interrupt()` clears the interrupt and reports `RTC_AF`.

Control flow: probe allocates state, maps the MMIO resource, obtains IRQ, allocates RTC, sets `range_max = U64_MAX / NSEC_PER_SEC`, requests the IRQ, and registers the RTC. Alarm setting writes high then low nanosecond fields and enables IRQs; disabling clears an active alarm if the status register indicates one. Reads combine high/low registers and divide by nanoseconds per second.

State and persistence: state is emulator-provided timer/RTC register content. Runtime state is base pointer, IRQ, and RTC object.

Dependencies and integration: depends on platform/OF binding `google,goldfish-rtc`, goldfish MMIO accessors, RTC core, and timer register definitions.

Risks and test signals: high/low 64-bit register reads are not latched in the driver, so rollover between reads is a potential concern if hardware does not guarantee coherence. Test alarm enable/disable, interrupt clear, high/low rollover, no-IRQ probe failure, and large timestamp range handling.
