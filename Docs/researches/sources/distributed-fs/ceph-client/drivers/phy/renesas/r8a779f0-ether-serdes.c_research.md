# sources/distributed-fs/ceph-client/drivers/phy/renesas/r8a779f0-ether-serdes.c

## Purpose
This driver exposes the Renesas R-Car S4-8/R8A779F0 Ethernet SERDES as three generic PHY channels for Ethernet MAC consumers. It performs a shared black-box hardware initialization sequence, channel-specific SGMII/USXGMII programming, speed programming, and link-up monitoring.

## Important APIs, Types, And Functions
`struct r8a779f0_eth_serdes_drv_data` owns the common MMIO base, reset, three channel records, and an `initialized` flag. `struct r8a779f0_eth_serdes_channel` stores channel MMIO, PHY pointer, selected `phy_interface_t`, speed, and index. Register helpers `r8a779f0_eth_serdes_write32()`, `read32()`, and `reg_wait()` select a bank then access or poll offsets. Generic PHY callbacks are `init`, `exit`, `power_on`, `set_mode`, and `set_speed`. `r8a779f0_eth_serdes_xlate()` maps phandle arg 0 to one of three channels.

## Control Flow
Probe maps the common register area, obtains reset, creates three PHYs with per-channel base offsets, and registers an OF PHY provider. It then enables runtime PM and takes a runtime PM reference for the device lifetime. `.set_mode` accepts only `PHY_MODE_ETHERNET` with GMII, SGMII, or USXGMII submodes, though later channel setting only handles SGMII and USXGMII. `.set_speed` records the requested line speed. `.init` runs the common reset/RAM/combination-mode sequence once and marks the shared block initialized. `.power_on` runs late per-channel programming: channel mode table, speed programming, status toggles, and link-up polling/restarts.

## State And Persistence
Software state is the shared `initialized` boolean plus per-channel interface and speed. Hardware programming persists across PHY users until reset or driver exit; `.exit` clears the shared initialized flag rather than reference counting channel users, so multi-channel sequencing depends on generic PHY consumer ordering.

## Dependencies And Integration Points
The driver uses generic PHY, Linux PHY interface mode constants, platform MMIO, reset controller, runtime PM, polling/delay helpers, and compatible string `renesas,r8a779f0-ether-serdes`. It integrates with Ethernet MAC drivers through PHY phandles, `.set_mode`, `.set_speed`, and `.power_on`.

## Risks And Test Signals
The register sequences are explicitly undocumented "black magic", so small changes carry high hardware risk. GMII is accepted in `.set_mode` but not implemented by channel setup/speed paths, so consumers selecting GMII can reach `-EOPNOTSUPP` later. The shared `initialized` flag is not per-channel reference counted. Test signals include all three phandle indices, reset/common init once, SGMII 100/1000 speed writes, USXGMII setup, timeout diagnostics from `reg_wait()`, link-up retry behavior, and concurrent or repeated channel init/exit cycles.
