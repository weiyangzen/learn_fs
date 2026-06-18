# sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.h

## Purpose
`mptsas.h` defines the private SAS topology, event, and mapping structures shared by the Fusion MPT SAS driver implementation. It is not a broad public API header; its types model firmware events, SAS physical topology, OS/firmware target mapping, and enclosure information used by `mptsas.c`.

## Important APIs, types, and functions
- `struct mptsas_target_reset_event` stores queued target-reset work for SAS device removal, including firmware event data, whether a reset was issued, and timing.
- `enum mptsas_hotplug_action` is the normalized action set used by `mptsas_hotplug_work()`: add/delete end device, add/delete RAID volume, add/delete/reprobe hidden physical disks, add inactive volumes, or ignore.
- `struct mptsas_mapping` records an `(id, channel)` pair for either OS-visible mapping or firmware mapping.
- `struct mptsas_device_info` tracks a discovered SAS device across OS and firmware mappings, SAS address, device flags, enclosure/slot metadata, logical volume state, hidden RAID component state, volume ownership, and cached-removal state.
- `struct mptsas_hotplug_event` is the work item payload used after raw firmware event decoding. It carries adapter, normalized event type, SAS address, bus/target IDs, device information, handle, phy ID, physical disk number, and optional `scsi_device`.
- `struct fw_event_work` embeds delayed work and flexible event payload storage for process-context firmware event handling.
- `struct mptsas_discovery_event` is a small work item for discovery/rescan style operations.
- `struct mptsas_devinfo` mirrors SAS Device Page 0 fields in CPU-endian driver form.
- `struct mptsas_portinfo_details`, `struct mptsas_phyinfo`, and `struct mptsas_portinfo` model wide/narrow SAS port groupings and link firmware data, plus kernel transport objects (`sas_phy`, `sas_port`, `sas_rphy`, `scsi_target`).
- `struct mptsas_enclosure` mirrors SAS Enclosure Page 0 fields.

## Control flow
The header supports a control flow where firmware config pages are read into `mptsas_devinfo`, `mptsas_phyinfo`, `mptsas_portinfo`, and `mptsas_enclosure`, then converted into SAS transport `identify`, phy, port, rphy, and SCSI target objects. Firmware notifications are copied into `fw_event_work`, normalized into `mptsas_hotplug_event`, and then consumed by SAS hotplug logic.

## State and persistence behavior
These structures are in-memory state only. They preserve the relationship between firmware identifiers and OS-visible SCSI topology during a driver lifetime. `mptsas_device_info::is_cached` lets the driver remember removed OS devices long enough to translate later firmware events safely. Logical volume and hidden RAID fields let the SAS driver hide or expose physical disks depending on integrated RAID state.

## Dependencies and integration points
The header assumes surrounding Fusion MPT and kernel SCSI/SAS definitions are already available: `MPT_ADAPTER`, `MPT_SCSI_HOST`, `EVENT_DATA_SAS_DEVICE_STATUS_CHANGE`, `list_head`, `delayed_work`, `work_struct`, `scsi_device`, `scsi_target`, `sas_phy`, `sas_port`, and `sas_rphy`.

## Risks and edge cases
- The structures contain raw pointers to transport and SCSI midlayer objects; lifetime rules are enforced in `mptsas.c`, not encoded in the types.
- `mptsas_portinfo_details::phy_bitmask` is a 64-bit mask with a comment noting limited support for larger phy counts.
- OS and firmware mappings can diverge during hotplug, RAID reconfiguration, and target deletion. Consumers must know whether they need `os` or `fw` mapping.
- Flexible event payloads in `fw_event_work` require callers to allocate the exact event-data size.

## Test signals
- Compile coverage should catch type drift against kernel SCSI/SAS and Fusion MPT headers.
- Runtime tests should validate that target reset queue entries, hotplug payloads, device mapping entries, and topology structs are allocated, linked, unlinked, and freed without leaks during add/remove/reset flows.
- RAID tests should verify `is_logical_volume`, `is_hidden_raid_component`, `volume_id`, and `is_cached` transitions.
