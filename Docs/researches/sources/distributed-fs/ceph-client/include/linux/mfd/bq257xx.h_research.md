## sources/distributed-fs/ceph-client/include/linux/mfd/bq257xx.h

Purpose: This header defines TI BQ257xx/BQ25703 charger register constants, field masks, unit conversions, ADC controls, and the shared charger device object.

Important APIs, types, and constants: Register addresses are 16-bit-spaced charger configuration/status locations: charge options, charge current, maximum charge voltage, OTG voltage/current, input voltage/current, minimum system voltage, charger/prochot status, DPM current, ADC readings, manufacturer/device ID, and ADC options. Field definitions include watchdog timing, charge-current mask and microamp limits, charge-voltage mask and microvolt limits, OTG voltage/current ranges, minimum VSYS range, charger fault/status bits, input current DPM conversion, battery/input/system ADC masks and units, ADC channel enables, ADC conversion start/full-scale bits, and OTG enable. `struct bq257xx_device` stores the I2C client and regmap.

Control flow: No functions are declared. The charger driver uses the constants to translate power-supply/regulator requests into register values through regmap, and uses ADC/status fields for charger state reporting.

State and persistence: Charger configuration and ADC/status state are hardware registers. Watchdog settings may reset charger state if the driver does not service or disable the timer.

Dependencies and integration points: Requires I2C and regmap types via including consumers. Integrates with power-supply and regulator/OTG paths, and with the MFD parent if split into subfunctions.

Risks: Unit conversions are central; off-by-one or offset mistakes can over/under-charge. Register widths are 16-bit, so regmap configuration must match chip endianness/word size. Watchdog default behavior can revert charger programming.

Test signals: Regmap tests for 16-bit register access, conversion tests for current/voltage min/max/step values, charger state/fault decoding, ADC channel enable/readback, OTG enable, and watchdog disable/timeout behavior.
