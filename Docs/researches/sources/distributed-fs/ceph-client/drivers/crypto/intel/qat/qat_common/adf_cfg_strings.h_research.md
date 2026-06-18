# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_strings.h

## Purpose
This header centralizes string keys and section names used by QAT configuration storage, generated defaults, user configuration, and debugfs display.

## Important APIs, Types, And Functions
Important constants include section names `ADF_GENERAL_SEC`, `ADF_KERNEL_SEC`, `ADF_ACCEL_SEC`; service strings `ADF_CFG_DC`, `ADF_CFG_DECOMP`, `ADF_CFG_CY`, `ADF_CFG_SYM`, `ADF_CFG_ASYM`, `ADF_CFG_DCC`; key names such as `ADF_SERVICES_ENABLED`, ring names, coalescing keys, core-affinity formats, heartbeat timer, and SR-IOV enabled flag. There are no functions.

## Control Flow
No runtime flow exists. Other code uses these constants to write and read exact key strings.

## State And Persistence Behavior
No mutable state exists. The strings become the stable names visible through debugfs and user config paths.

## Dependencies And Integration Points
It is included by config storage, service parsing, user config structs, Gen2/Gen4/Gen6 config generation, and control-device code.

## Risks
Renaming strings breaks user tools, default config lookup, and service parsing. Format strings for bank-specific settings must remain aligned with config generation code.

## Test Signals
Config ioctl round trips, debugfs `dev_cfg` output, service parsing, generated ring configuration, heartbeat config, and SR-IOV config are useful validation.
