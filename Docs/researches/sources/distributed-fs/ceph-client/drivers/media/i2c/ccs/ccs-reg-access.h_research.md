# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.h

## Purpose
`ccs-reg-access.h` declares the CCS register access abstraction used by the core driver and quirks. It wraps generated `CCS_R_*` register macros into readable `ccs_read()` and `ccs_write()` call sites.

## Important APIs, Types, and Functions
The header declares `ccs_read_addr()`, `ccs_read_addr_8only()`, `ccs_read_addr_noconv()`, `ccs_write_addr()`, `ccs_write_data_regs()`, and `ccs_reg_conv()`. `CCS_REG_ADDR(reg)` strips a register descriptor to the 16-bit address. Macros `ccs_read(sensor, REG, val)` and `ccs_write(sensor, REG, val)` expand to generated `CCS_R_REG` descriptors.

## Control Flow
No implementation is present. The macros route typed logical register names to the functions in `ccs-reg-access.c`, where static data, quirks, CCI/regmap access, and conversion are applied.

## State and Persistence Behavior
The header stores no state. It defines accessors that operate on `struct ccs_sensor` runtime state and hardware registers.

## Dependencies and Integration Points
It includes Linux I2C/types and generated `ccs-regs.h`; it forward-declares `struct ccs_sensor`. It is included by `ccs.h`, so all core and quirk code can use symbolic CCS register accesses.

## Risks and Edge Cases
Callers must pass generated CCS register names without the `CCS_R_` prefix to the convenience macros. Using `ccs_read_addr_noconv()` bypasses real-number conversion and is appropriate for raw limit caching, not normal consumers. `CCS_REG_ADDR()` discards width and private conversion flags, so it is only suitable when a raw 16-bit address is intended.

## Test Signals
Compile coverage should catch invalid register names. Runtime tests should compare macro-based access against direct address access and verify converted versus non-converted reads for float/ireal capability registers.
