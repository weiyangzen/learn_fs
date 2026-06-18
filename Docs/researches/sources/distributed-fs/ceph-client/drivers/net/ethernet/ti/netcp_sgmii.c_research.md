# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_sgmii.c

## Purpose
`netcp_sgmii.c` provides the small SGMII register helper layer used by the TI KeyStone NetCP Ethernet subsystem. It resets SGMII ports, toggles runtime reset, reports port link state, and programs SGMII control/advertisement values for MAC-MAC autonegotiation, MAC-PHY, forced MAC-MAC, and fiber-style modes.

The file is not a standalone driver. It is called by `netcp_ethss.c` during slave open/stop and periodic link polling.

## Important APIs, Types, And Functions
The exported helper APIs are `netcp_sgmii_reset()`, `netcp_sgmii_rtreset()`, `netcp_sgmii_get_port_link()`, and `netcp_sgmii_config()`. All take a mapped SGMII base pointer and a zero-based port number.

Internal helpers are `sgmii_write_reg()`, `sgmii_read_reg()`, and `sgmii_write_reg_bit()`. Register address macros calculate per-port offsets with `SGMII_OFFSET()`, using a separate formula for ports 2 and 3 so callers can pass the appropriate base for SGMII 3/4 windows.

Important register bits are `SGMII_SRESET_RESET`, `SGMII_SRESET_RTRESET`, `SGMII_REG_STATUS_LOCK`, `SGMII_REG_STATUS_LINK`, `SGMII_REG_STATUS_AUTONEG`, and `SGMII_REG_CONTROL_AUTONEG`.

## Control Flow
`netcp_sgmii_reset()` sets the soft-reset bit in the per-port reset register and busy-waits until hardware clears it. There is no timeout in this loop, so it assumes the SGMII block is responsive.

`netcp_sgmii_rtreset()` reads the reset register, returns the previous runtime-reset bit value, sets or clears the bit according to the caller, writes the result, and issues a write memory barrier. `netcp_ethss.c` uses this to hold non-XGMII ports in reset while stopping and to release them while opening.

`netcp_sgmii_get_port_link()` reads the status register and returns `1` when `SGMII_REG_STATUS_LINK` is set, otherwise `0`.

`netcp_sgmii_config()` first translates the `link-interface` value into MR advertisement and control register values. It supports `SGMII_LINK_MAC_MAC_AUTONEG`, `SGMII_LINK_MAC_PHY`, `SGMII_LINK_MAC_PHY_NO_MDIO`, `SGMII_LINK_MAC_MAC_FORCED`, and `SGMII_LINK_MAC_FIBER`; unsupported values trigger `WARN_ONCE()` and `-EINVAL`. The function clears control, waits up to 1000 one-to-two millisecond sleeps for SerDes PLL lock, logs an error if lock is absent, writes advertisement and control, then waits up to 1000 short sleeps for link and, when autoneg is enabled, autoneg completion.

## State And Persistence Behavior
The file maintains no software state. It mutates memory-mapped SGMII registers. Reset, runtime reset, advertisement, and control settings persist in hardware until changed or reset. Link state is read directly from hardware each time.

## Dependencies And Integration Points
The file includes `netcp.h` for link-interface constants, MMIO helpers, bit macros, sleeps, and warning/logging infrastructure. Its only consumers in this work item are `netcp_ethss.c` helper paths: `gbe_sgmii_config()`, `gbe_sgmii_rtreset()`, and `netcp_ethss_update_link_state()`.

The base pointer passed by `netcp_ethss.c` differs by hardware generation and slave index through `SGMII_BASE()`, so the offset math here relies on the caller selecting the right window for ports 0/1 versus 2/3.

## Risks And Edge Cases
`netcp_sgmii_reset()` can spin forever if hardware never clears the reset bit. `netcp_sgmii_config()` logs PLL lock failure but still proceeds to program advertisement/control and returns success even if final link/autoneg polling times out. Callers therefore cannot distinguish a failed link setup from a slow or absent link by return code.

The port offset logic is compact but sensitive to caller assumptions. Passing a port greater than expected or the wrong SGMII base can program the wrong register window. Interface constants must stay aligned with `netcp.h` and device-tree `link-interface` values.

## Test Signals
Test with SGMII MAC-PHY, MAC-PHY no-MDIO, forced MAC-MAC, MAC-MAC autoneg, and fiber configurations. Hardware or emulation tests should confirm reset completion, runtime reset bit preservation/return value, PLL lock logging, link/autoneg polling, and correct port offset selection for ports 0 through 3. Watch for "serdes PLL not locked" and `WARN_ONCE` invalid-interface messages.
