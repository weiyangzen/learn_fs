# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1553.c

Purpose: supports the Dallas DS1553 memory-mapped RTC/NVRAM device. The final register window holds clock, alarm, control, watchdog, and status registers; the preceding address space is exported as battery-backed nvmem.

Important APIs/types/functions: `struct rtc_plat_data` tracks the RTC device, mapped I/O, IRQ, cached alarm fields, interrupt enable flags, `last_jiffies`, and a spinlock. `ds1553_rtc_read_time()` and `ds1553_rtc_set_time()` handle BCD calendar conversion with century support. `ds1553_rtc_update_alarm()` writes alarm registers and interrupt enable state. `ds1553_nvram_read()` and `ds1553_nvram_write()` provide byte nvmem access up to `RTC_OFFSET`.

Control flow: probe maps the resource, detects/stops the RTC stop bit, warns on battery-low, initializes cached state, registers the RTC, then optionally requests the IRQ and registers nvmem. Reads assert `RTC_READ`, sample the calendar, then deassert control. Writes assert `RTC_WRITE`, program fields, write the shared century/control register carefully, and exit write mode. Alarm setup stores requested fields in software, writes them to hardware, and enables the alarm interrupt when requested. The IRQ handler distinguishes alarm versus update-style wildcard events and calls `rtc_update_irq()`.

State and persistence: time, alarm registers, control bits, and NVRAM persist in the chip. Cached alarm fields and `irqen` are runtime mirrors used because the alarm read path reports driver state rather than re-reading all hardware semantics.

Dependencies and integration: integrates with platform MMIO resources, RTC core, nvmem, jiffies delay logic, and optional IRQs. Module alias is `platform:rtc-ds1553`.

Risks and test signals: the one-jiffy read delay avoids continuous read hazards but may be timing-sensitive. Alarm support depends on IRQ presence but the feature bit is not explicitly cleared after failed IRQ setup. Test stop-bit recovery, century register preservation, battery-low warning, wildcard/update alarm behavior, IRQ unavailable paths, and NVRAM offset coverage.
