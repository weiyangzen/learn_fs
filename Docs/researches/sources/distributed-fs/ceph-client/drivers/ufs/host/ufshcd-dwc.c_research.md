# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.c

## Purpose
`ufshcd-dwc.c` provides shared helper logic for UFS hosts built around the Synopsys DesignWare Core. It programs the DWC clock divider, verifies link-up state, configures local and peer UniPro CPort/application connection attributes, and exports a link-startup notify callback for DWC-based platform drivers.

## Important APIs, Types, And Functions
Two symbols are exported: `ufshcd_dwc_dme_set_attrs()` and `ufshcd_dwc_link_startup_notify()`. `ufshcd_dwc_dme_set_attrs()` applies an array of `struct ufshcd_dme_attr_val` with `ufshcd_dme_set_attr()`. `ufshcd_dwc_link_startup_notify()` is intended for use as a UFS variant `.link_startup_notify` callback. Private helpers are `ufshcd_dwc_program_clk_div()`, `ufshcd_dwc_link_is_up()`, and `ufshcd_dwc_connection_setup()`.

## Control Flow And State
During PRE_CHANGE link startup, the driver writes `DWC_UFS_REG_HCLKDIV_DIV_125` to the DWC `HCLKDIV` register and invokes variant PHY initialization through `ufshcd_vops_phy_initialization()`. During POST_CHANGE, it reads `VS_POWERSTATE`; if the link is up it marks the HBA link active, then applies a static sequence of local and peer DME attributes to establish device IDs, peer IDs, CPort flags/mode, traffic class, and connection state.

No persistent private state is stored in this file. All state updates are made directly in the UFS core HBA or in UniPro attributes.

## Dependencies And Integration Points
The helpers depend on UFS core DME accessors, UniPro attribute IDs, and DWC register definitions from `ufshci-dwc.h`. They are exported for other DWC host drivers to reuse rather than registering a bus driver themselves.

## Risks And Edge Cases
The fixed 125 MHz divider and static CPort setup may be inappropriate for DWC integrations with different reference clocks or firmware-preconfigured connections. `ufshcd_dwc_link_is_up()` returns `1` rather than a negative errno on link-down, so callers should treat any nonzero as failure. DME attribute programming stops on first error, leaving a partially configured connection.

## Test Signals
Test with DWC-based hardware by observing PRE clock-divider write, PHY initialization callback execution, POST `VS_POWERSTATE` link-up detection, and successful traffic after connection setup. Negative tests should inject DME failures and link-down status.
