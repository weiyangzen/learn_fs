# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.c

## Purpose

This file implements the dynamic configuration interface for NXP SJA1105/SJA1110 Ethernet switches. Static configuration tables are normally uploaded as an all-at-once switch image, but several tables expose a register-like dynamic view that can be read, written, searched, or invalidated without resetting the switch. The file builds a per-family `struct sja1105_dynamic_table_ops` table and exposes the common runtime APIs `sja1105_dynamic_config_read()` and `sja1105_dynamic_config_write()`.

The driver treats a dynamic transaction as a packed compound buffer: an entry area followed by a 32-bit command area. Different switch generations put fields in different places, sometimes overlapping command and entry data. This file centralizes those packing quirks so higher-level paths in `sja1105_main.c`, `sja1105_ptp.c`, flower offload, VLAN, FDB, mirroring, CBS, and management-route TX can operate in terms of normal C table entries.

## Important APIs, Types, and Data

- `struct sja1105_dyn_cmd` is the internal command model. It carries `valid`, `rdwrset`, `errors`, `valident`, `index`, and the software-only `search` flag used to select HOSTCMD search behavior on P/Q/R/S/SJA1110.
- `enum sja1105_hostcmd` maps the generic read/write/delete/search model into the second/third-generation L2 lookup HOSTCMD field.
- `sja1105et_dyn_ops`, `sja1105pqrs_dyn_ops`, and `sja1110_dyn_ops` are the exported operation tables indexed by `enum sja1105_blk_idx`. Each row defines command packing, entry packing, access flags, entry limit, packed size, and base SPI address for one dynamic block.
- `sja1105_dynamic_config_read()` validates the block/index/access mode, packs a read or search command, optionally packs the search key into the entry buffer, writes the command via SPI, waits for completion, and unpacks the resulting entry.
- `sja1105_dynamic_config_write()` validates write/delete support, packs a write or invalidate command, optionally packs the entry, writes it via SPI, and polls for completion/error status.
- `sja1105et_fdb_hash()` implements the first-generation FDB bin hash over VID and MAC address using the configured L2 lookup polynomial.

The command/entry packers cover virtual link lookup/policing, L2 lookup and management routes, VLAN lookup, L2 forwarding, MAC configuration, L2 lookup/general/AVB parameters, retagging, CBS, SJA1110 xMII params, L2 policing, and L2 forwarding params.

## Control Flow

The common read path checks `blk_idx`, `ops->max_entry_count`, `OP_SEARCH`, `OP_READ`, buffer size, and packing callbacks. It sets `cmd.valid`, `cmd.rdwrset = SPI_READ`, chooses either a numeric index or search command, sets `cmd.valident`, packs the command, and packs the entry only for searches. It holds `priv->dynamic_config_lock` around the SPI command and completion poll. Completion polling reads back the same dynamic buffer, unpacks the command, waits until hardware clears VALID, checks VALIDENT unless `OP_VALID_ANYWAY` is set, and unpacks the entry if requested.

The write path is similar but requires `OP_WRITE`, rejects negative indexes, and requires `OP_DEL` when `keep == false`. It sets `cmd.valident = keep`, packs the command before packing the entry, and skips entry packing for pure invalidation. Completion checks hardware error bits but does not require VALIDENT.

Several packers deliberately violate a clean command/entry split because the hardware layout does. L2 lookup indexes are physically stored in entry fields on some generations, VLAN indexes are the VLAN ID field, SJA1110 VLAN validity is inferred from `TYPE_ENTRY`, and `lockeds` is read from command writeback but belongs semantically to the FDB entry. Management route packers reuse L2 lookup command layouts while forcing the management-route bit.

## State and Persistence Behavior

Dynamic writes immediately modify switch hardware and are also generally made against entries stored in `priv->static_config` by callers. That dual update is essential because `sja1105_static_config_reload()` resets and reuploads the static image, so runtime FDB/VLAN/MAC/CBS/flooding/mirroring state must be replayable from software. This file itself does not persist state beyond the stack transaction buffer; it enforces serialized hardware access through `priv->dynamic_config_lock`.

`sja1105et_fdb_hash()` depends on the current static L2 lookup params table, so changes to the polynomial affect the bin selected for first-generation FDB operations.

## Dependencies and Integration Points

The implementation depends on `sja1105_packing()`, `sja1105_pack()`, and `sja1105_unpack()` from the local packing infrastructure, static table entry packers from `sja1105_static_config.c`, SPI transfer helpers from `sja1105_spi.c`, Linux `read_poll_timeout()`, and `priv->info->dyn_ops` selected in `sja1105_spi.c` chip info tables. The exported dynamic ops arrays are referenced by `struct sja1105_info`.

Important consumers include FDB add/delete/dump and fast-age, VLAN add/delete, bridge forwarding/flood changes, MAC speed/STP/PVID/drop settings, CBS offload, mirror config, management routes for control-packet TX, PTP AVB parameter changes, and SJA1110 dynamic table operations.

## Risks and Edge Cases

- The hardware layouts are generation-specific and sometimes contradictory; the packers contain several intentional hacks. A bitfield mistake can silently corrupt hardware table entries.
- `SJA1105_MAX_DYN_CMD_SIZE` must remain large enough for all `packed_size` values; both public paths reject oversized ops, but adding new tables requires care.
- Some operations report missing entries via VALIDENT while others legitimately lack it and require `OP_VALID_ANYWAY`; wrong access flags can turn valid reads into `-ENOENT` or hide missing entries.
- Search is only supported where `OP_SEARCH` is set; callers using `SJA1105_SEARCH` with unsupported tables receive `-EOPNOTSUPP`.
- Dynamic transactions are serialized only by `dynamic_config_lock`; callers that also mutate `priv->static_config` need their own higher-level locks such as `fdb_lock` or `mgmt_lock`.
- First-generation FDB bin handling relies on the configured CRC polynomial and four-way bin semantics, so changing L2 lookup params can alter FDB placement.

## Test Signals

Useful validation signals include successful probe/static upload followed by dynamic VLAN/FDB/bridge operations, `bridge fdb show` traversing entries without SPI errors, `bridge vlan` add/delete reflecting in traffic behavior, CBS/mirror/tc-flower offloads returning success and affecting forwarding, management-route control packets leaving expected ports, and absence of `-EAGAIN` timeout, `-EINVAL` hardware error, or `-ENOENT` surprises during dynamic reads. Tests should cover E/T, P/Q/R/S, and SJA1110 because command packing and access flags differ materially.
