# sources/distributed-fs/ceph-client/net/ncsi/ncsi-netlink.c

## Purpose
This file exposes NCSI status and control through generic netlink. It lets users query package/channel topology, choose preferred package/channel, clear preferences, send raw NCSI commands, configure package/channel masks, and receive command responses, timeouts, or errors.

## APIs, Types, and Functions
The generic netlink family is `NCSI`. Policy entries validate ifindex, package/channel IDs, binary command data, multi flags, and masks. Static handlers include `ndp_from_ifindex()`, `ncsi_write_channel_info()`, `ncsi_write_package_info()`, `ncsi_pkg_info_nl()`, `ncsi_pkg_info_all_nl()`, `ncsi_set_interface_nl()`, `ncsi_clear_interface_nl()`, `ncsi_send_cmd_nl()`, `ncsi_set_package_mask_nl()`, and `ncsi_set_channel_mask_nl()`. Exported internal response helpers are `ncsi_send_netlink_rsp()`, `ncsi_send_netlink_timeout()`, and `ncsi_send_netlink_err()`.

## Control Flow
Query handlers resolve an NCSI device by network namespace and ifindex, then serialize package/channel data into nested attributes. Set-interface and clear-interface handlers mutate package/channel whitelists, preferred channel pointers, multi-mode flags, and trigger `ncsi_reset_dev()` to reconfigure hardware. Raw command handling validates package/channel bounds and a minimum NCSI header, derives type and payload from user data, sends the command as netlink-driven, and reports immediate send errors through netlink. Response and timeout helpers construct replies using saved request sequence and port IDs.

## State and Persistence
Netlink commands persist changes in `ncsi_dev_priv.package_whitelist`, `multi_package`, per-package `channel_whitelist`, `multi_channel`, and `preferred_channel`. Raw command requests persist reply routing metadata in `struct ncsi_request` until response/timeout. The generic netlink family is registered at `subsys_initcall` time.

## Dependencies and Integration
The file depends on generic netlink, public `uapi/linux/ncsi.h` attributes/commands, internal topology structures, command TX, response timeout/error paths, and device reset logic. It is the administrative interface for `ncsi-manage.c` state.

## Risks
Topology is walked with RCU-style macros but without a single high-level snapshot lock during serialization, so users can observe concurrent changes. `ndp_from_ifindex()` gets and puts the netdev but returns an internal pointer whose lifetime depends on NCSI unregister synchronization. Mask operations can disable all channels or request multi-package mode without HWA, which is guarded only in package-mask handling. Raw command payloads are bounded to 2048 bytes but still depend on lower command-builder sizing.

## Test Signals
Netlink tests should query single and all packages, force preferred package/channel, clear preferences, set masks and multi flags, send raw commands with success, timeout, unsupported command, and malformed payload cases, and verify that management reset/reconfiguration follows persistent setting changes.
