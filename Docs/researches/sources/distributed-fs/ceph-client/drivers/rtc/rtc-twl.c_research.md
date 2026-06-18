## sources/distributed-fs/ceph-client/drivers/rtc/rtc-twl.c

Purpose: Provides RTC support for TI TWL4030/TWL5030/TWL6030/TPS659x0 PMIC families. It handles time/alarm BCD registers, PM wake behavior, interrupt routing, and small battery-backed NVMEM areas.

Important APIs/types/functions: `struct twl_rtc` stores the RTC device, register map, cached interrupt-enable bits, wake flag, PM suspend IRQ state, and TWL class. Register access goes through `twl_rtc_read_u8`, `twl_rtc_write_u8`, `twl_i2c_read`, and `twl_i2c_write`. RTC callbacks are `twl_rtc_read_time`, `twl_rtc_set_time`, `twl_rtc_read_alarm`, `twl_rtc_set_alarm`, and `twl_rtc_alarm_irq_enable`. NVMEM is implemented by `twl_nvram_read`/`twl_nvram_write`.

Control flow: Probe requires DT, an IRQ, and a supported TWL class. It selects the 4030 or 6030 register map, reads and clears power-up/alarm status, unmasks TWL6030 RTC interrupt lines, starts the RTC, disables inherited bootloader interrupts, caches interrupt state, registers an RTC device, requests the threaded IRQ, and registers secured/backup NVMEM windows. Time reads latch a coherent snapshot with `GET_TIME`; TWL6030 needs an extra clear/restore and `RTC_V_OPT` handling. Time writes clear STOP, bulk-write six BCD fields, then set STOP to run. Alarm writes disable alarm IRQ, write six fields, then optionally re-enable. IRQ handling reads status, reports alarm or periodic events, clears alarm status, and performs an extra TWL4030 power ISR read to clear legacy interrupt state.

State and persistence: The PMIC maintains BCD time/alarm registers, status, interrupt-enable bits, and battery-backed NVMEM. The driver caches `rtc_irq_bits` because enable state is modified under RTC ops locking and needs to survive PM suspend/resume. `wake_enabled` tracks whether IRQ wake was enabled by alarm operations.

Dependencies/integration: Integrates with TWL MFD helpers, RTC core, NVMEM via `devm_rtc_nvmem_register`, OF match `"ti,twl4030-rtc"`, platform IRQs, and PM sleep callbacks.

Risks: Cached interrupt bits can diverge if external code writes registers. TWL6030 shadow-register sequencing is easy to regress. The TWL4030 extra-clear workaround can theoretically clear unrelated power interrupt status. Alarm fields can be wildcard-like in hardware, but the driver reports normal decoded values.

Test signals: Boot on 4030 and 6030 variants, validate time set/read coherency across seconds rollover, alarm IRQ and wake toggling, NVMEM read/write windows, PM suspend/resume restoration of timer/alarm bits, and probe recovery from pending power-up/alarm status.
