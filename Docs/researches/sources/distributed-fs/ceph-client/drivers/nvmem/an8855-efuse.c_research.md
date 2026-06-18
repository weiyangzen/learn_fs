<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/an8855-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/an8855-efuse.c

## Purpose
Exposes Airoha AN8855 switch eFuse words as a read-only NVMEM provider backed by the parent MFD regmap.

## Important APIs, Types, And Functions
`an8855_efuse_read()` performs `regmap_bulk_read()` from `AN8855_EFUSE_DATA0 + offset`. `an8855_efuse_probe()` obtains the parent regmap, fills an `nvmem_config` with 50 32-bit cells, 32-bit stride/word size, and registers through `devm_nvmem_register()`.

## Control Flow
The platform driver matches `airoha,an8855-efuse`. Probe fetches the parent regmap, attaches it as provider private data, and registers the NVMEM device. Reads are direct bulk register reads in word units.

## State And Persistence
The only driver state is the regmap pointer stored as `config.priv`. Fuse contents are hardware-persistent and read-only from this provider.

## Dependencies And Integration Points
Depends on a parent device exposing a regmap, platform/OF matching, and the NVMEM provider core. Consumers access calibration cells via standard NVMEM APIs or fixed DT cells.

## Risks
Offsets are treated as byte offsets while bulk count is `bytes / sizeof(u32)`, so NVMEM core alignment via 32-bit stride and word size is important. Missing parent regmap returns `-ENOENT`.

## Test Signals
Probe under an AN8855 MFD parent, read aligned 32-bit cells, verify sysfs or NVMEM consumer output matches hardware documentation, and test failure when no parent regmap exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/an8855-efuse.c -->
