# File Research: sources/block-storage/libblkid-rs/src/topology.rs

Purpose: Wraps libblkid topology information for a probed device.

Key APIs:
- `get_alignment_offset`
- `get_minimum_io_size`
- `get_optimal_io_size`
- `get_logical_sector_size`
- `get_physical_sector_size`

Implementation notes:
- Thin read-only wrapper around `blkid_topology`.
- No ownership release is implemented, implying the probe owns the topology memory.

Notable risks:
- The type has no lifetime parameter tying it to `BlkidProbe`, even though `probe.rs` documents that topology state is overwritten by later probe calls.
- Methods assume the inner pointer remains valid.
