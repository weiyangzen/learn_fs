# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-fec.sh

Purpose: Validates ethtool Forward Error Correction configuration and reporting through netdevsim.

Important APIs/functions: Uses `ethtool-common.sh`, `make_netdev`, `ethtool --show-fec`/`--set-fec` or equivalent short options, and `check` counters. It verifies supported FEC modes, auto/off settings, and resulting active/configured mode display.

Control flow: After creating a netdevsim netdev, the script probes ethtool FEC support, applies valid FEC settings, checks they are reflected in ethtool output, and verifies invalid or unsupported combinations are rejected when applicable.

State and persistence: Changes only transient netdevsim FEC state associated with the generated port. Cleanup deletes the backing simulated device.

Dependencies and integration: Requires ethtool FEC support in userspace and the netdevsim kernel driver hooks. This is paired with broader standard-stat checks in `stats.py`.

Risks: Ettool output wording for FEC modes is version-sensitive. If netdevsim capabilities change, expected modes must be updated. Tests that assume all modes exist can over-fail on reduced kernel configs.

Test signals: A successful run shows valid FEC mode transitions, consistent displayed configured/active modes, correct rejection of invalid settings, and a final all-checks-passed report.
