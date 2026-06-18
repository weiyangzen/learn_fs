# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_extended_state.sh

Purpose: Tests ethtool extended link state/substate reporting for no partner and forced-mode mismatch scenarios.

Important APIs/functions: `setup_prepare()`, `ethtool_ext_state()`, `autoneg()`, `autoneg_force_mode()`, `no_cable()`, `busywait`, `ethtool_set`, `different_speeds_get`, and forwarding helpers.

Control flow: It selects two connected ports plus `NETIF_NO_CABLE`, checks a single up port reports `Autoneg, No partner detected`, forces different speeds on two ports and checks `No partner detected during force mode`, and checks the no-cable interface reports expected extended state.

State and persistence: Changes link up/down and ethtool speed/autoneg settings; cleanup/restoration comes from helper behavior.

Dependencies and integration points: Requires ethtool extended state strings, cabled and no-cable interfaces, and common ethtool library.

Risks and test signals: String parsing is sensitive to ethtool output format. Failures indicate extended state reporting regressions or unsupported testbed topology.
