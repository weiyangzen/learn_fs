<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx6110.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx6110.c

Purpose: implements the Epson RX-6110 SA RTC over either SPI or I2C using a shared regmap-backed core, exposing time read/write and basic initialization/status handling.

Important APIs/types/functions: `struct rx6110_data` stores the RTC and regmap. `rx6110_rtc_tm_to_data()` and `rx6110_data_to_rtc_tm()` convert between `rtc_time` and native BCD/one-hot weekday format. `rx6110_set_time()`, `rx6110_get_time()`, and `rx6110_init()` implement RTC operations and startup configuration. Separate SPI/I2C probe functions allocate regmaps and call common `rx6110_probe()`.

Control flow: module init registers SPI first and I2C second, unwinding SPI if I2C registration fails. Probe allocates bus-specific state, initializes regmap, registers the RTC, and applies defaults: disables timer enable, writes reserved/IRQ/alarm default registers, warns on VLF/AF/TF/UF, and clears non-VLF flags. Reads reject VLF, bulk-read seven time registers, decode BCD, and enforce year 2000-2099. Writes set STOP, bulk-write time, clear VLF, and clear STOP.

State and persistence: hardware stores time, alarm/timer registers, extension/control/flag bits, user bytes, and IRQ register. The driver persists no local state beyond the regmap and RTC pointer and does not expose alarm/timer/user RAM functions.

Dependencies and integration points: depends on regmap over SPI or I2C, RTC core, ACPI I2C ID `SECC6110`, OF SPI compatible `epson,rx6110`, I2C/SPI IDs, and board-provided SPI mode constraints.

Risks and test signals: `rx6110_data_to_rtc_tm()` sets `tm_wday = ffs(mask)` without subtracting one, unlike most RTC drivers. SPI mode mismatches only warn and continue. I2C regmap also sets `read_flag_mask = 0x80`, which should be validated against bus protocol. Test both buses, VLF rejection/clear, STOP bit failure recovery, weekday encoding, reserved register patching, alarm flag warning/clear, and init rollback between SPI/I2C registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx6110.c -->
