# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-coalesce.sh

Purpose: Validates ethtool coalescing configuration on a generated netdevsim netdev.

Important APIs/functions: Sources `ethtool-common.sh` for `make_netdev`, `check`, and cleanup. `SETTINGS_MAP` maps ethtool `-C` option names to `ethtool -c` output labels. `get_value` reads current settings via `awk`; `update_current_settings` refreshes an associative array for comparison.

Control flow: The script skips if ethtool lacks coalesce support, creates a netdevsim netdev, captures initial expected values, then iterates over all coalesce knobs assigning random 32-bit values with `ethtool -C`. After each change it compares the full current settings vector to the expected vector. It separately tests `adaptive-rx` and `adaptive-tx` display formatting.

State and persistence: Mutates coalesce settings on the temporary netdevsim port. The helper trap should delete the netdevsim device on exit.

Dependencies and integration: Requires bash associative arrays, ethtool text output format, netdevsim, and the local common helper.

Risks: Parsing is text-based and sensitive to ethtool label changes. Iterating `${!SETTINGS_MAP[@]}` has unspecified order, but both expected/current arrays are expanded consistently in the same shell. Random high values assume netdevsim accepts the full range.

Test signals: Each knob update must be observable in `ethtool -c`, adaptive booleans must report expected paired status, and final output reports all checks passed.
