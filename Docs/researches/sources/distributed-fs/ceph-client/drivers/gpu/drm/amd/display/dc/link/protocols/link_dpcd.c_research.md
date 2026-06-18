# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.c

Purpose: centralizes low-level DPCD read/write access and enforces DisplayPort address partitioning constraints so AUX transactions do not illegally cross mandatory DPCD windows.

Important APIs/functions: exported `core_link_read_dpcd` and `core_link_write_dpcd` wrap `dm_helpers_dp_read_dpcd`/`dm_helpers_dp_write_dpcd`. Internal helpers define DPCD address ranges, detect intersections, compute the next partition size, extend reads that touch mandatory single-transaction blocks, and reduce extended replies back to the caller buffer.

Control flow: reads may be extended when the request intersects mandatory blocks such as LTTPR tunable PHY fields. The extended request is then partitioned into legal chunks, read sequentially, and reduced back to the requested subrange. Writes are partitioned only; they do not use mandatory block extension.

State/persistence: no persistent state. It observes `link->aux_access_disabled`; when AUX access is disabled, internal read/write helpers return `DC_OK` without touching hardware.

Dependencies/integration: includes DRM DP helper definitions, `dm_helpers`, `link_service`, and `dpcd_defs`. Nearly all DP training, eDP panel, and capability code depends on these wrappers.

Risks: the partition table must cover the full DPCD address space without gaps; otherwise `dpcd_get_next_partition_size` can loop forever. `dpcd_reduce_address_range` appears to copy from the caller buffer into the extended buffer before freeing, which is suspicious for reads and should be reviewed if read-extension bugs appear. Allocation failure only asserts.

Test signals: unit/static tests for partition boundaries, reads that span LTTPR/FEC windows, mandatory-block extension, AUX-disabled behavior, and error propagation from `dm_helpers`.
