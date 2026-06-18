<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-spmi-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/apple-spmi-nvmem.c

## Purpose
Exposes Apple SPMI PMIC address space as a byte-addressable NVMEM provider using a regmap over SPMI extended transfers.

## Important APIs, Types, And Functions
`apple_spmi_regmap_config` configures 16-bit registers and 8-bit values. `apple_spmi_nvmem_probe()` creates an SPMI regmap and registers an NVMEM device named `spmi_nvmem` with `regmap_bulk_read` and `regmap_bulk_write` as callbacks.

## Control Flow
The SPMI driver matches `apple,spmi-nvmem`. Probe initializes `devm_regmap_init_spmi_ext()`, stores the regmap as private data, and registers a 0xffff-byte, byte-stride NVMEM provider.

## State And Persistence
Runtime state is the regmap. Backing storage is SPMI-attached PMIC NVMEM or register-backed persistent settings, writable through the NVMEM core.

## Dependencies And Integration Points
Depends on SPMI, `REGMAP_SPMI`, the NVMEM provider framework, and Apple PMIC DT bindings. It allows cell consumers to access power or RTC-related persistent settings.

## Risks
The callbacks are cast to NVMEM function types, so their signatures must remain compatible. Exposing write access across the full 16-bit address range can be risky if bindings do not constrain cells. Regmap/SPMI errors propagate directly to consumers.

## Test Signals
Probe on Apple SPMI PMICs, read and write known safe cells, confirm regmap transaction sizes, and test invalid SPMI transfers. DT cell coverage should constrain consumers to documented offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-spmi-nvmem.c -->
