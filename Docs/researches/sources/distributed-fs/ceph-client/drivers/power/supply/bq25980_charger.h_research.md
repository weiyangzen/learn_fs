# sources/distributed-fs/ceph-client/drivers/power/supply/bq25980_charger.h

Purpose: defines the register map, bit masks, ADC scaling constants, watchdog values, and per-model electrical limits shared by the BQ25980 charger implementation.

Important APIs/types/functions: the header declares register addresses from `BQ25980_BATOVP` through `BQ25980_CHRGR_CTRL_6`, thresholds for BUS OCP/OVP, BAT OVP/OCP across BQ25980/BQ25975/BQ25960 variants, control bits such as `BQ25980_EN_BYPASS`, `BQ25980_CHG_EN`, `BQ25980_EN_HIZ`, and `BQ25980_ADC_EN`, status masks for OVP/OCP/thermal/watchdog/presence, ADC step constants, and watchdog configuration constants used by `bq25980_charger.c`.

Control flow: this header has no direct runtime flow. Its constants drive regmap default tables, device-tree validation, property conversion, health/status decoding, and register bit updates in the C file.

State and persistence: no independent state. The values are compile-time contracts for interpreting persistent charger hardware registers and volatile status/ADC registers.

Dependencies and integration: depends on kernel bit macros such as `BIT()` and `GENMASK()` through the including C file. It is private to the BQ25980 driver and intentionally not an exported UAPI.

Risks and test signals: any datasheet mismatch here propagates to unsafe charge limits or incorrect status reporting. Several constants are model-specific but similarly named, so tests should cover all three chip table entries, especially min/max boundaries, ADC sign polarity, watchdog disable/max encoding, and bypass versus switched-capacitor OVP/OCP conversions.
