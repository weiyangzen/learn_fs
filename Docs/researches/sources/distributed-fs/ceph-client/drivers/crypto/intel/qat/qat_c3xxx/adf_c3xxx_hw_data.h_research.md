# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.h

## Purpose
This header defines C3xxx PF hardware constants: BAR IDs, accelerator and AE limits/masks, softstrap offset, ETR bank count, AE-to-function mapping register counts, clock frequency bounds, firmware names, and hardware-data init/clean declarations.

## Important APIs, Types, And Functions
Public declarations are `adf_init_hw_data_c3xxx()` and `adf_clean_hw_data_c3xxx()`. Important constants include `ADF_C3XXX_MAX_ACCELERATORS`, `ADF_C3XXX_MAX_ACCELENGINES`, `ADF_C3XXX_ACCELERATORS_REG_OFFSET`, `ADF_C3XXX_ETR_MAX_BANKS`, `ADF_C3XXX_MIN_AE_FREQ`, `ADF_C3XXX_MAX_AE_FREQ`, `ADF_C3XXX_FW`, and `ADF_C3XXX_MMP`.

## Control Flow
The header has no executable flow. Its constants are consumed by `adf_c3xxx_hw_data.c` and the C3xxx PCI probe code when reading softstraps, mapping BARs, validating clock measurements, and loading firmware.

## State And Persistence Behavior
No mutable state exists. The constants compile into C3xxx runtime callbacks and module firmware metadata.

## Dependencies And Integration Points
It includes Linux unit helpers and integrates with Gen2 QAT common code, PCI probing, firmware loading, and SR-IOV AE-to-function mapping.

## Risks
Incorrect mask or BAR IDs can prevent probe or misroute CSR access. Clock bounds that do not match silicon can reject valid devices or hide invalid timings. Firmware names must match installed firmware packages.

## Test Signals
Build coverage, successful PCI probe, firmware request for C3xxx binaries, correct 6-AE SKU detection, valid BAR access, and Gen2 SR-IOV mapping are the key signals.
