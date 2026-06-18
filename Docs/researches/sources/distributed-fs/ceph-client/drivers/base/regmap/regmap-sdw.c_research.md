<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw.c

Purpose: Provides general SoundWire regmap support for 32-bit little-endian register addresses and byte payloads.

Important APIs/types/functions: `regmap_sdw_write()`, `regmap_sdw_gather_write()`, and `regmap_sdw_read()` wrap `sdw_nwrite_no_pm()` and `sdw_nread_no_pm()`. `regmap_sdw_config_check()` validates supported regmap formats. Exported wrappers are `__regmap_init_sdw()` and `__devm_regmap_init_sdw()`.

Control flow: The normal write path expects the first four bytes of the formatted buffer to be the destination address and writes the remaining bytes. Gather write decodes the separate register buffer and writes the value buffer. Read decodes the register buffer and reads requested bytes. Initialization rejects non-32-bit register addresses, nonzero pad bits, and `can_multi_write` because only bulk writes are supported.

State and persistence behavior: No adapter-owned persistent state exists. Each transfer decodes its address from the current buffer and delegates to SoundWire.

Dependencies and integration points: Depends on SoundWire slave helpers, little-endian decoding, regmap core formatting, and no-PM SoundWire access APIs.

Risks: Callers must use 32-bit register fields and no pad bits. Multi-register writes are rejected because the transport does not implement regmap multi-write semantics. Address bytes are always little-endian.

Test signals: Validate config rejection, write/gather/read address decoding, value length calculation, and propagation of SoundWire errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw.c -->
