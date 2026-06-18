# File Research: sources/block-storage/kvdo/vdo/vdo.c

## Purpose
Provides core VDO lifecycle, construction/destruction, thread creation, resize preparation, state persistence, read-only notification, statistics, compression control, flush, status dump, and thread assertion helpers.

## Construction And Destruction
- `vdo_make()` allocates and initializes the VDO object, thread config, work queues, flusher, packer, data VIO pool, I/O submitter, optional bio ack queue, and CPU queue.
- `initialize_vdo()` reads the geometry block, creates thread configuration, allocates compression contexts, registers the device, and transitions admin state to initialized.
- `vdo_make_thread()` creates a work queue for a thread-config thread ID and validates repeated construction type.
- `vdo_destroy()` requires the VDO not be running, tears down sysfs stats, queues, subsystems, registry entries, thread config, compression contexts, instance number, and the VDO object/kobject.

## Configuration And Resize Preparation
- `vdo_prepare_to_modify()` validates a new device config, prepares logical growth, prepares physical growth, and logs backing-device name changes.
- Physical-growth `VDO_PARAMETER_MISMATCH` is mapped to `-EINVAL` for user-facing behavior.
- `vdo_get_backing_device()` and `vdo_get_device_name()` expose underlying block device and dm target name.

## State Persistence
- `vdo_get_state()` and `vdo_set_state()` use memory barriers around atomic state access.
- `record_vdo()` snapshots release version, VDO state, block map, recovery journal, slab depot, and layout into `vdo->states`.
- `vdo_save_components()` encodes component states and saves the superblock at the data-region start.
- `vdo_enable_read_only_entry()` registers a listener that saves `VDO_READ_ONLY_MODE` to disk when read-only mode is entered.

## Runtime Operations
- `vdo_synchronous_flush()` submits a flush bio and waits synchronously.
- `vdo_set_compressing()` synchronously toggles compression on the packer thread and flushes the packer when disabling.
- `vdo_get_compressing()` reads compression state with `READ_ONCE`.
- `vdo_enter_recovery_mode()` transitions to `VDO_RECOVERING` unless already read-only.

## Statistics
- `get_vdo_statistics()` populates `struct vdo_statistics` on the admin thread.
- It combines immutable config, slab depot usage, journal stats, packer stats, block map stats, dedupe stats, atomic error stats, bio stats, VIO pool usage, and memory usage.
- `vdo_fetch_statistics()` runs this synchronously on the admin thread.

## Thread And Zone Helpers
- `vdo_get_callback_thread_id()` identifies the current VDO work queue thread.
- `vdo_assert_on_admin_thread()`, `vdo_assert_on_logical_zone_thread()`, `vdo_assert_on_physical_zone_thread()`, and `assert_on_vdo_cpu_thread()` provide debug assertions.
- `vdo_get_physical_zone()` validates a PBN and maps it to the owning physical zone.
- `vdo_get_bio_zone()` maps PBNs to bio submission zones using rotation interval.

## Important Invariants
- A running VDO must be suspended before destruction.
- All superblock saves should flow through `vdo_save_components()` so component snapshots are consistent.
- Metadata overhead accounting subtracts data blocks and adds block-map journal data blocks.
- Invalid physical PBN checks avoid entering read-only mode in `vdo_get_physical_zone()`.
