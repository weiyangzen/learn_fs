# File Research: sources/block-storage/lvm2/lib/device/nvme.c

## Purpose
Implements optional libnvme support for reading NVMe namespace identifiers and persistent reservation information. When `NVME_SUPPORT` is absent, it provides no-op/failing stubs with the same public API.

## Main Responsibilities
- Reads NVMe namespace IDs and identify data from an opened block device.
- Extracts NGUID, EUI64, and UUID identifiers and stores them as LVM `dev_wwid` entries with standard prefixes.
- Reads namespace descriptor lists for NVMe 1.3+ controllers to collect additional identifiers.
- Translates NVMe reservation types to LVM persistent-reservation types.
- Reads reservation reports to identify reservation type and, where applicable, holder key.
- Searches registered reservation keys by exact key, host-id suffix, or returns all keys/counts.

## Important Control Flow
`dev_read_nvme_wwids` marks `DEV_ADDED_NVME_WWIDS`, opens `dev_name(dev)`, gets the NSID, reads namespace identify data, saves nonzero NGUID/EUI64, checks controller version before descriptor reads, then walks `NVME_IDENTIFY_DATA_SIZE` descriptor data by descriptor length. Identifiers are formatted as `uuid.<uuid>`, `eui.<32 hex>` for NGUID, or `eui.<16 hex>` for EUI64.

Reservation readers allocate an 8192-byte report buffer, call `nvme_resv_report` with extended data status, clamp reported registration count to buffer capacity, and then inspect registered keys and holder status.

## Dependencies
Depends on `device.h`, `device_id.h`, persistent reservation definitions from `persist.h`, endian helpers, aligned allocation, and optional `<libnvme.h>`.

## Risk Notes
- Identifier formatting is part of device-ID matching compatibility; changes can invalidate existing `system.devices` entries.
- Descriptor iteration trusts `cur->nidl` for progress after each descriptor; invalid device/kernel data must not cause infinite loops.
- Reservation report parsing uses a fixed-size buffer for up to 127 keys and clamps excessive registration counts.
- Stub builds silently provide no NVMe WWID enrichment and no reservation support.
