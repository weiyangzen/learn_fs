# sources/control-plane/mayastor/io-engine/src/host/blk_device.rs

Purpose: this host module implements block-device discovery for gRPC host APIs. It uses udev and mountinfo to return disks/partitions and decide whether each device is available for pool creation.

Important APIs/types/functions: data structs are `Partition`, `FileSystem`, and `BlockDevice`. `Property` conversion impls safely parse optional udev values into strings and numbers. Availability helpers are `usable_device`, `usable_partition`, and `mayastor_device`. Builders are `new_partition`, `new_filesystem`, and `new_device`. Discovery functions are `get_mounts`, `get_disks`, `get_partitions`, and public async `list_block_devices`.

Control flow: `list_block_devices(all)` reads mountinfo, enumerates udev block devices with `DEVTYPE=disk`, gathers child partitions for each disk, builds a disk record with `include = partitions.is_empty()`, then builds partition records. It returns all records when `all` is true or only records marked available. A device is available when included, nonzero size, not Mayastor-presented, allowed major number, acceptable partition type if partitioned, and no filesystem/mount evidence.

State and persistence: read-only. It reflects current kernel/udev/mount state and does not cache. Size is the raw udev `size` attribute value as exposed by the device.

Dependencies and integration points: depends on `udev`, `devinfo::mountinfo`, Mayastor constants identifying internal devices, and host gRPC conversion code in v0/v1 services.

Risks: allowed major numbers are hardcoded and include broad dynamic ranges; filesystem detection depends on udev properties plus mount source matching; partition type allowlist only accepts Linux GPT/MBR IDs; constructing `Vec::new()` inside `unwrap_or` creates a temporary reference pattern that is safe for the call but easy to alter incorrectly; async function performs blocking udev scans. Test signals should use mocked udev/mount data or integration fixtures for disks with partitions, mounted filesystems, Mayastor devices, rotational/bus fields, and `all` filtering.
