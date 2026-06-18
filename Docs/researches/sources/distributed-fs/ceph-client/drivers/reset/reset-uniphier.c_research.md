# sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier.c

Purpose: UniPhier SoC reset controller for system, media I/O, SD, peripheral, and analog amplifier reset blocks using syscon regmaps and SoC-specific ID tables.

Important APIs/types/functions: `uniphier_reset_data` records ID, register, bit, and active-low flag. Macros define active-high and active-low entries with sentinel termination. `uniphier_reset_update()` searches the table and writes the target bit with polarity handling. `uniphier_reset_status()` reads and applies polarity. Probe gets parent syscon regmap and computes `nr_resets` from max ID.

Control flow: compatible match selects a reset table; runtime ops linear-search for the requested binding ID. Unknown IDs log and return `-EINVAL`.

State and persistence: static tables encode layout; parent syscon registers store reset state. Software state is devm allocated.

Dependencies and integration: syscon parent nodes, regmap, many UniPhier OF compatibles, reset-controller framework.

Risks and test signals: linear search supports sparse IDs safely but scales with table length. `val = ~mask` relies on `regmap_write_bits()` masking correctly. Test all compatible/table mappings, unknown IDs, active-low and active-high entries, and parent syscon lookup failure.
