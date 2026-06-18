## sources/distributed-fs/ceph-client/drivers/rtc/rtc-vt8500.c

Purpose: Implements the VIA/WonderMedia VT8500 SoC RTC driver. It exposes MMIO-backed time, date, alarm, and alarm IRQ control to the Linux RTC core.

Important APIs/types/functions: `struct vt8500_rtc` holds the mapped register base, alarm IRQ, RTC device, and a spinlock used around interrupt status clear. The RTC operations are `vt8500_rtc_read_time`, `vt8500_rtc_set_time`, `vt8500_rtc_read_alarm`, `vt8500_rtc_set_alarm`, and `vt8500_alarm_irq_enable`. `vt8500_rtc_irq` handles the alarm interrupt.

Control flow: Probe allocates driver state, initializes the spinlock, gets the platform IRQ, maps the register resource, enables the RTC in 24-hour mode by writing `VT8500_RTC_CR_ENABLE`, allocates/registers the RTC, and requests the alarm IRQ. Time reads fetch packed BCD date/time registers and decode seconds, minutes, hours, day, month, weekday, and a 2000/2100 century bit. Time writes encode date and time into the set registers. Alarm reads decode the alarm-set register and status register, reporting enabled if any compare-enable bit is set and pending from interrupt status. Alarm writes pack day/hour/min/sec plus compare-enable bits when requested. IRQ handling reads and writes back interrupt status to clear it, then reports `RTC_AF | RTC_IRQF` when the alarm bit was set.

State and persistence: Hardware stores packed BCD date/time and alarm values. Driver state is devm-managed except the register values. The code sets `range_min` to 2000 and `range_max` to 2199, matching the century bit logic.

Dependencies/integration: Uses platform resources, OF compatible `"via,vt8500-rtc"`, `devm_platform_ioremap_resource`, `devm_request_irq`, RTC class ops, MMIO `readl/writel`, and BCD helpers.

Risks: The write-status and invalid-time bits are defined but not used, so the driver does not wait for write completion or reject invalid hardware state. IRQ status clearing is protected, but ordinary alarm writes are not locked against concurrent IRQ. `remove` writes zero to the interrupt status register despite the comment saying disable alarm matching, so hardware semantics should be checked before changing it.

Test signals: Validate rollover-safe read/write, alarm enable/disable bitmask behavior, pending alarm reporting, IRQ clear-on-write behavior, and boundary years 2000 and 2199 under a DT platform instance.
