# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool.c

## Purpose
Defines Siena `struct ethtool_ops` and implements operations that are local to the concrete ops table: LED identify, register dumps, coalescing, ring sizing, WOL, FEC stats, and timestamp info.

## Important APIs and functions
`efx_siena_ethtool_ops` is assigned to registered netdevs. Helpers implement `phys_id`, register length/dump, get/set coalesce, get/set ring parameters, get/set WOL, get FEC stats, and get timestamp info.

## Control flow
Coalescing reads current IRQ moderation, accepts standard and legacy IRQ fields, validates through common IRQ moderation code, then pushes settings to all channels. Ring resizing validates limits and calls channel reallocation. The ops table delegates shared stats, tests, link, RSS, filters, reset, FEC params, and module EEPROM to `ethtool_common.c`.

## State and persistence behavior
Changes IRQ moderation, RX/TX queue sizes, WOL options through NIC callbacks, and LED state during identify. No disk persistence.

## Dependencies
Depends on Linux ethtool, NIC register helpers, MCDI LED, PTP timestamp info, channel reallocation, IRQ moderation, TX descriptor sizing, and NIC callbacks for WOL/FEC.

## Risks
Shared-channel coalescing means RX and TX moderation may be forced equal. Ring resize disrupts datapath and depends on safe channel rollback. Register dump format is revision-specific.

## Test signals
Run ethtool `-c/-C`, `-g/-G`, `-d`, `-p`, WOL, FEC stats, timestamp info, and ring resizing under traffic and XDP.
