# sources/distributed-fs/ceph-client/net/psp/psp_nl.c

## Purpose
`psp_nl.c` implements PSP generic-netlink management operations. It exposes device discovery/configuration, key rotation, RX/TX association setup for TCP sockets, and PSP device statistics. It is the control-plane bridge between userspace netlink clients and PSP device/socket internals.

## Important APIs, Types, And Functions
Key public entry points are `psp_device_get_locked()`, `psp_device_unlock()`, `psp_nl_dev_get_doit()`, `psp_nl_dev_get_dumpit()`, `psp_nl_dev_set_doit()`, `psp_nl_key_rotate_doit()`, `psp_assoc_device_get_locked()`, `psp_nl_rx_assoc_doit()`, `psp_nl_tx_assoc_doit()`, `psp_nl_get_stats_doit()`, and `psp_nl_get_stats_dumpit()`. Helpers `psp_nl_reply_new()` and `psp_nl_reply_send()` create single-message generic-netlink replies. `psp_nl_dev_fill()` and `psp_nl_stats_fill()` serialize device and stats attributes. `psp_nl_parse_key()` and `psp_nl_put_key()` translate nested key attributes with SPI and raw key bytes.

The code depends on generated PSP netlink policy and family definitions from `psp-nl-gen.h`, and on core PSP structures and operations from `psp.h`/`net/psp.h`: `struct psp_dev`, `struct psp_assoc`, `struct psp_key_parsed`, `struct psp_dev_config`, and driver `psd->ops`.

## Control Flow
Device operations first resolve a device id from `PSP_A_DEV_ID`, take the global `psp_devs_lock`, look up `psp_devs` by xarray id, then take the device mutex and check namespace/device access. Get/dump paths serialize device state into generic-netlink messages. Set validates requested enabled PSP versions against device capabilities, calls `psd->ops->set_config()`, updates cached config, and emits a management notification.

Key rotation creates both an immediate reply and a use-notification. It suggests a next generation number, calls the driver `key_rotate()`, validates the resulting generation, marks associations rotated via `psp_assocs_key_rotated()`, increments stats, multicasts on `PSP_NLGRP_USE`, and replies.

Association operations resolve a TCP socket fd, infer or validate the PSP device attached to the socket route, lock that device, parse version/key attributes, and call socket-layer functions. RX association allocates a `psp_assoc`, asks the driver for an RX SPI/key, returns that key to userspace, and attaches the association to the socket. TX association parses a userspace-provided key and upgrades the existing RX association for transmit.

## State And Persistence
Persistent kernel state touched here is PSP device config, device generation, per-device stats, active association lists indirectly through `psp_assoc_create()`/socket setters, and per-socket PSP association pointers. There is no disk persistence. Lifetime is governed by device mutexes, socket references from `sockfd_lookup()`, PSP device references, and association refcounts.

## Dependencies And Integration Points
This file integrates with generic netlink, xarray device registration, TCP sockets, PSP driver callbacks (`set_config`, `key_rotate`, `rx_spi_alloc`, stats), and PSP socket helpers in `psp_sock.c`. Notifications use `genlmsg_multicast_netns()` for management and use groups.

## Risks
The file is lock-order sensitive: global device lock precedes per-device lock, and association commands keep socket references until post-op unlock. Key material is copied from netlink attributes and returned in netlink responses, so validation of key size and SPI is critical. `psp_nl_reply_send()` assumes a single message per skb. Version checks use `1 << version`, so callers must keep version values in a sane range through policy/ABI. Errors during RX setup must release both the temporary association and reply skb correctly.

## Test Signals
Useful coverage includes netlink policy rejection for missing attributes, unsupported versions, key length/SPI validation, device id/socket mismatch, non-TCP socket fds, set-config no-op versus changed config, key-rotation notifications, dump filtering by namespace access, and stats behavior when driver leaves required counters unset.
