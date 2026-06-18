<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.c

Purpose: implements the Dialog/Renesas SLG51000 I2C high-PSRR multi-output regulator driver, registering seven LDO outputs, deriving their voltage limits from chip MIN/MAX registers, supporting optional GPIO enables, and reporting over-current/over-temperature events.

Important APIs/types/functions: `struct slg51000` owns device, regmap, regulator descriptors/devices, optional chip-select GPIO, and IRQ. `slg51000_regmap_config` constrains 16-bit register access using writable/readable/volatile tables from `slg51000-regulator.h`. `slg51000_of_parse_cb()` captures optional `enable` GPIOs. `slg51000_regulator_init()` reads per-LDO MIN/MAX ranges and mode bits, adjusts `regulator_desc` fields, switches LDO5/6 to switch ops when bypass mode is selected, and registers all LDOs. `slg51000_irq_handler()` reads event/status/mask registers and sends regulator notifier events.

Control flow: I2C probe allocates state, asserts optional `dlg,cs` GPIO, waits 10 ms, initializes regmap, registers regulators, logs fault state, and optionally requests a threaded IRQ. During regulator initialization, LDO1/2 use their voltage-range bit to choose low or high base voltage; LDO5/6 may become non-voltage switches; all others use OTP-programmed min/max selector windows. IRQ handling bulk-reads event/status/mask triplets for every LDO plus system control, reports unmasked over-current for specific rails, reports high-temperature warning to rails whose status looks otherwise valid, and handles OTP CRC events.

State and persistence: descriptor fields are mutated at probe according to OTP/config registers. Runtime state holds regulator device pointers for notifier delivery and optional GPIO/IRQ handles. Actual voltage windows, bypass mode, events, masks, and enable matrix bits are stored in SLG51000 registers/OTP.

Dependencies and integration: depends on I2C, regmap access tables, GPIO descriptors, regulator OF child nodes under `regulators`, threaded IRQs, and notifier integration. The header provides all register and bitfield constants used by access control, voltage setup, fault logging, and IRQ decoding.

Risks and test signals: `regls_desc` is static and mutated at probe, so multiple devices could share adjusted descriptor state. `slg51000_of_parse_cb()` ignores GPIO errors, including defer, which can mask incomplete GPIO providers. IRQ event interpretation depends on three adjacent event/status/mask registers per rail. Test OTP/min/max-derived voltage windows, LDO1/2 high/low range, LDO5/6 bypass-as-switch, optional chip-select timing, optional enable GPIOs, regmap access denials, no-IRQ probe, over-current notifier delivery, high-temperature notifier delivery, and fault-log reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/slg51000-regulator.c -->
