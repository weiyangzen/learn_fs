# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshci-dwc.h

## Purpose
`ufshci-dwc.h` defines DesignWare UFSHCI-specific host-controller register offsets, clock-divider values, and selector indexes used by DWC helper code and DWC host variants.

## Important APIs, Types, And Macros
The header provides `enum dwc_specific_registers` with `DWC_UFS_REG_HCLKDIV`, `enum clk_div_values` with 62.5/125/200 MHz encoded divider values, and `enum selector_index` for lane TX/RX selector indexes.

## Control Flow And State
The header is declarative only. `ufshcd-dwc.c` uses `DWC_UFS_REG_HCLKDIV` and `DWC_UFS_REG_HCLKDIV_DIV_125` during link startup PRE_CHANGE.

## Dependencies And Integration Points
It is paired with `ufshcd-dwc.c` and `ufshcd-dwc.h`. DWC host integrations can include it when they need DWC-specific register constants distinct from generic UFSHCI registers.

## Risks And Edge Cases
Divider enum values are encoded as hexadecimal MHz equivalents and assume the controller's expected representation. Integrations with different HCLK requirements must not blindly use the 125 MHz default.

## Test Signals
Runtime validation is the DWC clock-divider write during link startup and successful link bring-up. Static tests should ensure no generic UFSHCI code accidentally depends on DWC-only constants.
