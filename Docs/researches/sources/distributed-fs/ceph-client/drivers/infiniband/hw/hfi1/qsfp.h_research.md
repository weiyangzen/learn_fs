# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.h

## Purpose
`qsfp.h` defines QSFP device constants, SFF-8636 byte offsets, technology/power/attenuation helpers, interrupt flag masks, per-port QSFP cache state, and public QSFP/I2C APIs for the HFI1 driver.

## Important APIs, Types, And Functions
The header defines the QSFP I2C address, power/mod-presence delays, page/cache sizes, 128-byte read/write boundary, page-select offset, required module fields, monitor ranges, power/CDR/TX control offsets, technology classification macros, OUI helpers, alarm/warning masks, and attenuation helpers. `struct qsfp_data` holds the per-port cache, work item, spinlock, and state flags. It declares cache refresh, power-class, presence, cable-info, raw I2C, QSFP paged read/write, one-shot read, and I2C setup/cleanup functions.

## Control Flow
Callers use the constants to interpret cached QSFP bytes and the prototypes to refresh or access module memory. The cache layout stores five logical 128-byte chunks: lower page 0, upper page 0, and optional upper pages 1-3, matching cable-info query mapping rather than raw 256-byte page layout.

## State And Persistence
`struct qsfp_data` is volatile per-port state. `cache_valid` and `cache_refresh_required` indicate whether cached module bytes can be used; `reset_needed` and `limiting_active` coordinate with platform tuning after the driver has modified active modules.

## Dependencies And Integration Points
The header is consumed by QSFP implementation, platform tuning, management query code, and link bring-up. Its offsets and masks are contracts with SFF-8636 module memory and HFI1 ASIC GPIO pin wiring.

## Risks
Incorrect offsets or technology bitmaps directly affect cable qualification and tuning. Cache size and address mapping must match both `refresh_qsfp_cache()` and `get_cable_info()`. State flags are compact `u8`s updated from multiple contexts, requiring the implementation's locking discipline to be preserved.

## Test Signals
Validate power-class mappings, technology classification macros across all 16 high-nibble values, address-to-cache mapping, monitor range constants, alarm bit masks, QSFP state transitions after refresh/reset, and compile coverage for all public API users.
