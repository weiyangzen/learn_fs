# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.h

## Purpose
This header provides 420xx-specific constants and lifecycle declarations used by the QAT 420xx hardware-data implementation and family driver.

## Important APIs, Types, And Functions
- Hardware shape constants: `ADF_420XX_MAX_ACCELENGINES`, `ADF_420XX_ACCELENGINES_MASK`, and `ADF_420XX_ADMIN_AE_MASK`.
- Error/parity masks: CPP agent command parity, ATH/CPH, CPR/XLT, DCPR/UCS, PKE, WAT/WCP, and `ADF_420XX_SSMFEATREN_MASK`.
- Firmware names: `qat_420xx.bin`, `qat_420xx_mmp.bin`, and per-service object binaries for sym, DC, asym, and admin.
- Rate-limit constants: PCIe scale factors, decompression correction, scan rate, max throughput per service, and slice reference.
- Clock constant: `ADF_420XX_AE_FREQ`.
- Public functions: `adf_init_hw_data_420xx()` and `adf_clean_hw_data_420xx()`.

## Control Flow
The family driver includes this header to initialize and clean `struct adf_hw_device_data`. The C implementation uses the constants when installing gen4 operation hooks and reporting firmware/capability/rate-limit metadata.

## State And Persistence
The header owns no runtime state. Its constants define runtime hardware-data values loaded into device structures.

## Dependencies And Integration Points
It depends on `adf_accel_devices.h` and gen4/common QAT infrastructure that interprets these values.

## Risks
- Firmware filename constants must match installed firmware package names.
- Throughput and clock constants influence rate limiting and heartbeat timing; incorrect values can affect performance management.
- Error masks are hardware-specific and must remain synchronized with 420xx register definitions.

## Test Signals
- Build coverage for QAT 420xx.
- Firmware loading tests confirming all named binaries are requested as expected.
- Runtime sanity checks that reported number of AEs and masks match hardware documentation/SKU.
