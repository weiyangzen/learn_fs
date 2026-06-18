
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_pci_id_tbl.h

## Purpose
`hinic3_pci_id_tbl.h` centralizes PCI device IDs for hinic3 physical and virtual functions.

## Important APIs, Types, And Functions
- `PCI_DEV_ID_HINIC3_PF` is `0x0222`.
- `PCI_DEV_ID_HINIC3_VF` is `0x375F`.

## Control Flow
There is no control flow. The constants are intended for PCI device-id tables in probe code elsewhere in the hinic3 driver.

## State And Persistence Behavior
No runtime state is stored. The identifiers are compile-time constants.

## Dependencies And Integration Points
This header has only include guards. It integrates with PCI probe/registration code that matches Huawei hinic3 PF/VF devices.

## Risks And Edge Cases
Incorrect IDs would prevent device binding or bind the driver to unsupported hardware. Any future revision support should be added with explicit compatibility validation.

## Test Signals
Build-time usage in PCI tables and runtime probe logs for PF/VF devices are the primary signals.
