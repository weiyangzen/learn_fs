<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw-mbq.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw-mbq.c

Purpose: Adds SoundWire SDCA Multi-Byte Quantity regmap support, including variable MBQ sizes and deferrable busy handling.

Important APIs/types/functions: `struct regmap_mbq_context` stores device, slave, readable callback, MBQ config, and max value size. `regmap_sdw_mbq_size()`, `regmap_sdw_mbq_deferrable()`, `regmap_sdw_mbq_poll_busy()`, `regmap_sdw_mbq_write_impl()`, and `regmap_sdw_mbq_read_impl()` implement MBQ-specific behavior. Exported wrappers are `__regmap_init_sdw_mbq()` and `__devm_regmap_init_sdw_mbq()`.

Control flow: Config validation requires 32-bit registers, zero pad bits, and value widths that fit `unsigned int`. Read/write determine per-register MBQ size, perform multi-byte accesses using `SDW_SDCA_MBQ_CTL(reg)` for upper bytes and the base register for the low byte, and retry once if the SoundWire operation returns `-ENODATA`. Deferrable controls may poll the function busy bit via `read_poll_timeout(sdw_read_no_pm, ...)`; otherwise the code sleeps for the configured timeout before retrying.

State and persistence behavior: Context is device-managed allocation. It persists MBQ policy callbacks and the value-size ceiling. No register state is cached here beyond what regmap core may provide.

Dependencies and integration points: Depends on SoundWire no-PM read/write APIs, SDCA register macros, polling/sleep helpers, and regmap bus callbacks. Integrates with drivers using SDCA MBQ controls over SoundWire.

Risks: `config->readable_reg` is stored and called when polling busy; configs without it would be unsafe if a deferrable transaction reaches `regmap_sdw_mbq_poll_busy()`. Invalid MBQ callback sizes fail with `-EINVAL`. The retry model handles only one busy wait and one retry, so repeated device busy states propagate. Non-deferrable controls that defer are only warned, not rejected.

Test signals: Cover config rejection, fixed and callback MBQ sizes, byte ordering across MBQ control registers, `-ENODATA` retry, busy polling timeout, and readable-vs-sleep fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw-mbq.c -->
