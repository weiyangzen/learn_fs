# sources/distributed-fs/ceph-client/drivers/rtc/rtc-spear.c

Purpose: ST SPEAr platform RTC driver with BCD date/time registers, full alarm date/time registers, interrupt control, clock management, and suspend wake support.

Important APIs/types/functions: `struct spear_rtc_config` holds RTC device, clock, spinlock, MMIO, and IRQ wake state. Helpers clear/enable/disable alarm interrupt, poll busy bits, and check lost write status. `spear_rtc_read_time()` waits not busy, reads time/date and converts BCD. `spear_rtc_set_time()` writes packed BCD time/date and checks write completion. Alarm ops mirror this for alarm registers. `spear_rtc_irq()` clears status and reports `RTC_AF`.

Control flow/state/persistence: probe requests the alarm IRQ, maps MMIO, enables the clock, initializes lock and RTC range 0..9999, registers, and enables wake capability. Suspend either enables IRQ wake or disables interrupt/clock; resume reverses that. Shutdown disables interrupt and clock.

Dependencies/integration: platform driver `rtc-spear`, compatible `st,spear600-rtc`, clock framework, MMIO, RTC core, IRQ wake.

Risks/test signals: `spear_rtc_read_time()` loops while the first time read equals a second time read, which is unusual and can be sensitive to hardware behavior. `tm2bcd()` mutates the caller-provided `rtc_time`, so callers must not reuse fields after set ops. Test busy/lost-write handling, BCD packing for years, alarm enable/disable, suspend non-wakeup clock restore, and interrupt status clearing.
