## sources/distributed-fs/ipfs-kubo/test/sharness/t0141-addfilter.sh

Purpose: tests swarm address filter configuration through legacy and current config paths.

Important APIs and helpers: defines `test_swarm_filter_cmd`, `test_config_swarm_addrfilters_cmd`, and `test_swarm_filters`. Uses `ipfs swarm filters`, `ipfs config Swarm.AddrFilters`, `ipfs config --json`, and `test_cmp`.

Control flow and state: starts from a repo without filters, adds and removes filter entries through swarm filter commands, verifies output, then manipulates the config array directly and checks the resulting filters list. Persistent state is the `Swarm.AddrFilters` config.

Dependencies and integration points: covers multiaddr filter parsing, config serialization, compatibility between command and config interfaces, and command output stability.

Risks and test signals: catches filter entries not persisting, duplicate or malformed output, and divergence between config and `swarm filters`. Passing is exact output comparison for each mutation scenario.
