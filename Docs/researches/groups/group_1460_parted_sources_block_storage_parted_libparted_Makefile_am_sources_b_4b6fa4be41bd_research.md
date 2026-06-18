# Group Research: group_1460_parted_sources_block_storage_parted_libparted_Makefile_am_sources_b_4b6fa4be41bd

Scope verified against `Docs/research_subset_a.md`: all researched files are under `sources/block-storage/parted`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/Makefile.am -->
# File Research: sources/block-storage/parted/libparted/Makefile.am

This Automake file defines the build for `libparted.la`, the main libparted shared library.

Key points:
- Conditionally adds the `tests` subdirectory when `HAVE_CHECK` is enabled.
- Selects one architecture backend through `ARCH_SOURCE = arch/$(OS).c`.
- Builds subdirectories in this order: `labels`, `fs`, current directory, and optional tests.
- Main library sources are `debug.c`, `architecture.c`, `architecture.h`, `device.c`, `exception.c`, `filesys.c`, `libparted.c`, `timer.c`, `unit.c`, `disk.c`, `cs/geom.c`, `cs/constraint.c`, `cs/natmath.c`, and the selected architecture source.
- `EXTRA_libparted_la_SOURCES` lists all possible architecture backends: Linux, GNU/Hurd, and BeOS.
- Links filesystem and disk-label sublibraries plus gnulib and optional OS/device-mapper/blkid/uuid/intl libraries.
- Uses libtool version-info `2:5:0`.

Research notes:
- This file is the build-time switchboard that determines which `PedArchitecture` implementation is compiled as the active platform backend.
- `arch/linux.h` is listed as an extra source because it is Linux-backend private support, not a public installed header.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/arch/beos.c -->
# File Research: sources/block-storage/parted/libparted/arch/beos.c

This file implements the libparted architecture backend for BeOS/ZETA/Haiku-style device access.

Core responsibilities:
- Defines `BEOSSpecific`, containing the platform file descriptor used for I/O.
- Recursively scans `/dev/disk` and probes entries named `raw` as whole-disk devices.
- Initializes devices from either BeOS/ZETA ATA metadata, generic block-device geometry, or regular-file disk images.
- Provides the BeOS `PedDeviceArchOps` and `PedDiskArchOps` tables exported through `ped_beos_arch`.

Device initialization:
- `_device_init_ata()` is compiled for ZETA-era APIs and reads ATA identity/geometry through `B_ATA_GET_DEVICE_INFO`.
- `_device_init_generic_blkdev()` uses `B_GET_GEOMETRY` and optionally `B_GET_BIOS_GEOMETRY`.
- `_device_init_file()` treats a regular file as a disk image with default sector size and synthetic `4/32` geometry.
- `beos_new()` allocates `PedDevice`, path, and `BEOSSpecific`, initializes common flags, then delegates to `_device_init()`.

I/O behavior:
- `beos_open()` tries read-write first, falls back to read-only with a warning, and flushes cache.
- `beos_read()` and `beos_write()` use `lseek()` plus `read()`/`write()` loops, retrying or ignoring according to libparted exception responses.
- Writes set `dev->dirty` unless compiled with `READ_ONLY`.
- `beos_check()` reads a range and returns the number of sectors successfully read.
- `beos_sync()` and `beos_sync_fast()` are stubs that return success.

Disk/partition behavior:
- `beos_partition_get_path()` returns `NULL`.
- `beos_partition_is_busy()` returns `0`.
- `beos_disk_commit()` returns `0`, so kernel partition-table commit is effectively unsupported here.

Notable implementation risks:
- `_flush_cache()` checks `if ((fd=open(dev->path, O_RDONLY)) < 0)` before calling `ioctl(fd, B_FLUSH_DRIVE_CACHE)`, which appears inverted because it would call `ioctl` on a negative descriptor.
- Partition path and commit operations are placeholders, so this backend is mainly useful for raw device/file I/O and probing rather than full kernel partition synchronization.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/arch/beos.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/arch/gnu.c -->
# File Research: sources/block-storage/parted/libparted/arch/gnu.c

This file implements the GNU/Hurd architecture backend using Hurd `store` objects.

Core responsibilities:
- Defines `GNUSpecific`, holding a `struct store *` and a `consume` flag indicating whether libparted owns that store.
- Supports both path/type based store opening and direct construction with `ped_device_new_from_store()`.
- Exports `ped_gnu_arch` with GNU/Hurd device and disk operation tables.

Device model:
- Sector size is fixed to `PED_SECTOR_SIZE_DEFAULT`.
- Device length is computed from `store->blocks * store->block_size`.
- Geometry is synthetic: BIOS heads/sectors are set to `255/63`, with cylinders derived from length.
- `init_file()` opens the device, probes geometry, sets `dev->model` to an empty string, and closes the device.

Opening and ownership:
- `gnu_new()` allocates a device and tries to open the store read-write, then read-only.
- `ped_device_new_from_store()` wraps an existing store without registering it in Parted’s global device list and does not consume it.
- `gnu_destroy()` frees the store only when `consume` is set.

I/O behavior:
- `gnu_read()` maps libparted sectors to Hurd store blocks, handles store block sizes larger than 512 bytes, and copies only the requested byte range into the user buffer.
- `gnu_write()` handles unaligned first and last store blocks with read-modify-write and writes aligned middle ranges directly.
- Read/write errors are routed through libparted exceptions with retry/ignore/cancel behavior.
- `gnu_check()` currently returns `count` without actually checking media.
- `gnu_sync()` uses `file_sync()` and remembers one path whose sync failure was ignored to avoid repeating the same prompt.

Partition synchronization:
- `_reread_part_table()` attempts to notify the kernel with `BLKRRPART` for device stores, then removes active parted-based translators for paths like `<dev>sN`.
- `gnu_partition_get_path()` formats partitions as `<device-path>s<num>`.
- `gnu_partition_is_busy()` always returns not busy.
- `gnu_disk_commit()` delegates to `_reread_part_table()`.

Probe behavior:
- `gnu_probe_all()` probes a fixed list of common Hurd disk names: `/dev/sd*`, `/dev/hd*`, `/dev/wd*`, and `/dev/ud*`.

Research notes:
- This backend is store-centric rather than file-descriptor-centric.
- It contains careful handling for store block sizes that differ from libparted’s logical sector size.
- Busy detection is effectively absent, so correctness depends on Hurd store/translator behavior during commit.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/arch/gnu.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/arch/linux.c -->
# File Research: sources/block-storage/parted/libparted/arch/linux.c

This is the main Linux backend for libparted device discovery, geometry probing, I/O, cache flushing, partition naming, mount/busy checks, kernel partition-table synchronization, device-mapper integration, and topology-based alignment.

Major structures and constants:
- Uses `LinuxSpecific` from `arch/linux.h`, storing fd, major/minor, optional device-mapper target type, optional s390 fields, and optional blkid topology handles.
- Defines Linux ioctl constants locally for block size, disk size, flushing, odd last sectors, BLKPG partition operations, and old IDE/SCSI geometry.
- Classifies many block device families by major number: IDE, SCSI, DAC960, Compaq Smart Array, I2O, UBD, DASD, virtio, loop, md, blkext/NVMe, RAM, pmem, device-mapper, and others.

Device classification and initialization:
- `_device_probe_type()` uses `stat()`, `major()`, `minor()`, `/proc/devices`, and optional libdevmapper to assign `dev->type`.
- `linux_new()` allocates `PedDevice` and `LinuxSpecific`, initializes flags, optionally enables device-mapper udev synchronization, probes type, then dispatches to a type-specific initializer.
- `init_ide()` uses `HDIO_GET_IDENTITY` to get the IDE model and warns about multiple logical sectors per physical sector.
- `init_scsi()` uses `SCSI_IOCTL_GET_IDLUN`, sysfs vendor/model files, and fallback SCSI inquiry.
- `init_file()` handles regular files and test sector-size override via `PARTED_SECTOR_SIZE`.
- `init_generic()` is used for most modern or less-specific block devices and probes geometry through ioctl paths.
- `init_nvme()` reads the sysfs `model` field when available.
- s390 builds include DASD-specific initialization and alignment handling.

Geometry and length:
- `_device_set_sector_size()` uses `BLKSSZGET` for logical sector size and optional blkid topology for physical sector size.
- `_device_get_length()` prefers `PARTED_TEST_DEVICE_LENGTH`, then `BLKGETSIZE64`, then legacy `BLKGETSIZE`.
- `_device_probe_geometry()` sets length, BIOS geometry, and hardware geometry. For non-s390, it prefers sector-size ioctl data over old `HDIO_GETGEO`.

Open, close, cache, and sync:
- `_device_open()` tries requested flags, then falls back to read-only with a warning.
- `linux_open()` opens read-write through `_device_open()`.
- `_device_open_ro()` is used during probing and increments `open_count` itself.
- `linux_close()` flushes dirty devices, then `fsync()`s and closes.
- `_flush_cache()` issues `BLKFLSBUF` on the main device and unmounted partition devices. It skips read-only and RAM devices.
- `linux_sync()` performs `fsync()` then full cache flushing; `linux_sync_fast()` only performs `fsync()`.

I/O behavior:
- `linux_read()` and `linux_write()` seek by sector, use sector-aligned buffers from `posix_memalign()`, handle partial reads/writes, and route errors through libparted exceptions.
- Old kernels before 2.6 receive special handling for reading/writing the last sector on odd-sized block devices through `BLKGETLASTSECT`/`BLKSETLASTSECT`.
- `linux_check()` returns the number of readable sectors from a range.

Device discovery:
- `linux_probe_all()` probes standard `/dev/hd[a-h]` and `/dev/sd[a-f]` names, optional device-mapper dmraid devices, then `/sys/block`, falling back to `/proc/partitions`.
- `_probe_sys_block()` skips `dm-`, loop, ram, fd, `.` and `..` entries and converts sysfs `!` back to `/`.
- `_probe_proc_partitions()` uses a heuristic to skip partition entries and probe whole devices.

Partition naming and busy checks:
- `_device_get_part_path()` handles devfs `/disc` to `/partN`, appends `p` when needed for names ending in digits or certain controller types, and canonicalizes device-mapper names via `/dev/mapper`.
- `linux_partition_get_path()` returns the whole device path for `loop` disk labels.
- Mount/busy checks search `/proc/mounts`, `/proc/swaps`, and `/etc/mtab` by device number.
- `linux_is_busy()` checks the whole device and up to 32 partition paths.
- `linux_partition_is_busy()` checks active partitions and recursively checks logical partitions inside extended partitions.

Kernel partition-table synchronization:
- `_disk_sync_part_table()` implements a two-pass sync:
  1. Remove old kernel partition entries.
  2. Add or resize current libparted partitions.
- For regular block devices it uses BLKPG add/remove and optional BLKPG resize.
- For device-mapper devices it creates/removes/reloads linear maps and synchronizes with udev cookies.
- Existing kernel partition start/length is read from sysfs, HDIO geometry, BLKGETSIZE64, or device-mapper tables.
- `linux_disk_commit()` requires BLKPG for non-file devices and calls `_disk_sync_part_table()`.

Alignment:
- With blkid topology enabled, `linux_get_minimum_alignment()` uses topology alignment offset and minimum I/O size or physical sector size.
- `linux_get_optimum_alignment()` prefers Parted’s default 1 MiB alignment when it is compatible with topology I/O sizes, otherwise uses optimal or minimum I/O alignment.
- On s390, DASD-like devices use minimum alignment for optimum alignment.

Notable implementation risks:
- Some fallback ioctl success tests in `_kernel_get_partition_start_and_length()` appear suspicious because ioctl success convention is zero, but the code checks truthy return values in places.
- Several paths depend on old kernel ioctls and legacy geometry behavior, so modern correctness depends mostly on sysfs, blkid topology, and BLKPG/device-mapper paths.
- Device probing and busy checks are heuristic-heavy and intentionally conservative on allocation/path failures.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/arch/linux.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/arch/linux.h -->
# File Research: sources/block-storage/parted/libparted/arch/linux.h

This private Linux backend header defines `LinuxSpecific` and the `LINUX_SPECIFIC(dev)` cast helper.

Contents:
- Optionally includes `<blkid/blkid.h>` when available.
- Defines `LINUX_SPECIFIC(dev)` as a cast of `dev->arch_specific`.
- Declares and defines `struct _LinuxSpecific`.

Fields:
- `fd`: active Linux file descriptor for device I/O.
- `major` and `minor`: kernel device numbers captured from `stat()`.
- `dmtype`: device-mapper target type string.
- On s390/s390x:
  - `real_sector_size`: preserved sector size for DASD handling.
  - `devno`: DASD device number.
- With blkid:
  - `probe`: blkid probe handle.
  - `topology`: blkid topology handle.

Research notes:
- This header is intentionally private to the Linux backend and is listed in `EXTRA_libparted_la_SOURCES`, not installed as part of the public API.
- It carries the state required by Linux-specific probing, topology alignment, and device-mapper handling.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/arch/linux.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/architecture.c -->
# File Research: sources/block-storage/parted/libparted/architecture.c

This file owns the global architecture dispatch pointer used by libparted.

Key behavior:
- Defines `const PedArchitecture* ped_architecture`.
- `ped_set_architecture()` initializes the global pointer exactly once.
- Compile-time platform selection:
  - `linux` selects `ped_linux_arch`.
  - `__BEOS__` selects `ped_beos_arch`.
  - All other builds select `ped_gnu_arch`.

Research notes:
- This is the runtime bridge between common code like `device.c` and the platform-specific operation tables.
- The function is idempotent but not synchronized; initialization assumes libparted setup is serialized.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/architecture.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/architecture.h -->
# File Research: sources/block-storage/parted/libparted/architecture.h

This private internal header defines libparted’s architecture abstraction.

Contents:
- Includes `<parted/disk.h>` for `PedDiskArchOps` and `PedDeviceArchOps`.
- Defines `struct _PedArchitecture` with:
  - `PedDiskArchOps* disk_ops`
  - `PedDeviceArchOps* dev_ops`
- Declares global `ped_architecture`.
- Declares `ped_set_architecture()`.

Research notes:
- The warning comment says this should not be exported to the public API.
- Common libparted code reaches platform functionality only through this two-table abstraction.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/architecture.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/cs/constraint.c -->
# File Research: sources/block-storage/parted/libparted/cs/constraint.c

This file implements libparted’s `PedConstraint` solver, combining geometry ranges with start/end alignment requirements and size bounds.

Core model:
- A constraint has:
  - start alignment
  - end alignment
  - allowed start geometry range
  - allowed end geometry range
  - minimum size
  - maximum size
- The introductory comments connect the implementation to intersection closure and the Chinese Remainder Theorem through the alignment layer in `natmath.c`.

Construction and lifetime:
- `ped_constraint_init()` duplicates alignment and geometry inputs into a preallocated constraint.
- `ped_constraint_new()` allocates and initializes a constraint.
- `ped_constraint_new_from_min_max()` creates a constraint requiring a resulting geometry to contain `min` and fit inside `max`.
- `ped_constraint_new_from_min()` uses the whole device as maximum.
- `ped_constraint_new_from_max()` constrains only containment inside `max`.
- `ped_constraint_duplicate()`, `ped_constraint_done()`, and `ped_constraint_destroy()` manage copies and allocated state.

Intersection:
- `ped_constraint_intersect()` intersects start alignments, end alignments, start ranges, end ranges, and size bounds.
- Any empty alignment/range intersection returns `NULL`, representing no solution.
- The resulting size bounds are `max(min_size)` and `min(max_size)`.

Solving:
- `_constraint_get_canonical_start_range()` computes where starts can lie such that at least one valid end can exist.
- `_constraint_get_nearest_start_soln()` aligns the requested start into that canonical range.
- `_constraint_get_end_range()` computes valid ends for a chosen start.
- `_constraint_get_nearest_end_soln()` aligns the requested end into that valid end range.
- `ped_constraint_solve_nearest()` returns a geometry near a requested geometry and asserts it satisfies the constraint.
- `ped_constraint_solve_max()` asks for the nearest solution to the whole-device geometry.

Validation and helpers:
- `ped_constraint_is_solution()` checks start/end alignment, start/end range membership, and min/max size.
- `ped_constraint_any()` creates a permissive whole-device constraint.
- `ped_constraint_exact()` creates a constraint matching a geometry’s exact start and end using zero-grain alignments.

Research notes:
- `NULL` is used both as “no alignment” in lower layers and “no constraint/no solution” in this solver, so callers must follow the documented conventions carefully.
- This file is central to partition placement and resize decisions above the raw device layer.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/cs/constraint.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/cs/geom.c -->
# File Research: sources/block-storage/parted/libparted/cs/geom.c

This file implements `PedGeometry`, libparted’s representation of a contiguous sector range on a `PedDevice`.

Core invariants:
- `start + length - 1 == end`
- `length > 0`
- `start >= 0`
- `end < dev->length` is documented as an API invariant, though `ped_geometry_set()` itself mainly enforces positive length and nonnegative start.

Construction and mutation:
- `ped_geometry_init()` initializes caller-provided storage.
- `ped_geometry_new()` allocates a geometry.
- `ped_geometry_duplicate()` copies a geometry.
- `ped_geometry_intersect()` returns the shared region between two geometries on the same device.
- `ped_geometry_destroy()` frees an allocated geometry.
- `ped_geometry_set()`, `ped_geometry_set_start()`, and `ped_geometry_set_end()` update range fields.

Predicates:
- `ped_geometry_test_overlap()` checks overlap on the same device.
- `ped_geometry_test_inside()` checks full containment.
- `ped_geometry_test_equal()` checks same device/start/end.
- `ped_geometry_test_sector_inside()` checks sector membership.

I/O wrappers:
- `ped_geometry_read()` reads device sectors relative to the geometry start and rejects reads beyond the geometry end.
- `ped_geometry_read_alloc()` allocates a buffer sized by `count * sector_size`, reads into it, and returns ownership through `buffer`.
- `ped_geometry_write()` writes relative to the geometry start and throws an exception if the write crosses the geometry boundary.
- `ped_geometry_sync()` calls full device sync.
- `ped_geometry_sync_fast()` calls fast device sync.

Checking and mapping:
- `ped_geometry_check()` scans a region for unreadable sectors, using a timer and exception suppression while narrowing failures to granularity-sized reads.
- `ped_geometry_map()` maps a sector from one overlapping geometry’s coordinate system to another.

Research notes:
- This is the thin safety layer between partition/filesystem logic and `ped_device_*` I/O.
- Boundary checks are expressed in geometry-relative offsets, which is critical for filesystem code operating inside a partition region.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/cs/geom.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/cs/natmath.c -->
# File Research: sources/block-storage/parted/libparted/cs/natmath.c

This file implements natural-number and modular arithmetic helpers for libparted alignment constraints.

Core model:
- A `PedAlignment` represents sectors satisfying `sector = offset + X * grain_size`.
- `ped_alignment_any` is offset `0`, grain size `1`.
- `ped_alignment_none` is `NULL`.
- Grain size `0` represents a single exact sector at `offset`.

Arithmetic helpers:
- `abs_mod()` implements mathematically positive modulo for negative values.
- `ped_round_down_to()`, `ped_round_up_to()`, and `ped_round_to_nearest()` round sectors to grain multiples.
- `ped_greatest_common_divisor()` implements Euclid’s algorithm.

Alignment lifecycle:
- `ped_alignment_init()` initializes preallocated storage, normalizing offset modulo grain size when grain size is nonzero.
- `ped_alignment_new()` allocates an alignment.
- `ped_alignment_destroy()` frees it.
- `ped_alignment_duplicate()` copies it.

Intersection:
- `extended_euclid()` computes GCD plus coefficients.
- `ped_alignment_intersect()` computes an alignment satisfying two input congruence constraints.
- The implementation uses the Chinese Remainder Theorem idea:
  - New grain size is the least common multiple.
  - New offset is solved via extended Euclid.
  - Inconsistent constraints return `NULL`.

Alignment operations:
- `_closest_inside_geometry()` adjusts aligned sectors into a geometry range.
- `ped_alignment_align_up()` returns the nearest aligned sector at or after a target, constrained by geometry if supplied.
- `ped_alignment_align_down()` returns the nearest aligned sector at or before a target.
- `ped_alignment_align_nearest()` chooses the closer up/down aligned sector.
- `ped_alignment_is_aligned()` checks both geometry membership and congruence/exact-sector matching.

Research notes:
- This is the mathematical foundation for `constraint.c`; partition start/end placement depends on these congruence operations.
- Exact-sector alignments use `grain_size == 0`, so code must avoid treating zero grain size as a normal modulo divisor.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/cs/natmath.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/debug.c -->
# File Research: sources/block-storage/parted/libparted/debug.c

This file implements debug/assertion support when libparted is compiled with `DEBUG`.

Behavior under `DEBUG`:
- Defines a default debug handler that prints level, source file, line, function, and formatted message to `stderr`.
- `ped_debug()` formats a message into an 8192-byte heap buffer and sends it to the current debug handler.
- `ped_debug_set_handler()` installs a custom handler or restores the default handler for `NULL`.
- `ped_assert()` optionally prints a backtrace when `HAVE_BACKTRACE` is available, throws a `PED_EXCEPTION_BUG`, then aborts.

Behavior without `DEBUG`:
- The entire implementation is excluded by `#ifdef DEBUG`.

Research notes:
- The public-facing macros in headers are expected to call these functions only in debug builds.
- Assertion failure intentionally both reports through libparted’s exception system and terminates with `abort()`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/device.c -->
# File Research: sources/block-storage/parted/libparted/device.c

This file implements libparted’s common `PedDevice` API and delegates platform-specific work through `ped_architecture->dev_ops`.

Global device cache:
- Maintains a process-global linked list `devices`.
- `_device_register()` appends a device to the list.
- `_device_unregister()` removes a device and tolerates repeated unregister calls.
- `ped_device_get_next()` iterates the cached list.
- `ped_device_free_all()` destroys all cached devices.
- `ped_device_cache_remove()` removes a device from the cache without destroying it.

Device lookup and probing:
- `_ped_device_probe()` calls `ped_device_get()` while suppressing uncaught probe exceptions.
- `ped_device_probe_all()` delegates to the active architecture backend.
- `ped_device_get()` canonicalizes paths except `/dev/mapper/` and `/dev/md/`, returns a cached device when present, otherwise calls the architecture `_new` operation and registers the result.

Open/close and external access:
- `ped_device_open()` enforces non-external mode and uses `open` for first open or `refresh_open` for nested opens, incrementing `open_count` on success.
- `ped_device_close()` decrements `open_count` and uses `refresh_close` or final `close`.
- `ped_device_begin_external_access()` marks external mode and closes the backend fd if the device is currently open.
- `ped_device_end_external_access()` clears external mode and reopens the backend if the open count is nonzero.

I/O and sync dispatch:
- `ped_device_read()`, `ped_device_write()`, `ped_device_check()`, `ped_device_sync()`, and `ped_device_sync_fast()` assert the device is open and not in external mode, then delegate to architecture operations.

Constraints and alignment:
- `ped_device_get_constraint()` returns a whole-device constraint without alignment requirements.
- `_ped_device_get_aligned_constraint()` constructs start and end alignment constraints over the whole device.
- `ped_device_get_minimal_aligned_constraint()` uses minimum hardware alignment.
- `ped_device_get_optimal_aligned_constraint()` uses optimal hardware alignment.
- `ped_device_get_minimum_alignment()` asks the architecture backend first, then falls back to `phys_sector_size / sector_size`.
- `ped_device_get_optimum_alignment()` asks the backend first, then falls back to 1 MiB alignment via `PED_DEFAULT_ALIGNMENT / sector_size`.

Research notes:
- This file is the central abstraction boundary: all common libparted users call here, while Linux/GNU/BeOS details live behind `PedDeviceArchOps`.
- The global cache is simple and unsynchronized.
- The path canonicalization exceptions for `/dev/mapper` and `/dev/md` preserve names that tests and Linux device semantics depend on.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/device.c -->