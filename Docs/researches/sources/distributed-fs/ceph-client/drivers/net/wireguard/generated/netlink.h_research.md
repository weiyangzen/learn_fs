# sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.h

Purpose: Auto-generated declaration header for WireGuard Generic Netlink policy arrays, split operations, and handler prototypes.

Important APIs and types: Declares `wireguard_wgallowedip_nl_policy`, `wireguard_wgpeer_nl_policy`, `wireguard_nl_ops[2]`, and the handwritten callbacks `wg_get_device_start()`, `wg_get_device_done()`, `wg_get_device_dumpit()`, and `wg_set_device_doit()`.

Control flow: This header binds generated validation/dispatch tables to the handwritten implementation that registers the Generic Netlink family. It has no executable flow.

State and persistence: No state. It preserves the generated source contract derived from `Documentation/netlink/specs/wireguard.yaml`.

Dependencies and integration points: Includes netlink/genetlink headers, UAPI WireGuard definitions, and `linux/time_types.h`. Consumed by generated `netlink.c` and handwritten `netlink.c`.

Risks: Prototype or array-size drift breaks Generic Netlink registration. Hand editing the generated header risks divergence from the YAML schema.

Test signals: Compile WireGuard netlink registration, run get/set Generic Netlink commands, and compare regenerated output from `tools/net/ynl/ynl-regen.sh`.
