# Group Research: group_1654_reactos_sources_windows_reactos_drivers_filesystems_CMakeLists_txt__33cddf7fb1f9

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/CMakeLists.txt

Top-level ReactOS filesystem-driver build aggregator. It contains only `add_subdirectory()` entries and delegates all actual driver definitions to child directories.

Key behavior:
- Adds the Btrfs driver first, followed by CDFS, Ext2, FastFAT, filesystem recognizer, mailslot, MUP, NFS, named pipe, NTFS, UDFS, and VFAT filesystem driver subprojects.
- Has no conditional logic, target declarations, compiler options, or dependency wiring of its own.

Filesystem/build relevance:
- Defines which filesystem drivers are included beneath `drivers/filesystems` in this ReactOS build tree.
- The Btrfs subtree is part of the default filesystem-driver traversal through this file.

Notable risks:
- Build inclusion is all-or-nothing per listed subdirectory; disabling a driver requires editing this list or handling it in the child project.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/CMakeLists.txt

Build definition for the ReactOS Btrfs kernel-mode filesystem driver, derived from WinBtrfs sources.

Key behavior:
- Adds include paths for ReactOS driver headers, ReactOS zlib headers, and the local `inc` directory.
- Defines the vendored Zstandard source list used by Btrfs compression support.
- Builds a `btrfs` kernel-mode driver module with architecture-specific `crc32c.S` and `xor.S` assembly on i386/amd64.
- Links against `rtlver`, `zlib_solo`, `chkstk`, `wdmguid`, `${PSEH_LIB}`, `ntoskrnl`, and `hal`.
- Installs the driver, driver INF, and registry INF into the ReactOS image.

Build invariants:
- `__KERNEL__` is globally defined for this target.
- MSVC warning C4267 is suppressed.
- Zstd is built from in-tree C sources rather than an external target.

Filesystem/build relevance:
- This is the complete ReactOS build recipe for the bundled Btrfs filesystem driver.

Notable risks:
- The target embeds multiple imported components directly, including WinBtrfs-derived code, BLAKE2, zlib integration, and Zstd sources.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/balance.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/balance.c

Implements the WinBtrfs/ReactOS Btrfs balance engine: relocating data and metadata chunks, rewriting extent backreferences, converting allocation profiles, persisting/resuming balance state, pausing/resuming/stopping balance work, and using the same relocation machinery for device removal and shrink flows.

Key entry points:
- `start_balance()` validates a user balance request, checks privilege/state, records options, and starts `balance_thread()`.
- `balance_thread()` selects chunks, optionally changes target profiles, relocates data before metadata/system chunks, handles pause/stop events, persists/removes balance state, trims freed space, and finalizes removal/shrink work.
- `look_for_balance_item()` resumes interrupted on-disk `BALANCE_ITEM` work during mount.
- `query_balance()`, `pause_balance()`, `resume_balance()`, and `stop_balance()` implement control/status helpers.
- `remove_device()` validates RAID/device-count constraints and starts balance in removal mode.

Core mechanics:
- Metadata relocation queues tree blocks, reads old nodes/leaves, allocates new metadata addresses, patches parent/root pointers, updates loaded tree caches, recalculates checksums, writes relocated tree blocks, and recreates metadata extent items.
- Data relocation scans non-tree extents, allocates new data space, copies data in 1 MiB units, moves checksum entries, relocates owning metadata leaves, recreates data extent items, and updates changed extents plus cached file extents.
- Backrefs are extracted from inline and non-inline `TREE_BLOCK_REF`, `SHARED_BLOCK_REF`, `EXTENT_DATA_REF`, and `SHARED_DATA_REF` records, sorted, merged where needed, and reinserted at new physical addresses.
- Balance filters support profile, device id, physical range, virtual range, stripe count, usage percentage, limit, convert, and soft-convert behavior.
- Device removal clears device/dev-stat items, updates superblock totals, removes volume/PnP records, optionally clears on-disk superblocks, and notifies volume-size changes.

Important invariants:
- Tree mutations are protected by `Vcb->tree_lock`; chunk allocation/list work uses `Vcb->chunk_lock` and per-chunk locks.
- Relocation must update both on-disk references and loaded in-memory tree/cache state.
- Extent refcounts and backrefs must move without changing logical ownership.
- Data relocation must preserve checksum coverage and explicitly handle no-checksum runs.
- Rollback lists restore chunk-space accounting on failure; successful paths commit with `do_write()`.

Filesystem relevance:
- This file is central to online Btrfs space rebalancing, allocation-profile conversion, and multi-device maintenance.

Notable risks:
- The code spans extent trees, checksum trees, chunk accounting, cached trees, open FCB extent caches, PnP volume state, and mount-manager integration.
- `start_balance()` appears to assign usage bounds from `stripes_start` / `stripes_end` when validating `BTRFS_BALANCE_OPTS_USAGE`; that is suspicious.
- `should_balance_chunk()` compares `num_stripes < opts->stripes_start || num_stripes < opts->stripes_end`; the second comparison likely intended an upper-bound check.
- Device removal correctness depends on all chunks on the target device being selected and fully relocated before final removal.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/balance.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/blake2-impl.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/blake2-impl.h

Bundled BLAKE2 reference implementation support header used by `blake2b-ref.c`.

Key contents:
- Defines `BLAKE2_INLINE` portably for C89/MSVC/GCC/C99/C++ contexts.
- Forces `NATIVE_LITTLE_ENDIAN`, so 16/32/64-bit load/store helpers use `memcpy()` on this build.
- Provides 48-bit load/store helpers and 32/64-bit rotate-right helpers.
- Defines `BLAKE2_PACKED()` for MSVC and GCC-style compilers.
- Defines BLAKE2b constants and the internal `blake2b_state` plus packed `blake2b_param`.

Important invariants:
- The header assumes little-endian targets.
- `memcpy()` avoids unaligned-access problems for native little-endian loads/stores.
- The packed parameter block layout must remain exact.

Filesystem relevance:
- Supplies low-level primitives and state layout for Btrfs BLAKE2b checksum computation.

Notable risks:
- A big-endian build would be wrong unless `NATIVE_LITTLE_ENDIAN` handling changed.
- This is vendored hash reference code; local changes should be treated cautiously.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/blake2-impl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/blake2b-ref.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/blake2b-ref.c

Bundled reference C implementation of BLAKE2b hashing, exposed as one-shot `blake2b()`.

Key entry points:
- `blake2b()` initializes state, absorbs input, finalizes, and writes the digest.
- `blake2b_init()` builds a default unkeyed parameter block.
- `blake2b_update()` buffers input and compresses full 128-byte blocks.
- `blake2b_final()` marks the last block, pads, compresses, serializes the hash, and copies the requested digest length.
- `blake2b_compress()` implements the 12-round BLAKE2b compression function.

Core mechanics:
- Uses the standard BLAKE2b IV and sigma schedule.
- Maintains a 128-bit byte counter in `S->t`.
- Uses final-block and last-node flags in `S->f`.
- Exposes unkeyed hashing only.

Filesystem relevance:
- Used by Btrfs read/write/flush/calculation paths to verify or compute BLAKE2 checksums for superblocks, tree blocks, and data sectors.

Notable risks:
- The public wrapper ignores update/final return codes, so invalid digest lengths would fail silently.
- Includes `<stdio.h>` despite not needing formatted I/O in this driver context.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/blake2b-ref.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/boot.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/boot.c

Implements Btrfs boot-volume discovery and boot-time device attachment support.

Key entry points:
- `check_system_root()` resolves `\SystemRoot` / `\Device\BootDevice`, parses a Btrfs ARC-style boot UUID, finds the matching PDO, marks or adds the boot device, and parses boot subvolume options.
- `boot_add_device()` calls `AddDevice()`, suppresses pending-device reporting, clears `DOE_START_PENDING`, and notifies mountmgr.
- `get_system_root()` decodes `\ArcName\btrfs(<uuid>)` into global `boot_uuid`.
- `check_boot_options()` reads `SystemStartOptions` and parses hexadecimal `SUBVOL=` into global `boot_subvol`.
- `mountmgr_notification()` sends `IOCTL_MOUNTMGR_VOLUME_ARRIVAL_NOTIFICATION`.

Core mechanics:
- Uses global boot state `boot_uuid` and `boot_subvol`.
- Coordinates with PnP using `pdo_list_lock` and `boot_lock`.
- Handles cases where normal PnP callbacks occur too late for a Btrfs boot volume.
- Toggles the device interface state when an existing mounted device needs boot-partition marking.

Filesystem/boot relevance:
- Enables the Btrfs driver to attach early enough for system boot and carry a requested boot subvolume into mount logic.

Notable risks:
- `mountmgr_notification()` leaks the referenced mount-manager file object if notification-buffer allocation fails.
- `check_boot_options()` writes a trailing NUL into a fixed-size query buffer; the source comment notes the buffer should be verified.
- `SUBVOL=` values are parsed as hexadecimal.
- `get_system_root()` is strict about ARC path format.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/boot.c -->