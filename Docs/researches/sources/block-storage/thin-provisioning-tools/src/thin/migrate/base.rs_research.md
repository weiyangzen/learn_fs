# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/base.rs

This file implements thin-device migration orchestration: opening source/destination devices, generating copy streams, and copying mapped regions.

Key elements:
- `DEFAULT_BUFFER_SIZE` is 131,072 sectors, documented as 64 MiB.
- `SourceArgs` carries source path and optional delta ID.
- `DestArgs` distinguishes destination block device versus file.
- `ThinMigrateOptions` carries source, destination, zeroing flag, buffer size, and report.
- `open_source()`:
  - opens the thin source read-only with `O_DIRECT`
  - resolves it to a device-mapper name
  - reads thin and pool tables
  - resolves pool metadata device path
  - requires the thin device to be read-only
  - creates a `ThinStream` from the metadata snapshot and thin ID
- `open_dest_dev()` opens destination block device with `O_EXCL | O_DIRECT`, verifies it is a block device, and checks size.
- `open_dest_file()` creates/truncates a regular file to expected size or checks block-device size.
- `copy_regions()` creates vectored block I/O, a `SyncCopier`, `CopyOpBatcher`, threaded copier, and progress reporter. It turns stream `Copy` chunks into same-offset copy operations.
- `migrate()` wires the scanner, source, destination, buffer size, and copy loop.

Interactions:
- Uses `devices.rs` to inspect device-mapper topology.
- Uses `stream.rs` for copy/skip chunks.
- Uses copier infrastructure for batched threaded copying.

Risks and notes:
- `zero_dest` is present in options but unused in this file.
- `SourceArgs.delta_id` is present but not used; `Discard` chunks are still `todo!()`.
- Source must be a read-only thin device; this protects consistency during migration.
