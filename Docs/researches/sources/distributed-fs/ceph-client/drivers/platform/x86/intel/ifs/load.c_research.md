<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/load.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/load.c

## Purpose
Loads Intel IFS firmware images, validates Intel microcode-style headers and IFS metadata, copies hashes, and authenticates scan/SBAF chunks into secure package memory.

## Important APIs, Types, And Functions
`find_meta_data()` walks microcode metadata blocks. `image_sanity_check()` validates IFS header type, Intel microcode sanity, and CPU signature match. `validate_ifs_metadata()` checks batch number, test type, chunk alignment, and stride metadata. `scan_chunks_sanity_check()` authenticates chunks per socket for gen0 and through gen2 stride-aware flow when supported. `ifs_load_firmware()` constructs `intel/ifs_<test>/<ff>-<mm>-<ss>-<batch>.<suffix>` and drives the full process.

## Control Flow
Firmware is requested with `request_firmware_direct()`, size is checked against header `totalsize`, metadata and CPU signature are validated, and global pointers are set to header/hash/test data. Gen0 schedules `copy_hashes_authenticate_chunks()` on one online CPU per package and waits for completion. Gen2 optionally copies hashes, invalidates stride, then writes chunk-table pointers to copy/authenticate chunks with retry on authentication-interrupted errors.

## State And Persistence
Global pointers reference the currently requested firmware while it is loaded. `ifs_data` is updated with loaded flag, image version, chunk size, valid chunks, loading error, and SBAF max bundle. Authenticated chunks persist in hardware secure memory until invalidated/reloaded or reset.

## Dependencies And Integration Points
Depends on firmware loader, Intel microcode helpers, CPU topology, MSR writes, completions/workqueues, and `ifs_pkg_auth` from `core.c`.

## Risks And Test Signals
Risks are use of firmware data pointers only while firmware is held, metadata corruption, generation-specific chunk status interpretation, and package authentication races. Test good and bad firmware names, size/signature failures, metadata mismatch, multi-socket loading, gen2 stride invalidation, and expected sysfs `current_batch`/`image_version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/load.c -->
