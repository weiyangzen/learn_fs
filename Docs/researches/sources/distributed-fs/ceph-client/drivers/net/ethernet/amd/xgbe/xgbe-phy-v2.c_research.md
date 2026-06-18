# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v2.c

## Purpose
`xgbe-phy-v2.c` is the PHY backend for newer PCI XGBE devices. It supports many port/connection types: backplane, backplane without AN, 2.5G backplane, Base-T via external MDIO PHYs, Base-X, 10GBase-R, SFP/SFP+, optional redrivers, mailbox-driven rate changes, receiver reset cycles, CDR workarounds, and RX adaptation.

## Important APIs, Types, And Functions
- Local enums define port modes, connection types, SFP communication/cable/base/speed types, MDIO reset types, and redriver interface/model/modes.
- `struct xgbe_phy_data` stores port properties, SFP state, external PHY state, redriver state, current/start mode, and CDR/RRC counters.
- I2C helpers (`xgbe_phy_i2c_read/write`, SFP mux helpers, redriver I2C write) wrap `xgbe-i2c.c`.
- `xgbe_phy_get_comm_ownership` and `xgbe_phy_put_comm_ownership` serialize software and hardware ownership of muxed I2C/MDIO/GPIO resources.
- MDIO bus callbacks expose internal/external Clause 22 and Clause 45 access through a registered `mii_bus`.
- SFP helpers read GPIOs and EEPROM, verify checksums, parse module type, expose module info/EEPROM, and detect copper SFP PHY availability.
- External PHY helpers create/destroy `phy_device`, apply Bel-Fuse and Finisar quirks, and start PHY AN.
- AN outcome helpers resolve CL37, CL37 SGMII, CL73, and CL73-with-redriver results.
- Mode helpers map speeds/ports to `enum xgbe_mode` and issue mailbox rate-change commands.
- RX adaptation helpers stop/start data path around adaptation, retry mailbox/RX EQ flows, and track `rx_adapt_done`.
- `xgbe_phy_init/start/stop/reset/exit` and `xgbe_init_function_ptrs_phy_v2` provide the implementation interface.

## Control Flow
Init validates that the port is enabled, initializes I2C, reads hardware property registers `pp0`/`pp3`/`pp4`, validates port/connection/speed/redriver combinations, sets supported link modes and start mode based on port mode, configures SFP GPIO/mux metadata when needed, configures external MDIO mode, registers an internal `mii_bus`, and caches PHY data. Start begins I2C, configures redriver MDIO mode, sets the highest supported start mode, handles CDR tracking, detects SFP modules, and attaches an external PHY when present. Link status repeatedly detects SFP changes, polls external PHYs, reads PCS status, runs RX adaptation when enabled, restarts AN on relevant down states, and periodically triggers receiver reset cycles. Stop frees external PHYs, resets SFP state, restores CDR tracking, powers off PHY firmware, and stops I2C.

## State And Persistence
The file owns substantial runtime state in `struct xgbe_phy_data`: `port_mode`, `conn_type`, `port_speeds`, `mdio_addr`, SFP GPIO and EEPROM fields, `sfp_changed`, `sfp_mod_absent`, `sfp_phy_avail`, `phydev`, `mii`, reset/redriver metadata, `cur_mode`, `start_mode`, `rrc_count`, `phy_cdr_notrack`, and `phy_cdr_delay`. It also updates shared `pdata` fields such as `kr_redrv`, `an_again`, `en_rx_adap`, `rx_adapt_retries`, `rx_adapt_done`, `data_path_stopped`, and `mode_set`. State is runtime and re-derived on probe or SFP changes.

## Dependencies And Integration Points
This backend depends on PCI-populated property registers, the private I2C controller, hardware MDIO/GPIO callbacks, Linux PHYLIB, Linux ethtool module EEPROM APIs, mailbox scratch/int registers, common AN/link management in `xgbe-mdio.c`, and version-data workarounds from `xgbe-pci.c`. `xgbe-ethtool.c` reaches module info and EEPROM through this implementation.

## Risks
This is one of the highest-risk files in the subset. Hardware resource ownership spans a software mutex and hardware mutex registers; failure paths must always release ownership. SFP probing treats EEPROM/I2C errors as module absence, which is practical but can mask bus faults. Redriver settings are board-specific and validation must match supported models/lanes. Static version-data flags changed by PCI probing affect behavior such as RRC and CDR workarounds. RX adaptation deliberately stops TX/RX data path to prevent packet corruption; regressions here can cause link stalls or CRC errors. PHY quirks hard-code vendor/part behavior.

## Test Signals
Test every port mode available in hardware, including SFP insertion/removal, copper SFP external PHY attach/detach, `ethtool -m`, Base-T speeds from 10M to 10G, redriver MDIO and I2C paths, CL37/CL73 AN, no-AN backplane, RX adaptation success/failure, receiver reset cycles, suspend/resume via PCI, and mailbox timeout recovery. Important logs include SFP EEPROM/GPIO I2C errors, hardware mutex timeout, redriver setting errors, firmware mailbox timeout, and link mode transitions.
