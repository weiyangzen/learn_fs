# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/qsfp.c

## Purpose
`qsfp.c` implements HFI1 QSFP I2C bus support, paged QSFP memory reads/writes, QSFP cache refresh, cable-info query support, module presence detection, power-class decoding, and human-readable cable dumps.

## Important APIs, Types, And Functions
`set_up_i2c()` creates two bit-banged I2C adapters over ASIC QSFP GPIO CSRs using `hfi1_setsda()`, `hfi1_setscl()`, `hfi1_getsda()`, and `hfi1_getscl()`. `i2c_write()` and `i2c_read()` are resource-checked raw I2C accessors. `qsfp_write()` and `qsfp_read()` handle SFF-8636 page selection and 128-byte boundary limits. `one_qsfp_read()` wraps a single read with QSFP resource acquisition. `refresh_qsfp_cache()` reads lower/upper page 0 and optional upper pages into the 128-byte-chunk cache. `get_cable_info()` serves SMA cable-info reads from cache while refreshing dynamic monitor bytes. `get_qsfp_power_class()`, `qsfp_mod_present()`, and `qsfp_dump()` expose common cable metadata.

## Control Flow
I2C setup allocates adapter objects and registers them with the Linux bit-bang I2C core. Accessors select bus 0 or 1 by target, convert the shifted QSFP address into a 7-bit I2C address and offset-size, and require the caller to hold the matching chip resource except for raw internal helpers. QSFP paged reads/writes repeatedly set byte 127 to the target page, delay after writes, then transfer a chunk that does not cross a 128-byte boundary. Cache refresh clears stale data and `cache_valid`, verifies module presence, reads mandatory page 0, conditionally reads optional pages based on paging/status bits, and marks the cache valid. Cable-info reads validate port/address/cache, copy cached bytes, and live-refresh monitor ranges.

## State And Persistence
I2C adapter objects live in `hfi1_asic_data`. Per-port QSFP state lives in `struct qsfp_data`: cached bytes, lock, validity/refresh flags, reset-needed and limiting-active flags. QSFP module memory writes persist in the module until reset/removal or power state changes, but the driver treats cache as volatile and invalidates it before refresh.

## Dependencies And Integration Points
The file depends on Linux I2C bit-bang APIs, HFI1 CSR access, chip resource locking, QSFP constants from `qsfp.h`, port/device data, and platform/link tuning code. `platform.c` uses the read/write/cache APIs to qualify and tune cables; management query paths use `get_cable_info()` and `qsfp_dump()`.

## Risks
`set_up_i2c()` can leak the first adapter if the second allocation/registration fails unless caller cleanup handles the partial state. Page selection before every chunk adds write delays and can fail mid-transfer, returning short counts. Cache validity is protected by a spinlock, but cache byte array reads are not fully serialized against refresh. `get_cable_info()` zero-fills only `excess_len`, which is usually `len` on early errors but must stay correct for partial overrange copies.

## Test Signals
Test I2C adapter registration failure for bus0/bus1, resource-check rejection, offset sizes 0/1/2, page-boundary splitting, short read/write failures, module absent, optional page combinations, cache invalidation after cable swap, dynamic monitor refresh overlap cases, overrange cable-info zero fill, power-class decoding, and dump formatting with invalid cache.
