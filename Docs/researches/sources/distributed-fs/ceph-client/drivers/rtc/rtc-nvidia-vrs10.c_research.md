# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nvidia-vrs10.c

Purpose: implements RTC support for NVIDIA VRS10 power sequencer devices over I2C with PEC enabled, including 32-bit seconds time, alarm wake bits, interrupt clearing, and suspend wake integration.

Important APIs/types/functions: `struct nvvrs_rtc_info` stores device, I2C client, RTC, and IRQ. `nvvrs_update_bits()` provides read-modify-write for control registers. `nvvrs_rtc_write_alarm()`, `nvvrs_rtc_enable_alarm()`, and `nvvrs_rtc_disable_alarm()` manage alarm registers and RTC_WAKE/RTC_PU bits. Time and alarm callbacks read/write four one-byte registers MSB-first or MSB-to-LSB. `nvvrs_pseq_irq_clear()` clears all interrupt source registers by read/writeback. `nvvrs_pseq_vendor_info()` validates model revision.

Control flow: probe requires a client IRQ, enables I2C PEC, validates vendor/model revision, clears pending interrupts, allocates the RTC, requests a threaded IRQ, initializes wakeup, sets 2000-2099 range, and registers. Reads assemble 32-bit seconds from T3..T0; writes split seconds into T3..T0. Set-alarm disables if requested disabled, but then always enables wake bits and writes the alarm time. IRQ handler checks `INT_SRC1_RTC`, reports `RTC_AF` under `rtc_lock()`, then clears all interrupt sources.

State and persistence: hardware persists seconds counter, alarm seconds, RTC_WAKE/RTC_PU control bits, interrupt source flags, model revision, and PEC behavior. Driver state has no cache. Disabled alarm is represented by writing `0xffffffff`.

Dependencies and integration: depends on I2C/SMBus byte operations with PEC, OF compatible `nvidia,vrs-10`, a valid IRQ, PM sleep wake callbacks, and RTC class.

Risks and test signals: `nvvrs_rtc_set_alarm()` disables when `enabled == false` but then immediately enables alarm wake bits and writes the requested alarm time, so disabled alarms may be re-enabled. `alarm_irq_enable()` is a no-op because hardware cannot separate IRQ enable from alarm programming. Multi-byte register coherency relies on MSB-first reads with no retry. Test model revision rejection, PEC transactions, disabled-alarm semantics, reset-value read alarm, interrupt-source clear failures, suspend/resume wake bit writes, 2038+ values within 2000-2099 range, and missing IRQ probe failure.
