# sources/distributed-fs/ceph-client/drivers/rtc/rtc-loongson.c

Purpose: provides RTC support for Loongson SoCs and bridges, covering TOY counter timekeeping, alarm handling, PM-domain wakeup control, ACPI fixed RTC events, and chip-specific workarounds for broken control or alarm registers.

Important APIs and types: `struct loongson_rtc_config` carries PM offset and workaround flags; `struct loongson_rtc_priv` stores regmap, PM base, RTC device, spinlock, and the 64-year alarm compensation. RTC callbacks are `loongson_rtc_read_time()`, `loongson_rtc_set_time()`, `loongson_rtc_read_alarm()`, `loongson_rtc_set_alarm()`, and `loongson_rtc_alarm_irq_enable()`. Interrupt paths are `loongson_rtc_isr()` and ACPI `loongson_rtc_handler()`.

Control flow: probe maps MMIO into a regmap, selects OF/ACPI match data, allocates the RTC, configures alarms unless the chip flags disable them, clears UIE support, and registers a 2000-2099 RTC. Time reads check whether TOY counters and oscillator are enabled unless the LS1C workaround applies, then decode packed `TOY_READ0/1`. Setting time writes `TOY_WRITE0/1` and enables TOY/oscillator. Alarms write `TOY_MATCH0`, while PM enable bits drive wake and interrupt routing.

State and persistence: hardware TOY registers persist in the RTC domain. `fix_year` is derived from current time and compensates the 6-bit alarm year field; stale `fix_year` after a time jump can affect alarm reconstruction. PM status/enable registers are protected by `priv->lock`.

Dependencies and integration: uses MMIO regmap, ACPI fixed event handler registration, OF and ACPI match tables, platform IRQs, and Loongson PM1 status/enable registers. Some variants disable alarm feature bits at runtime.

Risks: LS1C control-register accesses can hang, so workaround flags must match hardware. Alarm year encoding is only six bits and relies on a previous time read to set `fix_year`. ACPI handler removes PM wake enable and clears status; mismatch between ACPI and non-ACPI paths can leave alarms armed. `pm_base` is derived by subtracting a per-chip offset from the RTC register base.

Test signals: verify LS1B/LS1C/LS2K/LS7A/ACPI variants, alarm feature clearing for workaround chips, 64-year alarm compensation around boundaries, ACPI fixed event install/remove, PM1 enable/status updates, and TOY disabled reads returning `-EINVAL`.
