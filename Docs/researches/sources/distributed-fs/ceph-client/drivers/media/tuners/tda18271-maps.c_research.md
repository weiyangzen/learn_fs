# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-maps.c

Purpose: provides all frequency-to-register lookup tables and default standard maps for the TDA18271 C1/C2 tuner variants.

Important APIs and functions: public helpers are `tda18271_lookup_thermometer`, `tda18271_lookup_cid_target`, `tda18271_lookup_rf_band`, `tda18271_lookup_pll_map`, `tda18271_lookup_map`, and `tda18271_assign_map_layout`. Static data includes C1/C2 main and calibration PLL maps, RF calibration maps, band-pass/filter/gain/IR/temperature maps, RF tracking templates, and C1/C2 `tda18271_std_map` defaults.

Control flow: `tda18271_assign_map_layout` selects the C1 or C2 map layout after hardware ID detection, copies the default standard map into private state, and initializes RF calibration state from the template. Lookup functions scan ascending maximum-frequency tables, return selected values, and emit debug-map traces.

State and persistence: static maps are immutable driver data. Per-device mutable state is only populated by copying the selected standard map and RF calibration template into `struct tda18271_priv`.

Dependencies and integration points: depends on private TDA18271 state and debug macros. Common and frontend files consume these lookups for PLL programming, RF tracking calibration, power scans, temperature compensation, and standard-specific IF/AGC values.

Risks: map searches are linear and rely on zero-terminated sorted tables; bad ordering or missing terminators would produce wrong tuning. Some out-of-range conditions intentionally return `-ERANGE`, while C1 RF-cal out-of-range is expected in high bands. Tables are hardware-calibration data with little algorithmic validation in code review.

Test signals: boundary-frequency tests for every lookup table, C1 vs C2 layout assignment, standard-map values for analog and digital modes, RF-band template copy, and debug traces around max-frequency transitions.
