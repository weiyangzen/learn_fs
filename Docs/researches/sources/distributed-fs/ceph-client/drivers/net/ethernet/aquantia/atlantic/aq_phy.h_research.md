<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.h

Purpose: declares MDIO and PHY helper APIs for Atlantic hardware code.

Important APIs/types: defines `HW_ATL_PHY_ID_MAX` and declares raw MDIO busy/read/write helpers, semaphore-protected PHY register read/write helpers, PHY ID initialization, PHY init, and PTP-disable workaround.

Control flow: callers use `aq_phy_init` to ensure `aq_hw->phy_id` is valid, use `aq_phy_read_reg`/`aq_phy_write_reg` for MMD register access, and call `aq_phy_disable_ptp` when hardware capability quirks require disabling PHY PTP blocks.

State and persistence: the header itself has no state. Implementations mutate `aq_hw_s` PHY ID and device registers.

Dependencies and integration: includes Linux MDIO definitions, low-level Atlantic register headers, hardware utilities, and `aq_hw`. It is consumed by `aq_nic.c` and B0 hardware PTP/GPIO support.

Risks: the header exposes low-level operations that assume the caller has a live `aq_hw_s` and valid MMIO mapping; misuse during remove/suspend can touch absent hardware. Test signals are build coverage plus PHY init and PTP GPIO paths on TP adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_phy.h -->
