# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_transport.c

## Purpose

`fcoe_transport.c` implements the libfcoe transport registry and shared FCoE helper routines. It maps netdevices to transports, provides module-parameter and sysfs create/destroy/enable/disable entry points, registers the FCoE sysfs bus, and exports helpers for link speeds, LESB, WWN formatting, vport validation, CRC, transmit retry queues, and paged CRC/EOF trailer allocation.

## Important APIs, types, and functions

Exports include `fcoe_transport_attach()`, `fcoe_transport_detach()`, `fcoe_ctlr_create_store()`, `fcoe_ctlr_destroy_store()`, `fcoe_link_speed_update()`, `__fcoe_get_lesb()`, `fcoe_get_lesb()`, `fcoe_ctlr_get_lesb()`, `fcoe_wwn_to_str()`, `fcoe_validate_vport_create()`, `fcoe_get_wwn()`, `fcoe_fc_crc()`, `fcoe_start_io()`, `fcoe_clean_pending_queue()`, `fcoe_check_wait_queue()`, `fcoe_queue_timer()`, and `fcoe_get_paged_crc_eof()`.

## Control flow

Module load registers the netdevice notifier and `fcoe` sysfs bus. FCoE drivers attach transports to `fcoe_transports`; the default transport is kept at the tail. Create paths parse an interface name, get a netdevice, reject duplicates through `fcoe_netdevs`, find a matching transport, call `alloc()` or `create()`, and record the mapping. Destroy and enable/disable paths look up the mapping and call transport callbacks.

Transmit helpers clone skbs to `dev_queue_xmit()` and maintain a retry queue with qfull watermarks and a timer. Link/stat helpers query ethtool speeds and aggregate per-CPU FC stats plus netdevice CRC errors. `fcoe_get_paged_crc_eof()` reuses a per-CPU page for trailer fragments.

## State and persistence behavior

`fcoe_transports` is protected by `ft_mutex`; `fcoe_netdevs` is protected by `fn_mutex`. Per-port retry queue/timer state is owned by `struct fcoe_port`. CRC/EOF page state lives in per-CPU FCoE context. State lasts only for module/runtime lifetime.

## Dependencies and integration points

The file depends on module parameters, netdevice notifiers, ethtool, CRC32, SCSI/libfc/libfcoe structures, and `fcoe_sysfs_setup()`/`teardown()`. Registered `struct fcoe_transport` implementations provide matching and lifecycle callbacks.

## Risks and edge cases

`fcoe_ctlr_create_store()` allocates via `ft->alloc()` before mapping insertion; if mapping allocation fails, this function does not destroy the allocated controller. Legacy parameter destroy removes mapping even if transport destroy fails, unlike sysfs destroy. Retry queue length manipulation is subtle. Interface parsing truncates and strips only trailing newlines.

## Test signals

Test attach/detach order, duplicate create rejection, allocation failure cleanup, parameter versus sysfs destroy failure semantics, netdevice unregister cleanup, interface parsing, link-speed mapping, LESB aggregation, vport WWPN duplicate rejection, CRC over fragmented skbs, retry qfull transitions, and trailer allocation page boundaries.
