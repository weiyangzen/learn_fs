# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.h

## Purpose
This header defines QAT 4xxx hardware constants used by the 4xxx hardware-data implementation and PCI driver. It names accelerator-engine limits, AE/admin masks, parity/error feature masks, firmware binaries for 4xxx and 402xx variants, rate-limiting constants, and AE frequency.

## Important APIs, Types, And Functions
The public functions are `adf_init_hw_data_4xxx(struct adf_hw_device_data *hw_data, u32 dev_id)` and `adf_clean_hw_data_4xxx(struct adf_hw_device_data *hw_data)`. Constants include `ADF_4XXX_MAX_ACCELENGINES`, `ADF_4XXX_ACCELENGINES_MASK`, `ADF_4XXX_ADMIN_AE_MASK`, firmware names such as `ADF_4XXX_FW`, `ADF_402XX_FW`, and RL constants such as `ADF_4XXX_RL_MAX_TP_SYM`.

## Control Flow
The header has no runtime control flow. Its values are read by `adf_4xxx_hw_data.c` during hardware-data initialization, firmware-object selection, error-mask setup, and rate-limiting setup.

## State And Persistence Behavior
There is no mutable state. The constants become compile-time ABI between device-specific code and the common QAT framework.

## Dependencies And Integration Points
It includes Linux unit helpers and `adf_accel_devices.h`. It is integrated with Gen4 common code, firmware loading, error handling, and the PCI driver's `MODULE_FIRMWARE()` declarations.

## Risks
Firmware-name or mask drift causes probe or firmware loading failures that may only appear on specific SKUs. Error-mask constants are hardware-contract values; wrong bits can hide parity faults or report false errors. Throughput/RL constants affect throttling behavior.

## Test Signals
Build coverage validates declarations. Runtime signals include successful 4xxx/402xx firmware requests, correct AE/admin masks, expected rate-limit capacities, and error/RAS handling that matches documented hardware behavior.
