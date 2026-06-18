# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-cci.c

## Purpose
`v4l2-cci.c` provides MIPI Camera Control Interface register access helpers on top of regmap. It lets sensor drivers describe register address, width, and endianness through encoded `CCI_REG_*` values and then perform typed reads, writes, masked updates, register sequences, and I2C regmap initialization.

## Important APIs, types, and functions
Exported functions are `cci_read()`, `cci_write()`, `cci_update_bits()`, `cci_multi_reg_write()`, and, when `CONFIG_V4L2_CCI_I2C` is enabled, `devm_cci_regmap_init_i2c()`. They use `struct regmap`, `struct cci_reg_sequence`, `CCI_REG_LE`, `CCI_REG_WIDTH_BYTES()`, and `CCI_REG_ADDR()` from `<media/v4l2-cci.h>`.

## Control flow
`cci_read()` short-circuits if an optional accumulated error pointer is already set, decodes width/endianness/address, bulk-reads up to eight bytes, converts the buffer into a `u64`, and stores errors back through `err`. `cci_write()` mirrors that flow by encoding a `u64` into a byte buffer and bulk-writing it. `cci_update_bits()` reads the current value, applies `(readval & ~mask) | (val & mask)`, and writes it back. `cci_multi_reg_write()` writes each register sequence entry until one fails. The I2C initializer creates an 8-bit-value regmap with big-endian register formatting and disabled regmap locking.

## State and persistence behavior
The helpers do not keep private state. Register values persist only in the target hardware. The optional `int *err` parameter supports caller-side error accumulation across a sequence; once nonzero, later helper calls return that error without issuing more I/O.

## Dependencies and integration points
This file integrates camera sensor drivers with Linux regmap, I2C regmap support, unaligned endian accessors, and device logging. It is built under `CONFIG_V4L2_CCI`, with the I2C initializer gated by `CONFIG_V4L2_CCI_I2C`.

## Risks and edge cases
Unsupported encoded widths return `-EINVAL`; callers must use valid CCI register macros. Disabled regmap locking assumes callers provide any necessary serialization or that sensor register access is otherwise safe. `cci_update_bits()` is read-modify-write and is not atomic at the hardware level. Error accumulation is convenient but can hide later intended operations if callers reuse a stale nonzero error variable.

## Test signals
Unit-style tests can use a fake regmap to verify 1-, 2-, 3-, 4-, and 8-byte reads/writes in both endian modes, invalid width handling, accumulated-error short-circuiting, masked updates, and sequence abort on first error. Hardware tests should confirm sensor probe tables and runtime control updates produce expected bus transactions.
