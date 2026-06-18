# sources/distributed-fs/ceph-client/drivers/mfd/stmpe.h

## Purpose
`stmpe.h` is the private interface and register map header for the STMPE core and its I2C/SPI transport wrappers. It defines variant metadata, transport callbacks, exported core entry points, interrupt bits, and register constants for supported STMPE chips.

## Important APIs, Types, and Functions
`struct stmpe_variant_block` binds an MFD cell, base IRQ, and block ID. `struct stmpe_variant_info` describes chip ID/mask, GPIO count, alternate-function width, register index table, block table, IRQ count, and callbacks. `struct stmpe_client_info` is the transport abstraction consumed by `stmpe_probe()`. Declarations include `stmpe_probe()`, `stmpe_remove()`, and `stmpe_dev_pm_ops`.

## Control Flow
The header has no executable control flow. The core uses these definitions to select register addresses, enable blocks, configure autosleep, and register child cells for each variant.

## State and Persistence
It defines constants and type layouts only. Runtime state is held in `struct stmpe` from the public MFD header and in variant instances declared in `stmpe.c`.

## Dependencies and Integration Points
It depends on Linux device, MFD core, public `linux/mfd/stmpe.h`, printk, and basic types. The private transport wrappers include this header to call the common core.

## Risks and Edge Cases
Register constants include variant-specific byte ordering and LSB/MSB conventions, so child drivers are sensitive to correct register-index tables in `stmpe.c`. The duplicated comment block in the simple transport abstraction is harmless but signals legacy maintenance.

## Test Signals
Build coverage across I2C and SPI wrappers, all variant table initializers, and child drivers using public STMPE definitions exercises this header.
