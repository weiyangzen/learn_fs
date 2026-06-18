# sources/distributed-fs/ceph-client/drivers/reset/reset-ti-syscon.c

Purpose: TI syscon reset provider whose reset layout is described entirely by the `ti,reset-bits` DT property.

Important APIs/types/functions: `ti_syscon_reset_control` records assert/deassert/status offsets, bits, and flags from `dt-bindings/reset/ti-syscon.h`. Reset ops implement flag-driven set/clear/unsupported semantics. `ti_syscon_reset_probe()` gets parent syscon regmap, parses seven-cell control entries, allocates an array, and registers `nr_resets`.

Control flow: at probe, DT data becomes a fixed table. Consumers index that table; assert/deassert write configured bits and status reads configured status bit with flag polarity.

State and persistence: parsed control array is device-managed. Hardware syscon registers hold reset state.

Dependencies and integration: syscon parent node, regmap, OF property parsing, TI reset flag binding, platform reset-controller framework.

Risks and test signals: malformed properties are rejected only by cell count; semantic validation of bit ranges/flags relies on bindings. Test each flag combination, unsupported assert/deassert/status, parent syscon absence, and big-endian property parsing.
