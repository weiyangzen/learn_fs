# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcap.c

Purpose: implements the Motorola EZX PCAP RTC subdevice, exposing day and time-of-day counters plus day/time alarm registers from the PCAP MFD.

Important APIs/types/functions: `struct pcap_rtc` stores parent PCAP chip and RTC device. `pcap_rtc_read_time()`/`set_time()` convert between seconds since epoch and PCAP day plus time-of-day registers. Alarm callbacks use the corresponding `DAYA` and `TODA` registers. `pcap_rtc_irq()` maps PCAP 1 Hz and alarm IRQs to RTC update and alarm events. `pcap_rtc_irq_enable()` enables/disables parent IRQ lines.

Control flow: probe gets the parent PCAP pointer, allocates and configures an RTC with a 14-bit day range, maps PCAP 1 Hz and alarm IRQs, requests both IRQs, and registers the RTC. Runtime time/alarm operations read or write the day and seconds-within-day registers. `alarm_irq_enable()` only enables/disables the PCAP alarm IRQ; set-alarm does not use the `enabled` field directly.

State and persistence: PCAP hardware persists day, time-of-day, alarm day, and alarm time-of-day counters. Driver state holds no cache. IRQ enable state is managed by Linux IRQ masking rather than a device register in this driver.

Dependencies and integration: depends on the EZX PCAP MFD, `pcap_to_irq()`, PCAP register access helpers, platform subdevice `pcap-rtc`, and RTC class.

Risks and test signals: `ezx_pcap_read()` and write return values are ignored, so bus failures are invisible to RTC callers. Alarm enabled state is not returned in `read_alarm()` and not programmed in `set_alarm()`. Disabling IRQs directly can interact poorly with shared users if parent IRQ mapping changes. Test PCAP read/write failures, 14-bit day range limit, 1 Hz update IRQ, alarm IRQ enable/disable, alarm set with disabled flag, and parent IRQ mapping correctness.
