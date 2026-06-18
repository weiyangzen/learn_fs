<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8581.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8581.c

Purpose: implements Epson RX8571/RX8581 I2C RTC support with time read/write and battery-backed nvmem exposure.

Important APIs/types/functions: `struct rx85x1_config` selects regmap range and number of nvmem regions for RX8581 or RX8571. `rx8581_rtc_read_time()` and `rx8581_rtc_set_time()` implement RTC ops. Nvmem callbacks expose one RAM byte for RX8581-like chips and an additional 16-byte user RAM region for RX8571.

Control flow: probe selects OF match data when present, initializes I2C regmap, stores it as client data, allocates an RTC, sets ops/range/start-time behavior, registers the RTC, and registers configured nvmem regions. Read-time checks VLF, clears and waits out UF by repeating time reads until the update flag stays clear, then decodes BCD fields. Set-time builds BCD time data, sets STOP, writes time registers, clears VLF, and clears STOP.

State and persistence: hardware stores BCD time, flag/control bits, one RAM byte, and for RX8571 a larger user RAM window. Driver state is the selected immutable config and regmap.

Dependencies and integration points: depends on I2C regmap, RTC core, OF compatibles `epson,rx8571` and `epson,rx8581`, I2C ID `rx8581`, nvmem registration, and BCD/ilog2 helpers.

Risks and test signals: `devm_rtc_nvmem_register()` results are ignored. If set-time fails after STOP, the clock can remain stopped. `ilog2()` assumes a valid nonzero one-hot weekday. The loop clearing UF can spin if hardware keeps setting UF. Test RX8571 versus RX8581 nvmem sizes, VLF rejection and clear, UF retry behavior, STOP failure recovery, RTC start-time initialization, invalid weekday encodings, and OF match data fallback to RX8581 config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8581.c -->
