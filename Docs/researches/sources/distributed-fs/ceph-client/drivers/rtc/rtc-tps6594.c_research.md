## sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6594.c

Purpose: Implements the RTC class driver for TI TPS6594 PMIC MFD children. It exposes calendar time, one-shot alarm, alarm wake, and RTC offset calibration through `struct rtc_class_ops` using the parent PMIC `regmap`.

Important APIs/types/functions: `struct tps6594_rtc` stores the allocated `rtc_device` and alarm IRQ. Time and alarm paths are `tps6594_rtc_read_time`, `tps6594_rtc_set_time`, `tps6594_rtc_read_alarm`, `tps6594_rtc_set_alarm`, and `tps6594_rtc_alarm_irq_enable`. Calibration is split between raw compensation helpers `tps6594_rtc_{get,set}_calibration` and RTC-core ppb APIs `read_offset`/`set_offset`. Probe uses `devm_rtc_allocate_device`, `devm_request_threaded_irq`, `device_init_wakeup`, and `devm_rtc_register_device`.

Control flow: Probe enables the crystal, verifies or starts RTC run state, intentionally stops the RTC until first `set_time` if it was uninitialized, installs a threaded alarm IRQ, marks the device wake-capable, sets the 2000-2099 range, and registers. Reads first check `TPS6594_BIT_RUN`, pulse `GET_TIME` to latch coherent shadow registers, bulk-read BCD fields, and translate into `rtc_time`. Time writes stop the counter, bulk-write the seven time registers, and restart it. Alarm writes disable the interrupt, bulk-write six BCD alarm fields, then re-enable if requested. The IRQ handler reads status only as a sanity check and reports `RTC_IRQF | RTC_AF`; resume separately notices latched startup RTC interrupts and clears/replays them.

State and persistence: Hardware state is in PMIC RTC, alarm, interrupt, status, and compensation registers. Driver state is minimal and devm-owned. Calibration persists in compensation registers and is exposed as signed ppb with an inverted sign convention. Wake state is configured via IRQ wake around system suspend.

Dependencies/integration: Depends on Linux RTC core, `linux/mfd/tps6594.h`, regmap, platform device IDs, and PM sleep helpers. It integrates with `/sys/class/rtc`, `wakealarm`, and `offset` through RTC core callbacks.

Risks: Stop/start bit naming is counterintuitive, so polarity regressions would break set-time. Offset conversion relies on bounded math and sign inversion. Alarm IRQ handling assumes parent interrupt/status clearing semantics. The driver rejects reads when the run bit is clear, which surfaces uninitialized or oscillator-failed hardware as `-EINVAL`.

Test signals: Exercise `hwclock -r/-w`, alarm wake from suspend, `/sys/class/rtc/rtcN/offset`, invalid oscillator/run-bit handling, and boundary years 2000/2099. Regmap fault injection should cover each bulk read/write and compensation path.
