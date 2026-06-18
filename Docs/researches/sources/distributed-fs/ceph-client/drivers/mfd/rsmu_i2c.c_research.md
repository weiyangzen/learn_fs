# sources/distributed-fs/ceph-client/drivers/mfd/rsmu_i2c.c

### Purpose
`rsmu_i2c.c` is the I2C bus glue for Renesas/IDT SMU devices. It builds the right regmap for ClockMatrix, SABRE, or SnowLotus devices, implements custom paged register access for ClockMatrix over either full I2C or SMBus block operations, and then delegates child registration to `rsmu_core_init()`.

### Important APIs, Types, And Functions
Main functions are `rsmu_i2c_probe()`, `rsmu_i2c_remove()`, `rsmu_write_page_register()`, low-level I2C/SMBus block helpers, and custom regmap callbacks `rsmu_i2c_reg_read/write()` plus `rsmu_smbus_i2c_reg_read/write()`. Static configs include ClockMatrix full-I2C and SMBus regmaps, SABRE range-window regmap, and SnowLotus 16-bit big-endian regmap.

### Control Flow
Probe allocates `struct rsmu_ddata`, stores it as I2C client data, assigns device and type from the I2C ID table, selects a regmap config, initializes the regmap, and calls `rsmu_core_init()`. For ClockMatrix, it prefers full I2C transfer support and falls back to SMBus I2C block support; custom callbacks set the page register when the target register is in SCSR space, then access the low byte offset. For SABRE and SnowLotus, standard `devm_regmap_init_i2c()` is used with range or 16-bit register formatting.

### State, Persistence, And Dependencies
Runtime state includes `rsmu->page`, which caches the last selected ClockMatrix page, and `rsmu->lock` initialized by the core. ClockMatrix regmaps use `REGCACHE_NONE`; SABRE uses maple cache with all registers volatile except the page selector, and SnowLotus uses no cache. Dependencies include I2C/SMBus APIs, regmap, MFD core, OF/I2C ID tables, and the public/private RSMU headers.

### Integration Points
The I2C ID and OF tables cover `8a34000`, `8a34001`, `82p33810`, `82p33811`, `8v19n850`, and `8v19n851`. The core exposes PHC and char-device children after bus setup. Child drivers depend on correct bus-specific regmap behavior, especially for paged ClockMatrix SCSR registers.

### Risks
`rsmu_i2c_write_device()` does not verify that `i2c_master_send()` wrote `bytes + 1`, so partial positive sends are treated as success. The page cache is per parent and not guarded in the bus callback itself; correctness relies on higher-level locking by child users. Casting `(u8 *)val` for reads assumes one-byte values and host memory layout is acceptable for regmap's use here. Adapter capability selection can choose SMBus fallback with smaller transfer semantics, so bulk access limits need coverage.

### Test Signals
Test ClockMatrix reads/writes below and above `RSMU_CM_SCSR_BASE`, page transitions, repeated same-page accesses, and both full I2C and SMBus block paths. Test SABRE virtual range access across the 128-byte windows and SnowLotus 16-bit big-endian addressing. Fault tests should cover unsupported adapters, regmap init failures, partial transfers, and child registration failure.
