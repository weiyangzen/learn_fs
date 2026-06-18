# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_phylink.c

## Purpose
`fbnic_phylink.c` adapts FBNIC MAC/PCS state to Linux phylink and XPCS. It creates/destroys phylink objects, maps firmware AUI modes to PHY interfaces, reports ethtool link/FEC/pause data, and performs MAC prepare/finish/link-up/link-down callbacks.

## Important APIs, Types, And Functions
Public APIs are `fbnic_phylink_get_pauseparam()`, `fbnic_phylink_set_pauseparam()`, `fbnic_phylink_ethtool_ksettings_get()`, `fbnic_phylink_get_fecparam()`, `fbnic_phylink_create()`, `fbnic_phylink_destroy()`, and `fbnic_phylink_pmd_training_complete_notify()`. The callback table `fbnic_phylink_mac_ops` implements PCS selection, MAC prepare/config/finish, and link state transitions.

## Control Flow
Creation instantiates an XPCS PCS over the FBNIC synthetic MDIO bus, fills `phylink_config` capabilities and supported interfaces, obtains firmware AUI/FEC defaults, and creates phylink with the selected interface. MAC prepare masks/clears PCS interrupts and resets PMD state if link is absent. MAC finish rechecks link and reenables link-change interrupts. Link-down calls the MAC hook and increments `link_down_events`; link-up stores pause state, configures RX drop mode based on TX pause, and calls the MAC link-up hook.

PMD training notification runs from service work. If the state is training and the four-second timer has elapsed, it atomically advances through LINK_READY to SEND_DATA and calls `phylink_pcs_change()` so phylink can observe stable link.

## State And Persistence
Phylink and PCS pointers live in `fbnic_net`. AUI/FEC mode, `tx_pause`, and link-down counters are stored there too. PMD state and training deadline live in `fbnic_dev`. Hardware MAC state is changed through the `fbnic_mac` vtable.

## Dependencies And Integration Points
The file depends on Linux phylink, PHY interface enums, `pcs-xpcs`, the synthetic MDIO bus, MAC hooks, TX/RX drop-mode configuration, and netdev ethtool integration. `fbnic_netdev.c` creates/destroys phylink and forwards ethtool calls; PCI service work calls training notification.

## Risks
FEC support is inferred from supported link modes and firmware defaults; mismatches can expose unsupported ethtool modes. The training state machine uses atomic compare/exchange and barriers; skipped notifications can delay carrier, while premature transitions can log link flaps. Link-up drop mode depends on TX pause and RX queue count, so pause configuration affects data-path loss behavior.

## Test Signals
Signals include phylink create/destroy success, correct interface selection for 25G/50G/50G-R2/100G-R2, ethtool FEC and lanes reporting, pause get/set propagation, carrier changes after training completion, link-down event count increments, and RX drop-mode changes when pause changes.
