# File Research: sources/block-storage/kvdo/vdo/dm-vdo-target.c

## Purpose
Defines the Linux Device Mapper target module for VDO transparent deduplication/compression.

## Main Behavior
- `vdo_map_bio()` handles incoming bios, counts them, routes flush/prefllush bios through the flusher, and launches normal bios through the data VIO pool.
- `vdo_io_hints()` sets logical/physical block size, IO size hints, discard limits, and discard granularity.
- `vdo_status()` emits info/status/table/IMA responses.
- `vdo_message()` handles `stats`, `dump`, `dump-on-shutdown`, dedupe index messages, and compression on/off messages.
- `vdo_ctr()` allocates or reuses an instance number, parses table config, modifies existing named VDOs, or initializes a new VDO.
- `vdo_dtr()` detaches a table config and destroys the VDO when the final config reference is removed.
- Suspend/resume hooks coordinate VDO admin states, loading metadata, validating backing size, and resuming operation.
- Module init/exit initializes UDS subsystems, sysfs, registry, status codes, DM target registration, and instance tracking.

## Integration
Connects many subsystems: config parsing, registry, VDO load/resume/suspend, data VIO pool, dedupe controls, io submitter, thread registry, sysfs, stats, and logging.

## Invariants and Risks
- Rejects sharing one backing device with multiple live VDOs.
- Uses target singleton feature.
- Normal bio mapping asserts VDO is in a normal admin state and avoids re-entering from an owned work queue.
- Discard-limit field differs by kernel/RHEL version (`max_discard_sectors` versus `max_hw_discard_sectors`).
