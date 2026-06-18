# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.c

## Purpose
`ccs-reg-access.c` centralizes CCS register reads and writes over the CCI/regmap layer, including conversion of CCS real-number encodings, static-data read-only register lookup, quirk interception, and bulk writes of manufacturer-specific register data.

## Important APIs, Types, and Functions
Exported functions are `ccs_reg_conv()`, `ccs_read_addr()`, `ccs_read_addr_8only()`, `ccs_read_addr_noconv()`, `ccs_write_addr()`, and `ccs_write_data_regs()`. Conversion helpers are `float_to_u32_mul_1000000()` and `ireal32_to_u32_mul_1000000()`. Static-data lookup is implemented by `__ccs_static_data_read_ro_reg()` and `ccs_static_data_read_ro_reg()`.

## Control Flow
Reads call `ccs_read_addr_raw()`. If enabled, it first searches parsed sensor and module static read-only register arrays. If not found, it calls a register-access quirk that may handle, redirect, or fail the access. It then reads the register through `cci_read()` and optionally converts float/ireal values. Writes first call a write quirk and then use `cci_write()`. Bulk writes iterate parsed `struct ccs_reg` arrays in chunks up to `MAX_WRITE_LEN`, log a hex string, retry failed `regmap_bulk_write()` calls up to ten times with 1 ms sleeps, and abort on persistent error.

## State and Persistence Behavior
The file stores no long-lived state. It reads from `sensor->sdata` and `sensor->mdata`, writes volatile hardware registers, and returns converted scalar values to callers. Manufacturer-specific writes are not persisted beyond sensor power state.

## Dependencies and Integration Points
It depends on `ccs.h`, generated register flags from `ccs-regs.h`, limit access for `CLOCK_CAPA_TYPE_CAPABILITY`, V4L2 subdev client lookup, CCI/regmap APIs, parsed static data from `ccs-data.h`, and quirk hooks from `ccs-quirk.h`.

## Risks and Edge Cases
`__ccs_read_addr()` accepts `only8` but does not currently use it directly; 8-bit-read-only behavior relies on the CCI/reg encoding and quirk path. Static read-only lookup assumes sorted/non-overlapping parsed register ranges; malformed or unsorted firmware can cause unexpected misses. Conversion saturates infinity/overflow to `~0` or `U32_MAX` and reports NaN/negative values as zero. Bulk writes to manufacturer registers may partially program a device before a later retry failure.

## Test Signals
Validate live CCI reads/writes for 8/16/32-bit registers; static-data override reads; float and ireal conversion paths; 8-bit-read-only quirked sensors; quirk-suppressed accesses; manufacturer-register bulk writes with chunks larger than 32 bytes; and retry/error logging on transient bus failures.
