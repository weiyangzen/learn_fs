# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.h

## Purpose
`ufshcd-dwc.h` declares the DesignWare UFS helper interface and shared RMMI/M-PHY constants used by DWC-based UFS host drivers.

## Important APIs, Types, And Macros
The public declarations are `ufshcd_dwc_link_startup_notify()` and `ufshcd_dwc_dme_set_attrs()`. `struct ufshcd_dme_attr_val` packages a DME attribute selector, value, and peer/local target flag for batch writes. The header also defines RMMI attributes such as `CBREFCLKCTRL2`, `CBCRCTRL`, and `CBCREG*`, M-PHY state attributes `MTX_FSM_STATE` and `MRX_FSM_STATE`, per-lane M-PHY register macros, and TX/RX FSM state enums.

## Control Flow And State
The header has no flow or storage. It defines the structure format consumed by `ufshcd_dwc_dme_set_attrs()` and symbolic constants consumed by DWC integrations during PHY/link setup.

## Dependencies And Integration Points
It includes `<ufs/ufshcd.h>` for UFS types and is paired with `ufshcd-dwc.c` and `ufshci-dwc.h`. DWC host variants can include it to reuse exported helpers and M-PHY constants.

## Risks And Edge Cases
Constants describe DWC M-PHY/RMMI behavior and may not apply to non-DWC controllers. The `peer` field is a small integer matching the DME peer/local convention; callers must provide the correct value.

## Test Signals
Compile tests validate ABI with `ufshcd-dwc.c`. Runtime use is covered by DWC link startup tests and any host driver that batches DME attribute programming with `struct ufshcd_dme_attr_val`.
