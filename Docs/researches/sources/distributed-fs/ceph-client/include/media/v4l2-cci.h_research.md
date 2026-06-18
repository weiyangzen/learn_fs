# sources/distributed-fs/ceph-client/include/media/v4l2-cci.h

## Purpose
Declares MIPI Camera Control Interface register encoding and regmap-backed access helpers for camera sensor drivers.

## Important APIs, Types, and Functions
`struct cci_reg_sequence` stores encoded register/value pairs. Macros encode register address, width, little-endian flag, private bits, and helpers to extract address/width. Constructors include `CCI_REG8/16/24/32/64` and little-endian variants. APIs include `cci_read()`, `cci_write()`, `cci_update_bits()`, `cci_multi_reg_write()`, and optional `devm_cci_regmap_init_i2c()`.

## Control Flow
Drivers encode each register with width metadata, then call CCI helpers. If an optional error pointer already contains an error, operations are skipped, allowing compact sequential setup code. Multi-register writes handle heterogenous register widths.

## State and Persistence Behavior
No persistent state is owned; register state persists in the target sensor. Optional error accumulator carries transient failure state across a sequence.

## Dependencies and Integration Points
Depends on bitfield/bits/types, regmap, and optionally I2C CCI regmap support. Integrates modern camera sensor drivers with width-aware register access.

## Risks
Using raw addresses instead of `CCI_REG*()` loses width metadata. `cci_update_bits()` is read-modify-write and explicitly not atomic against other CCI accesses. Endianness flag must match device register layout.

## Test Signals
Read/write for every width, little-endian register tests, error-accumulator skip behavior, multi-register write sequences, update-bits races under locking, and I2C regmap init with 8/16-bit register addresses.
