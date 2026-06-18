# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.h

## Purpose
`nci.h` defines S3FWRN5 proprietary NCI opcodes and command/response payload layouts used for RF-register and firmware clock configuration.

## Important APIs and types
- `NCI_PROP_SET_RFREG`, `NCI_PROP_START_RFREG`, `NCI_PROP_STOP_RFREG`, and `NCI_PROP_FW_CFG` are proprietary command identifiers under the NCI proprietary group.
- `struct nci_prop_set_rfreg_cmd` carries a section index plus up to 252 data bytes.
- `struct nci_prop_stop_rfreg_cmd` carries the final checksum.
- `struct nci_prop_fw_cfg_cmd` carries clock type, speed, and request settings.
- The header exports `s3fwrn5_nci_prop_ops` and `s3fwrn5_nci_rf_configure()`.

## Control flow and integration
The shared NCI ops in `core.c` register these proprietary response handlers. Firmware-update flow calls RF configuration through the exported function after returning the chip to NCI mode.

## State, dependencies, and risks
There is no standalone state. The layouts must match firmware expectations exactly; `set_rfreg` has a fixed 252-byte payload that matches the chunk size in `nci.c`. Endianness of the checksum field should be verified against chip documentation because the code writes native `__u16`.

## Test signals
Build tests should catch declaration drift between `nci.c` and the header. Runtime tests should validate the wire payloads for all four proprietary commands.
