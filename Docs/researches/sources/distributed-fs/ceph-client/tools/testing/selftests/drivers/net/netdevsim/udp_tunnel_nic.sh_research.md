# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/udp_tunnel_nic.sh

Purpose: Regression-tests UDP tunnel port offload table synchronization between tunnel devices, ethtool feature state, and netdevsim NIC tables.

Important APIs/functions: Defines helpers for creating/deleting VxLAN and Geneve devices, encoding/printing table entries, reading netdevsim debugfs UDP port tables, checking ethtool `--show-tunnels`, discovering new netdev names, and cleanup. Uses debugfs modes such as `udp_ports_open_only`, `sync_all`, `ipv4_only`, `shared`, `static_iana_vxlan`, per-port `inject_error`, and `reset`.

Control flow: The script runs multiple scenarios: basic tunnel add/delete and link state, module unload cleanup, port add/delete, open-only/sync-all/IPv4-only behavior, error injection, feature toggling, table reset, shared tables across two ports, overflow handling, and static IANA VxLAN ports. It compares expected arrays to debugfs and ethtool output after each mutation.

State and persistence: Creates netdevsim devices/ports, VxLAN/Geneve netdevs, toggles ethtool offload features, loads/unloads tunnel modules, and mutates debugfs table controls. Cleanup removes tunnels and devices.

Dependencies and integration: Requires netdevsim, vxlan/geneve/udp_tunnel modules, ethtool tunnel display support for full coverage, `iproute2`, debugfs, and root.

Risks: This is highly stateful and long; missed cleanup can poison later scenarios. Table ordering and overflow behavior must match netdevsim exactly. It conditionally degrades when ethtool lacks `show-tunnels`.

Test signals: PASS means debugfs NIC tables and ethtool tunnel dumps match expected encoded entries through all tunnel lifecycle, feature toggle, error, reset, shared-table, and static-port scenarios.
