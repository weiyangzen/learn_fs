# sources/distributed-fs/ceph-client/include/linux/phylink.h

## Purpose
PHYLINK MAC/PHY/PCS coordination contract for network drivers. It abstracts fixed links, PHY-managed links, and in-band-negotiated links, validating MAC/PCS capabilities and coordinating link-up/down, EEE, pause, WoL, suspend/resume, and ethtool operations.

## Important APIs, Types, and Functions
Defines mode and capability bits (`MLO_PAUSE_*`, `MLO_AN_*`, `PHYLINK_PCS_NEG_*`, `MAC_*`), `struct phylink_link_state`, `struct phylink_config`, `struct phylink_mac_ops`, `struct phylink_pcs`, and `struct phylink_pcs_ops`. Lifecycle APIs include `phylink_create()`, `phylink_destroy()`, `phylink_connect_phy()`, firmware-node connect helpers, fixed-link setup, `phylink_start()`, `phylink_stop()`, suspend/resume helpers, and MAC/PCS change notifications. EtHTool APIs cover ksettings, pause, EEE, WoL, nway reset, MII ioctl, and speed down/up.

## Control Flow
Drivers create phylink with MAC ops and config, connect a PHY/fixed link/fwnode, then start link management. Major reconfiguration calls `mac_prepare()`, `mac_config()`, PCS config/restart as needed, and `mac_finish()`. Link resolution calls PCS/MAC link-up/down in the correct order and supports in-band state changes through `phylink_mac_change()` or `phylink_pcs_change()`.

## State and Persistence
Opaque `struct phylink` holds runtime state outside the header. Persistent inputs in `phylink_config` include supported interfaces, MAC/LPI capabilities, PM policy, fixed-state callback, EEE defaults, and WoL policy. `phylink_pcs` persists PCS ops, supported interface bitmap, polling flag, and phylink backpointer.

## Dependencies and Integration Points
Depends on Ethernet PHYLIB, PCS drivers, netdevice, ethtool, workqueues, spinlocks, EEE config, fwnode/device-tree, and MAC drivers. It integrates media-specific MII C22/C45 PCS helpers and USXGMII/C73 decode helpers.

## Risks
MAC ops must not use invalid fields in `mac_config()`, and must avoid link bouncing for pause-only updates. Incorrect negotiation mode selection, PCS restart handling, or pause capability advertisement can cause unstable links. EEE and RX-clock stop interactions are sensitive during suspend and LPI.

## Test Signals
Phylink-enabled MAC driver tests, fixed/PHY/in-band mode coverage, PCS validation/config tests, ethtool ksettings/pause/EEE/WoL tests, suspend/resume with WoL, and link replay/change notification tests.
