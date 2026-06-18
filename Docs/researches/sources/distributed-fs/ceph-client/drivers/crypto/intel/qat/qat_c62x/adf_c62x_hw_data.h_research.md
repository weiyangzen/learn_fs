# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.h

## Purpose
This header defines C62x PF hardware constants for BAR layout, accelerator/AE masks, softstrap offset, ETR bank count, AE-to-function mapping register counts, AE frequency limits, firmware names, and hardware-data lifecycle declarations.

## Important APIs, Types, And Functions
It declares `adf_init_hw_data_c62x()` and `adf_clean_hw_data_c62x()`. Important constants include `ADF_C62X_MAX_ACCELERATORS`, `ADF_C62X_MAX_ACCELENGINES`, `ADF_C62X_ACCELERATORS_MASK`, `ADF_C62X_ACCELENGINES_MASK`, `ADF_C62X_ETR_MAX_BANKS`, `ADF_C62X_AE_FREQ`, `ADF_C62X_MIN_AE_FREQ`, `ADF_C62X_MAX_AE_FREQ`, `ADF_C62X_FW`, and `ADF_C62X_MMP`.

## Control Flow
No executable flow exists. The constants are used by C62x probe and hardware-data code to map BARs, compute masks, configure SR-IOV AE mapping, validate clocks, and request firmware.

## State And Persistence Behavior
No mutable state exists. The header provides compile-time hardware contracts.

## Dependencies And Integration Points
It includes Linux units and integrates with Gen2 QAT common code, firmware loading, PCI probing, and SR-IOV configuration.

## Risks
Incorrect BAR IDs or masks can break CSR access or misreport hardware resources. Clock bounds directly affect `adf_dev_measure_clock()` validation. Firmware names must match the kernel firmware package.

## Test Signals
Build coverage, C62x PCI probe, firmware request success, correct 8/10 AE SKU detection, clock measurement, and SR-IOV operation validate this header indirectly.
