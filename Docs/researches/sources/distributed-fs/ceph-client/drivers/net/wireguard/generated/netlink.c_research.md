# sources/distributed-fs/ceph-client/drivers/net/wireguard/generated/netlink.c

Purpose: Auto-generated Generic Netlink policy and split-op table for the WireGuard control API, generated from `Documentation/netlink/specs/wireguard.yaml`.

Important APIs and definitions: Defines exported policy arrays `wireguard_wgallowedip_nl_policy` and `wireguard_wgpeer_nl_policy`, plus command-specific `wireguard_get_device_nl_policy` and `wireguard_set_device_nl_policy`. Exports `wireguard_nl_ops[2]`, mapping `WG_CMD_GET_DEVICE` to `wg_get_device_start()`, `wg_get_device_dumpit()`, and `wg_get_device_done()`, and `WG_CMD_SET_DEVICE` to `wg_set_device_doit()`.

Control flow: Generic Netlink validates request attributes against these policies before invoking the handwritten handlers in `netlink.c`. The dump op permits admin dump capability; the set op permits admin doit capability. Nested peers and allowed IPs use nested array policies.

State and persistence: Owns no mutable runtime state. The arrays are kernel ABI validation data and must match UAPI `linux/wireguard.h` and the generated header.

Dependencies and integration points: Includes netlink/genetlink headers, `generated/netlink.h`, UAPI WireGuard definitions, and time types. Integrated by `netlink.c` through the `genl_family.split_ops` pointer.

Risks: Because this is generated, manual edits can be lost or drift from YAML/UAPI. Policy length/mask mistakes could either reject valid userspace configurations or admit malformed keys, flags, endpoints, or nested allowed IPs.

Test signals: Generic netlink get/set smoke tests, malformed attribute length tests, invalid flag mask tests, nested peer/allowedip parsing, and regeneration diff against the YAML spec.
