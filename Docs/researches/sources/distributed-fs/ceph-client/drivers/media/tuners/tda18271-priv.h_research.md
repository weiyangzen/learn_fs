# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-priv.h

Purpose: private register definitions, state structure, debug macros, map types, and internal function prototypes for the TDA18271 driver.

Important APIs and types: defines register offsets for the 39-byte TDA18271 register file, `struct tda18271_rf_tracking_filter_cal`, PLL/version enums, opaque map layout, `struct tda18271_priv`, debug level bits, `tda_fail`, map type enum, and prototypes shared by common/maps/frontend files.

Control flow: this header ties the multi-file implementation together. The register constants index the shadow array, debug macros annotate map/register/calibration flow, and internal prototypes allow each compilation unit to call the shared lookup and hardware helpers.

State and persistence: `struct tda18271_priv` is the durable per-I2C-address state: register shadow, hybrid list node, I2C props, current mode/role/gate/version/options, board config, calibration state, selected maps, standard map, RF calibration table, lock, and cached IF/frequency/bandwidth.

Dependencies and integration points: includes kernel primitives, `tuner-i2c.h`, and the public TDA18271 header. It integrates with Linux DVB frontend state via `fe->tuner_priv`.

Risks: `tda_fail` references a local `priv` symbol, so it is only safe in functions that define that name. The shared private header exposes many internals across C files, increasing coupling. Debug macros can produce high-volume logs during calibration and map scanning.

Test signals: compile all three TDA18271 C files together, static analysis for `tda_fail` call sites, lock coverage around `tda18271_priv` mutations, and register-index validation against `TDA18271_NUM_REGS`.
