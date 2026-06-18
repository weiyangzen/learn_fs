# File Research: sources/block-storage/libblkid-rs/src/probe.rs

Purpose: Implements the main probing interface over libblkid probe handles.

Key APIs:
- Probe creation and lifecycle: `new`, `new_from_filename`, `reset`, `reset_buffers`
- Device binding and metadata: `set_device`, `get_devno`, `get_wholedisk_devno`, `get_size`, `get_offset`, `get_sector_size`, `get_fd`
- Superblock, topology, and partition probing controls
- Probe execution: `do_probe`, `do_safeprobe`, `do_fullprobe`, `do_wipe`, `step_back`
- Value access: `numof_values`, `get_value`, `lookup_value`, `has_value`
- Global helpers: `is_known_fs_type`, `get_superblock_name`, `is_known_partition_type`, `get_partition_name`

Implementation notes:
- Owns `blkid_probe` and frees it in `Drop`.
- Builds null-terminated C string arrays for type filters.
- Returns borrowed partition/topology structures from libblkid probe state.

Notable risks:
- `get_superblock_name` ignores `get_name` and `get_flags` on return; if either was requested as false, it can still dereference null or convert unrequested flags.
- `get_value` formats `num_values - 1`; when there are zero values this can underflow.
- `get_topology` returns `BlkidTopology` without a lifetime tying it to the probe, allowing a topology handle to outlive the C backing state.
- `has_value` treats any nonzero C return as true, so negative error returns would be hidden if libblkid uses them there.
