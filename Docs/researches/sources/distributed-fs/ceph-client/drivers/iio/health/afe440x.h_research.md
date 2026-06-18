# sources/distributed-fs/ceph-client/drivers/iio/health/afe440x.h

Purpose: Shared private header for TI AFE440x health drivers. It centralizes common register addresses, bit definitions, IIO channel construction macros, table-backed sysfs helpers, and the custom attribute container used by the AFE4404 driver.

Important APIs/types/functions: Defines common AFE440x timing/result/control registers and control bits such as `AFE440X_CONTROL0_SW_RESET`, `AFE440X_CONTROL1_TIMEREN`, `AFE440X_TIAGAIN_ENSEPGAIN`, and `AFE440X_CONTROL2_PDN_AFE`. `AFE440X_INTENSITY_CHAN()` creates signed 24-bit IIO intensity scan channels with raw plus optional info masks. `AFE440X_CURRENT_CHAN()` creates output current channels with raw and scale. `struct afe440x_val_table` represents integer plus micro-fraction values. `AFE440X_TABLE_ATTR()` emits read-only availability attributes. `struct afe440x_attr`, `to_afe440x_attr()`, and `AFE440X_ATTR()` define writable table-backed device attributes whose show/store callbacks are implemented in the C driver.

Control flow: This file has no runtime code except macro-expanded sysfs show functions. Driver code supplies tables and callbacks; the macros expand into static attributes and channel specs that the IIO core registers through attribute groups and channel arrays.

State and persistence: No independent state is stored here. The generated `afe440x_attr` instances persist as static objects in consuming drivers and carry a regmap-field id plus lookup table metadata.

Dependencies and integration points: Requires IIO channel definitions and Linux bit macros through including C files. It is tightly coupled to AFE440x register layout and to callbacks named `afe440x_show_register` and `afe440x_store_register` in the consuming translation unit.

Risks: Macro coupling is implicit: `AFE440X_ATTR()` assumes callback names and table lifetimes exist in the includer. The table attribute macro writes `buf[len - 1] = '\n'`, so empty tables would underflow, though current tables are non-empty. Channel macros assign `.address` and `.scan_index` from the same `_index`, so enum values used by consumers must be valid scan positions.

Test signals: Compile consumers with sparse/W=1 to catch macro misuse. Validate generated sysfs availability text, channel scan types, and that all enum indices used by consuming drivers align with channel arrays and lookup tables.
