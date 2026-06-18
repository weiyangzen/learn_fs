## sources/distributed-fs/ceph-client/drivers/iio/dac/rohm-bd79703.c

Purpose: SPI IIO voltage driver for ROHM BD79700/BD79701/BD79702/BD79703 DAC variants. It abstracts 12-bit command transfers as 8-bit regmap addresses plus 8-bit DAC values.

Important APIs/types/functions: `struct bd7970x_chip_data` supplies name, channel table, count, and whether a separate VFS supply exists. `struct bd79703_data` stores regmap and full-scale voltage. `bd79703_write_raw()` writes the 8-bit value to the channel address; `bd79703_read_raw()` reports scale only.

Control flow: Probe gets chip data, initializes an SPI regmap with 8-bit registers and values, enables `vcc` and optionally reads/enables `vfs`, assigns channel table, writes zero to all outputs, and registers. BD79702 uses non-linear channel addresses for physical channels 0,1,4,5.

State and persistence: No raw cache and no readback are exposed. Regmap has a maple cache, but raw reads do not use it. Outputs are initialized to zero on probe.

Dependencies and integration points: Uses SPI regmap, regulators `vcc` and optional `vfs`, OF/SPI IDs, and IIO scale/raw ABI.

Risks and test signals: Check the 12-bit command abstraction with actual SPI controller word size, BD79702 address mapping, separate VFS vs VCC scale calculation, and all-output zero register behavior. Tests should verify raw bounds, scale for each variant, and probe failure cleanup when VFS is absent.
