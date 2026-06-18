# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max77686.c

Purpose: supports RTC blocks in Maxim/Samsung PMICs MAX77686, MAX77802, MAX77620, and MAX77714, handling model-specific register maps, ancillary I2C or shared regmap access, regmap IRQ chips, alarms, update handshakes, and suspend wake routing.

Important APIs and types: `struct max77686_rtc_driver_data` describes per-model delay, masks, register map, alarm-enable style, I2C address, IRQ origin, pending status register, IRQ chip, and regmap config. `struct max77686_rtc_info` holds parent and RTC regmaps, IRQ chip data, virtual alarm IRQ, mutex, and RTC device. Core helpers are `max77686_rtc_data_to_tm()`, `max77686_rtc_tm_to_data()`, `max77686_rtc_update()`, `max77686_rtc_stop_alarm()`, `max77686_rtc_start_alarm()`, and `max77686_init_rtc_regmap()`.

Control flow: probe selects platform-device driver data, initializes the RTC regmap either through an ancillary I2C client or the parent regmap, registers a regmap IRQ chip, initializes binary/24-hour mode, enables wakeup, registers the RTC, maps RTCA1 virtual IRQ, and requests the threaded alarm IRQ. Reads trigger read-update, bulk-read fields, then decode. Writes bulk-write and trigger write-update. Alarm handling differs between MAX77802's dedicated enable register and other chips' per-field enable bits.

State and persistence: time, alarm, enable bits, update bits, and interrupt status are PMIC RTC registers. Software state tracks the regmap IRQ chip and mutex-protected operations. Wake state is managed through device wakeup and PM callbacks.

Dependencies and integration: MFD parent regmaps, I2C ancillary devices, regmap IRQ framework, platform IDs, RTC class, PM sleep hooks, and PMIC-private register definitions.

Risks: model data must exactly match hardware; incorrect map or mask corrupts time/alarm fields. The driver initializes control registers at probe, which can alter mode. MAX77714 has unsupported alarm pending status. Suspend disables the parent IRQ for shared-IRQ models to avoid I2C access while suspended, which must coordinate with other MFD users.

Test signals: each platform ID, ancillary versus parent-regmap path, regmap IRQ add/delete cleanup, binary/24-hour initialization, read/write update delay timing, MAX77802 dedicated alarm enable, no-pending-status model, suspend/resume wake behavior, and failed virtual IRQ mapping.
