# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxlgmac2.h

Purpose: Defines the small XLGMAC-specific extension to the XGMAC2 register contract: high-speed link speed encodings and the XLGMAC RX queue enable register offset.

Important APIs and data: Macros cover `XLGMAC_CONFIG_SS` speed fields for 1G, 2.5G, 10G, 25G, 40G, 50G, and 100G plus `XLGMAC_RXQ_ENABLE_CTRL0`. These are used by `dwxgmac2_core.c` in `dwxlgmac2_setup()` and `dwxlgmac2_rx_queue_enable()`.

Control flow and state: No runtime code exists here. Runtime state affected by these macros is the link speed selection in the MAC configuration register and per-RX-queue enable mode.

Dependencies and integration: The header assumes kernel bit helpers are already available through including sources. It integrates with the shared XGMAC2 code path instead of defining a separate driver.

Risks and test signals: Wrong speed encodings would make phylink speed changes fail only on XLGMAC devices. Test XLGMAC setup, all high-speed modes, queue enablement for AVB and DCB, and fallback rejection when the device ID does not match `DWXLGMAC_ID`.
