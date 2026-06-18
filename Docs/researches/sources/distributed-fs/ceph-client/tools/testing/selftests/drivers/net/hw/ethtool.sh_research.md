# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool.sh

Purpose: Hardware link-mode/autonegotiation selftest using two connected interfaces.

Important APIs/functions: `h1_create()`, `h1_destroy()`, `h2_create()`, `h2_destroy()`, `setup_prepare()`, `cleanup()`, `same_speeds_autoneg_off()`, `different_speeds_autoneg_off()`, `combination_of_neg_on_and_off()`, `hex_speed_value_get()`, `subset_of_common_speeds_get()`, `speed_to_advertise_get()`, `advertise_subset_of_speeds()`, `check_highest_speed_is_chosen()`, `different_speeds_autoneg_on()`, and helpers from `ethtool_lib.sh`.

Control flow: The script initializes two interfaces with IPv4 addresses, builds a map of ethtool link mode bit positions, then runs tests for forced matching speeds, forced mismatched speeds, forced-vs-autoneg, advertising subsets, highest speed selection, and incompatible advertised modes. It checks link readiness and ping success/failure.

State and persistence: Changes ethtool speed/autoneg/advertise settings and restores autoneg at the end of cases. Interface IP state is cleaned by forwarding helpers.

Dependencies and integration points: Requires two cabled ports, ethtool link mode reporting, forwarding `lib.sh`, and common speed helper library.

Risks and test signals: Hardware support varies. Failures may indicate driver PHY link mode, autoneg advertisement, forced speed, or reporting regressions.
