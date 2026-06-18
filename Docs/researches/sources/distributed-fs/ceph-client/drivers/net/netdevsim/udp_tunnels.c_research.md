# sources/distributed-fs/ceph-client/drivers/net/netdevsim/udp_tunnels.c

Purpose: simulates UDP tunnel port offload tables for netdevsim and exposes debugfs knobs for reset, injected errors, and device-level mode flags.

Important APIs/types/functions: `nsim_udp_tunnel_info` defines two tables: VXLAN and Geneve/VXLAN-GPE. `nsim_udp_tunnel_set_port()`, `unset_port()`, and `sync_table()` update simulated table arrays. `nsim_udp_tunnels_info_create()` allocates per-device info and debugfs entries; `destroy()` frees them; `nsim_udp_tunnels_debugfs_create()` exposes global mode toggles.

Control flow: create rejects incompatible shared+open_only, selects per-netdev or shared arrays, creates debugfs arrays for both tables, installs reset and `inject_error`, duplicates the static info, then adapts callbacks and flags for sync-all, open-only, IPv4-only, shared, and static IANA VXLAN modes. Set/unset consume one injected error then update packed `(port,type)` entries. Reset clears arrays and notifies the UDP tunnel core.

State and persistence: table values are volatile `u32` arrays either per `netdevsim` or shared in `nsim_dev`. Debugfs toggles are mutable runtime state and affect subsequently created devices.

Dependencies and integration: uses `udp_tunnel_nic_info`, netdev `udp_tunnel_nic_info`, debugfs u32 arrays, and netdevsim device/port structures.

Risks: dynamically duplicating what normal drivers keep static is intentional for testing but requires explicit kfree. Shared mode couples multiple devices to the same arrays. Error injection is one-shot and negates the stored value into a return code.

Test signals: add/delete tunnel ports, force errors, reset registered devices, validate table debugfs contents, create devices with sync_all/open_only/ipv4_only/shared/static_iana_vxlan modes, and reject shared+open_only.
