# Group Research: group_824_linux_sources_os_linux_linux_fs_proc_vmcore_c_sources_os_linux_linux_ad213f84830d

Scope: `Docs/research_subset_a.md` / selected `sources/os/linux/linux/fs/{proc,pstore,qnx4,qnx6,quota}` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/vmcore.c -->
# File Research: sources/os/linux/linux/fs/proc/vmcore.c

## Role

Implements `/proc/vmcore`, the crash-dump file exposing the previous kernel's memory as an ELF core image to crash dump tools. It parses the crash kernel's ELF core header, normalizes PT_NOTE records, maps PT_LOAD memory ranges into the synthetic vmcore file, supports read and mmap access, and allows optional device dump/device RAM extensions.

## Key Mechanisms

- Maintains `vmcore_list`, a list of old-memory physical ranges with synthetic file offsets.
- Reads old memory through `read_from_oldmem()`, using `copy_oldmem_page()` or encrypted oldmem copies when needed.
- Uses SRCU-protected `vmcore_cb_list` callbacks so drivers can:
  - mark PFNs as non-RAM via `pfn_is_ram`;
  - contribute device RAM ranges when `CONFIG_PROC_VMCORE_DEVICE_RAM` is enabled.
- Exposes weak architecture hooks:
  - `elfcorehdr_alloc/free/read/read_notes`;
  - `remap_oldmem_pfn_range`;
  - `copy_oldmem_page_encrypted`.
- Supports `read_iter`, `llseek`, `open`, `release`, and MMU-only `mmap` proc operations.
- For sparse/non-RAM PFNs, reads return zeroes and mmap remaps zero pages through `remap_oldmem_pfn_checked()`.

## ELF Header Processing

- `parse_crash_elf_headers()` detects ELF32 vs ELF64 and dispatches to format-specific parsers.
- ELF sanity checks validate core type, architecture, class, version, header sizes, and program-header count.
- Multiple PT_NOTE program headers are merged into one:
  - actual note sizes are discovered by walking note headers until a zero `n_namesz`;
  - notes are copied into a vmalloc-backed buffer;
  - extra PT_NOTE program headers are removed from the exported ELF header.
- PT_LOAD entries are converted from old physical offsets to offsets in the synthetic `/proc/vmcore` file.
- `vmcore_size` is computed from adjusted ELF headers, note segment, optional device dumps, and all load ranges.

## Device Dump Support

When `CONFIG_PROC_VMCORE_DEVICE_DUMP` is enabled:

- `vmcore_add_device_dump()` validates a `vmcoredd_data` request, allocates a page-aligned buffer, writes a `NT_VMCOREDD` note header, invokes the driver's dump callback, appends the dump to `vmcoredd_list`, and updates exported ELF note/program-header sizes.
- Device dumps are placed before normal ELF notes in the exported note segment to avoid zero-filled gaps being interpreted as notes.
- Dump addition is rejected once `/proc/vmcore` is open.

## Device RAM Support

When `CONFIG_PROC_VMCORE_DEVICE_RAM` is enabled:

- callback-provided RAM ranges are converted into additional ELF64 PT_LOAD entries;
- the ELF core header buffer may be reallocated to fit new program headers;
- offsets are reset across PT_NOTE and PT_LOAD entries;
- ranges already overlapping known vmcore memory are discarded.

## Synchronization and Lifetime

- `vmcore_mutex` guards open counts, callback registration side effects, and device dump mutation.
- SRCU protects callback traversal during oldmem reads and mmap PFN validation.
- `vmcore_opened` warns about late callback or device dump changes after userspace has observed vmcore.
- `vmcore_cleanup()` removes procfs entry, frees ranges/header/note buffers, and releases device dumps.

## Research Notes

This file is the crash-dump export bridge between architecture-specific oldmem access, procfs, and ELF consumers. The security-sensitive paths are old-memory reads/mmap, sparse PFN zeroing, ELF note bounds checks, and preventing mutation of the exported file layout while userspace may be reading it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/vmcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc_namespace.c -->
# File Research: sources/os/linux/linux/fs/proc_namespace.c

## Role

Implements `/proc/<pid>/mounts`, `/proc/<pid>/mountinfo`, and `/proc/<pid>/mountstats`. It is procfs-facing code that depends closely on mount namespace internals.

## Key Functions

- `mounts_open_common()` obtains the target task, pins its mount namespace and fs root, opens a private seq file, and stores a `proc_mounts` context.
- `mounts_release()` drops the pinned root path and mount namespace.
- `show_vfsmnt()` emits traditional `/proc/mounts` lines.
- `show_mountinfo()` emits mountinfo records including mount IDs, parent IDs, root path, mount path, propagation tags, filesystem type, source, and options.
- `show_vfsstat()` emits mountstats records and delegates optional filesystem stats to `sb->s_op->show_stats`.
- `mounts_poll()` reports namespace event changes through poll using `ns->event`.

## Option Formatting

- `show_sb_opts()` prints superblock options such as `sync`, `dirsync`, `mand`, and `lazytime`, then delegates to LSM `security_sb_show_options()`.
- `show_vfsmnt_opts()` prints mount flags such as `nosuid`, `nodev`, `noexec`, `noatime`, `relatime`, `nosymfollow`, and `idmapped`.
- `mangle()` escapes whitespace, backslash, and `#` for proc output.
- `show_type()` prints filesystem type plus optional subtype.

## Exported Operations

- `proc_mounts_operations`
- `proc_mountinfo_operations`
- `proc_mountstats_operations`

All use seq reads and shared open/release helpers; mounts and mountinfo also support poll.

## Research Notes

The file is careful to present paths relative to the target task's root, returning `SEQ_SKIP` for mountpoints outside a chroot. It snapshots namespace/root references during open so iteration remains stable across task changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc_namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/Kconfig -->
# File Research: sources/os/linux/linux/fs/pstore/Kconfig

## Role

Defines configuration options for the Linux persistent storage subsystem and its RAM/block frontends.

## Options

- `PSTORE`: core persistent store filesystem and platform backend support.
- `PSTORE_DEFAULT_KMSG_BYTES`: default kernel log snapshot size.
- `PSTORE_COMPRESS`: zlib deflate compression for dmesg records.
- `PSTORE_CONSOLE`: persistent console logging.
- `PSTORE_PMSG`: `/dev/pmsg0` userspace persistent message logging.
- `PSTORE_FTRACE`: persistent ftrace function-call tracing.
- `PSTORE_RAM`: ramoops RAM backend with Reed-Solomon ECC support.
- `PSTORE_ZONE`: common zone manager used by pstore/blk.
- `PSTORE_BLK`: block-device-backed pstore.
- `PSTORE_BLK_BLKDEV`: block device selector string.
- `PSTORE_BLK_KMSG_SIZE`, `PSTORE_BLK_MAX_REASON`, `PSTORE_BLK_PMSG_SIZE`, `PSTORE_BLK_CONSOLE_SIZE`, `PSTORE_BLK_FTRACE_SIZE`: block backend sizing and kmsg reason limits.

## Research Notes

The configuration separates frontends from backends. `PSTORE` supplies the common filesystem/platform layer, while RAM and block storage select the lower-level support they require.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/Makefile -->
# File Research: sources/os/linux/linux/fs/pstore/Makefile

## Role

Build rules for the pstore subsystem.

## Contents

- Builds `pstore.o` from `inode.o` and `platform.o` under `CONFIG_PSTORE`.
- Adds `ftrace.o` and `pmsg.o` conditionally for their frontends.
- Builds `ramoops.o` from `ram.o` and `ram_core.o`.
- Builds `pstore_zone.o` from `zone.o`.
- Builds `pstore_blk.o` from `blk.o`.

## Research Notes

The Makefile mirrors the architectural split: common pstore core, optional frontends, RAM backend, zone manager, and block backend.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/blk.c -->
# File Research: sources/os/linux/linux/fs/pstore/blk.c

## Role

Implements the pstore block backend wrapper. It translates module/Kconfig sizing parameters into a `pstore_zone_info`, optionally opens a generic block device in best-effort mode, and registers the zone backend.

## Key Behavior

- Module parameters configure kmsg, pmsg, console, ftrace sizes, max kmsg reason, best-effort mode, and block device path.
- `__register_pstore_device()` validates a `pstore_device_info`, applies module parameter sizes, fills zone owner/name/max reason, and calls `register_pstore_zone()`.
- `register_pstore_device()` and `unregister_pstore_device()` export non-block device registration APIs under `pstore_blk_lock`.
- Best-effort block mode opens the configured block device with `O_RDWR | O_DSYNC | O_NOATIME | O_EXCL`, derives total size from `bdev_nr_bytes()`, and uses `kernel_read()`/`kernel_write()` callbacks.
- `psblk_generic_blk_write()` rejects interrupt or IRQ-disabled contexts because generic block writes are not panic-safe.

## Early Boot Handling

For built-in kernels, `early_boot_devpath()` resolves the configured block device using root-device lookup style logic, creates `/dev/pstore-blk`, and uses it before normal device nodes exist.

## Exports

- `register_pstore_device`
- `unregister_pstore_device`
- `pstore_blk_get_config`

## Research Notes

This backend's generic best-effort path is intentionally limited: without a dedicated panic write callback, it cannot safely write from interrupt/panic contexts. The actual persistence layout is delegated to `zone.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/blk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/ftrace.c -->
# File Research: sources/os/linux/linux/fs/pstore/ftrace.c

## Role

Provides the persistent ftrace frontend for pstore. It records function trace records into the active pstore backend and exposes a debugfs knob to enable or disable recording.

## Key Functions

- `pstore_ftrace_call()` is the ftrace callback. It avoids oops recursion, disables local IRQs, encodes IP, parent IP, timestamp, and CPU, then calls `psinfo->write()` with `PSTORE_TYPE_FTRACE`.
- `adjust_ip()` and `decode_ip()` compensate for KASLR when pstore is built in and `PSTORE_CPU_IN_IP` is not used.
- `pstore_set_ftrace_enabled()` registers or unregisters the ftrace ops and updates `record_ftrace`.
- `pstore_register_ftrace()` creates `debugfs/pstore/record_ftrace` and enables initial recording if requested.
- `pstore_unregister_ftrace()` disables tracing and removes debugfs entries.
- `pstore_ftrace_combine_log()` merges two buffers of `pstore_ftrace_record` entries by timestamp.

## Research Notes

The implementation prioritizes trace-path simplicity and low overhead. The timestamp counter is deliberately not atomic: ordering is useful but exactness is less important than avoiding heavy synchronization in ftrace paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/ftrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/inode.c -->
# File Research: sources/os/linux/linux/fs/pstore/inode.c

## Role

Implements the `pstore` filesystem view. It creates a single-instance filesystem under `/sys/fs/pstore`, turns backend records into read-only files, supports unlink-based backend erasure, and handles mount option parsing.

## Filesystem Model

- `records_list` tracks created pstore files and their private records.
- `pstore_sb` tracks the mounted singleton superblock.
- `pstore_private` holds the dentry, record pointer, total visible size, and list linkage.
- Root directory mode is `0750`; record files are regular `0444`.

## Record File Operations

- `pstore_file_open()` uses seq operations for ftrace records and plain buffer reads for other record types.
- `pstore_file_read()` formats ftrace records via seq output; other types use `simple_read_from_buffer()`.
- `pstore_file_llseek()` dispatches to seq or default llseek as appropriate.
- `pstore_ftrace_seq_show()` decodes persistent ftrace records into human-readable CPU/timestamp/IP/function lines.

## Record Creation and Removal

- `pstore_mkfile()` rejects duplicate records for the same type/id/backend, allocates inode/dentry/private state, names files as `<type>-<backend>-<id>[.enc.z]`, sets timestamps, and links into `records_list`.
- `pstore_unlink()` removes the record from the in-memory list, calls backend `erase()` under the backend read mutex, and unlinks the file.
- `pstore_put_backend_records()` removes all files belonging to an unregistering backend.

## Mount Handling

- Parses `kmsg_bytes=<u32>`, historically ignoring unknown/invalid parameters.
- `pstore_reconfigure()` syncs the filesystem and updates global kmsg snapshot size.
- `pstore_fill_super()` initializes simple superblock state and immediately populates records from the active backend.
- `pstore_init_fs()` creates the sysfs mount point and registers the filesystem.

## Research Notes

This file is the pstore user-visible projection layer. Backend record buffers transfer ownership to `pstore_mkfile()` on success and are freed on failure or inode eviction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/internal.h -->
# File Research: sources/os/linux/linux/fs/pstore/internal.h

## Role

Internal pstore header connecting filesystem, platform, ftrace, pmsg, and backend record code.

## Contents

- Declares global `kmsg_bytes` and active backend pointer `psinfo`.
- Provides ftrace frontend prototypes or no-op stubs depending on `CONFIG_PSTORE_FTRACE`.
- Provides pmsg frontend prototypes or no-op stubs depending on `CONFIG_PSTORE_PMSG`.
- Declares core helpers:
  - `pstore_set_kmsg_bytes`
  - `pstore_get_records`
  - `pstore_get_backend_records`
  - `pstore_put_backend_records`
  - `pstore_mkfile`
  - `pstore_record_init`
  - `pstore_init_fs`
  - `pstore_exit_fs`

## Research Notes

The header intentionally keeps optional frontend call sites simple by providing stubs when features are disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/platform.c -->
# File Research: sources/os/linux/linux/fs/pstore/platform.c

## Role

Core pstore platform/backend coordination layer. It owns single-backend registration, kmsg dump capture, optional compression, console/ftrace/pmsg frontend registration, record discovery, and backend unregister cleanup.

## Backend Registration

- `pstore_register()` enforces a single active backend, honors `backend=` selection, validates flags and required `read`/`write`, initializes locks, installs compatibility `write_user` if missing, loads existing records, and registers enabled frontends.
- `pstore_unregister()` unregisters pmsg/ftrace/console/kmsg callbacks, stops timer/work, removes backend files, frees compression buffers, clears `psinfo`, and releases the backend name.
- `pstore_record_init()` zeroes a record, attaches backend pointer, and timestamps it with `ktime_get_real_fast_ns()`.

## Kmsg Dump Capture

- `pstore_dump()` is registered as a `kmsg_dumper`.
- It snapshots up to `kmsg_bytes`, writing one or more `PSTORE_TYPE_DMESG` records with reason/count/part metadata.
- Panic/NMI/emergency paths use try-lock behavior to avoid blocking.
- Only the first backend write error is reported.
- Oops records can schedule delayed filesystem refresh through `pstore_update_ms`.

## Compression

- Supports only zlib deflate or `none`.
- Compression is only for dmesg records.
- `allocate_buf_for_compression()` allocates a worst-case compression buffer and zlib workspace.
- Failed or expanding compression falls back to uncompressed data truncated to backend buffer size.
- `decompress_record()` inflates compressed dmesg records before exposing them through pstorefs, preserving ECC notices.

## Frontends

- Kmsg dump frontend registers through `kmsg_dump_register()`.
- Console frontend writes `PSTORE_TYPE_CONSOLE` records from console callbacks.
- Ftrace and pmsg registration is delegated to optional frontend files.

## Record Discovery

- `pstore_get_backend_records()` opens the backend if needed, repeatedly calls backend `read()`, decompresses records, creates pstorefs files, detects loops with a 65536-record cap, and closes the backend.
- Uses `psi->read_mutex` to serialize backend reads and erase operations.

## Research Notes

This is the subsystem hub. It avoids complex dependencies in crash paths, limits compression choices to zlib/none, and centralizes frontend/backend lifetime ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/platform.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/pmsg.c -->
# File Research: sources/os/linux/linux/fs/pstore/pmsg.c

## Role

Implements the `/dev/pmsg0` userspace persistent message frontend.

## Key Functions

- `write_pmsg()` validates nonzero writes, initializes a `PSTORE_TYPE_PMSG` record, checks userspace access, serializes writes with `pmsg_lock`, and calls backend `write_user()`.
- `pstore_register_pmsg()` registers a dynamic char device major, creates a `pmsg` class, sets device node mode to write-only group/owner style `0220`, and creates `pmsg0`.
- `pstore_unregister_pmsg()` destroys the device, class, and char device.

## Research Notes

The frontend never buffers user data itself when the backend supports `write_user()`. The core platform layer supplies a compatibility implementation for backends without native user-copy support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/pmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/ram.c -->
# File Research: sources/os/linux/linux/fs/pstore/ram.c

## Role

Implements the `ramoops` pstore backend. It partitions a reserved RAM region into persistent RAM zones for dmesg, console, ftrace, and pmsg records, then registers those zones as a pstore backend.

## Configuration

Supports module parameters and device tree/platform data for:

- reserved memory address/name/size;
- memory mapping type;
- dmesg record size;
- console, ftrace, and pmsg sizes;
- max kmsg dump reason;
- deprecated `dump_oops`;
- ECC size;
- flags such as per-CPU ftrace.

## Read Path

- `ramoops_pstore_open()` resets per-type read counters.
- `ramoops_pstore_read()` returns records in order:
  - dmesg zones with valid `====<time>-<C|D>` headers;
  - console zone;
  - pmsg zone;
  - ftrace zone(s), combining per-CPU records when configured.
- Adds ECC status text to exposed records using `persistent_ram_ecc_string()`.

## Write Path

- `ramoops_pstore_write()` handles console, ftrace, and dmesg records.
- Dmesg writes accept only `record->part == 1` to avoid split crash reports across multiple RAM records.
- Before writing a new dmesg record, the target zone is zapped so the header starts at offset zero.
- `ramoops_pstore_write_user()` handles pmsg writes directly from userspace.
- `ramoops_pstore_erase()` frees old copies and zaps the selected zone.

## Zone Initialization

- `ramoops_init_przs()` creates arrays of persistent RAM zones for dmesg and ftrace.
- `ramoops_init_prz()` creates single console or pmsg zones.
- `ramoops_probe()` parses platform data/DT, rounds zone sizes down to powers of two, maps reserved memory, builds pstore frontend flags, allocates dmesg buffer, and registers with pstore.
- `ramoops_remove()` unregisters pstore and frees all zones.

## Device Tree and Dummy Platform Device

- `ramoops_parse_dt()` reads reserved-memory resource and properties such as `record-size`, `console-size`, `ftrace-size`, `pmsg-size`, `ecc-size`, `flags`, and `max-reason`.
- `ramoops_register_dummy()` creates a platform device from module parameters when no DT/platform device exists.

## Research Notes

`ram.c` contains policy and pstore integration; `ram_core.c` contains the persistent circular buffer/ECC mechanics. Ramoops is deliberately read-only from VFS perspective but writes during crash/console/pmsg/ftrace paths into reserved RAM.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/ram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/ram_core.c -->
# File Research: sources/os/linux/linux/fs/pstore/ram_core.c

## Role

Implements persistent RAM zone mechanics for ramoops: circular buffer headers, writes, user writes, old-log preservation, memory mapping, and optional Reed-Solomon ECC.

## Persistent Buffer Format

- `struct persistent_ram_buffer` contains:
  - signature;
  - atomic `start`;
  - atomic `size`;
  - flexible data array.
- `PERSISTENT_RAM_SIG` is XORed with a caller-provided signature to identify valid data.

## Circular Buffer Logic

- `buffer_start_add()` advances the circular start pointer with optional locking.
- `buffer_size_add()` grows valid size up to zone capacity.
- `persistent_ram_write()` and `persistent_ram_write_user()` keep only the newest bytes when input exceeds capacity, handle wraparound, update data/header ECC, and return original count on success.
- `persistent_ram_save_old()` copies existing persistent data into a linear `old_log` buffer, applying ECC correction first.
- `persistent_ram_zap()` resets start and size and refreshes header ECC.

## ECC

- Optional ECC uses Reed-Solomon over data blocks plus a separate header parity area.
- `persistent_ram_init_ecc()` carves parity bytes from the end of the zone, initializes `rs_decoder`, allocates parity workspace, and checks/corrects the header.
- `persistent_ram_ecc_old()` checks old data blocks and records corrected byte / bad block counts.
- `persistent_ram_ecc_string()` formats ECC status text for pstore records.

## Memory Mapping

- `persistent_ram_buffer_map()` chooses `vmap()` for valid RAM PFNs and `ioremap()`/`ioremap_wc()` for I/O memory.
- `persistent_ram_vmap()` handles page-granular mappings and preserves byte offsets.
- `persistent_ram_iomap()` requests the memory region before mapping.
- `persistent_ram_free()` unmaps, releases regions, frees RS state, ECC workspace, old logs, labels, and zone objects.

## Research Notes

This file is the durability primitive for ramoops. It validates existing signatures on boot, copies old data before optional zapping, and keeps ECC metadata inside the same reserved region.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/ram_core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/ram_internal.h -->
# File Research: sources/os/linux/linux/fs/pstore/ram_internal.h

## Role

Private header for the ramoops persistent RAM implementation.

## Key Definitions

- `PRZ_FLAG_NO_LOCK`: disables zone locking for contexts such as per-CPU ftrace where lockless writes are desired.
- `PRZ_FLAG_ZAP_OLD`: marks zones whose recovered contents should be wiped after boot-time copyout.
- `struct persistent_ram_zone`: stores physical/virtual mapping data, label, pstore type, flags, buffer pointer and size, ECC parity/header pointers, Reed-Solomon state, correction counters, ECC config, and saved old log.

## API Surface

Declares persistent RAM lifecycle and operations:

- `persistent_ram_new`
- `persistent_ram_free`
- `persistent_ram_zap`
- `persistent_ram_write`
- `persistent_ram_write_user`
- `persistent_ram_save_old`
- `persistent_ram_old_size`
- `persistent_ram_old`
- `persistent_ram_free_old`
- `persistent_ram_ecc_string`

## Research Notes

The header keeps the raw persistent buffer struct opaque to most ramoops code while exposing the zone state needed by `ram.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/ram_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pstore/zone.c -->
# File Research: sources/os/linux/linux/fs/pstore/zone.c

## Role

Implements the reusable pstore/zone intermediate backend used by pstore/blk-style storage. It manages in-memory zones, flushes them to a contiguous backing store, recovers old records after reboot, and registers a pstore backend.

## Data Model

- `struct psz_buffer`: per-zone on-storage header with signature, data length, circular start offset, and data.
- `struct psz_kmsg_header`: dmesg-specific subheader with magic, timestamp, compression bit, counter, and reason.
- `struct pstore_zone`: one in-memory zone with storage offset, type/name, current buffer, recovered old buffer, size, recovery flag, and dirty flag.
- `struct psz_context`: global singleton with kmsg/pmsg/console/ftrace zones, counters, recovery/panic flags, backend info lock, and embedded `pstore_info`.

## Writes and Flushes

- `psz_zone_write()` updates in-memory data and optionally flushes none/part/meta/all to backend `write` or `panic_write`.
- Dirty zones are marked when writes cannot be flushed, and a delayed cleaner retries later.
- `psz_flush_all_dirty_zones()` retries pmsg, console, kmsg, and ftrace zones.
- Panic state blocks non-dmesg writes and attempts to flush other dirty zones after panic dmesg writes.

## Recovery

- `psz_recovery()` runs once before reads.
- Kmsg recovery first scans metadata to validate headers, find latest write position, and recover oops/panic counters, then reads full data for valid zones.
- Pmsg, console, and ftrace recovery load old circular data into `oldbuf`.
- Recovery avoids damaging old records before storage is known readable.

## Record Operations

- `psz_pstore_open()` resets read counters.
- `psz_pstore_write()` dispatches records by type.
- `psz_pstore_read()` recovers if needed, then returns kmsg, combined ftrace, pmsg, and console records.
- `psz_pstore_erase()` clears kmsg zones by count match or frees old buffers for other record types.
- Ftrace reads combine per-CPU zone logs using `pstore_ftrace_combine_log()`.

## Registration

- `register_pstore_zone()` validates sizes, alignment, total capacity, name, and read/write callbacks; allocates zones; creates pstore dmesg buffer; sets flags; and registers with core pstore.
- `unregister_pstore_zone()` unregisters pstore, flushes dirty zones, frees buffers/zones, clears counters, and resets recovery/panic state.

## Research Notes

This layer turns arbitrary sector-like storage into pstore frontends while preserving crash-path behavior. The implementation is singleton-based, assumes one backend at a time, and treats `panic_write` as the only safe panic-time storage path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pstore/zone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/Kconfig -->
# File Research: sources/os/linux/linux/fs/qnx4/Kconfig

## Role

Kconfig option for QNX4 filesystem support.

## Contents

- `QNX4FS_FS`: tristate read-only QNX4 filesystem driver.
- Depends on `BLOCK`.
- Selects `BUFFER_HEAD`.
- Help text notes use for QNX 4 and QNX 6/QNX RTP disks, module name `qnx4`, and recommends `N` unless needed.

## Research Notes

Although the help mentions QNX6-era systems, this driver itself implements the older QNX4 on-disk format and is read-only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/Makefile -->
# File Research: sources/os/linux/linux/fs/qnx4/Makefile

## Role

Build rules for the QNX4 filesystem driver.

## Contents

- Builds `qnx4.o` under `CONFIG_QNX4FS_FS`.
- Object list: `inode.o`, `dir.o`, `namei.o`, `bitmap.o`.

## Research Notes

The driver is small and split into mount/inode/block mapping, directory iteration, lookup, and free-block counting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/bitmap.c -->
# File Research: sources/os/linux/linux/fs/qnx4/bitmap.c

## Role

Implements free-block counting for QNX4 statfs support.

## Key Function

- `qnx4_count_free_blocks()`:
  - locates the `.bitmap` inode saved in `qnx4_sb(sb)->BitMap`;
  - reads bitmap blocks sequentially;
  - counts zero bits as free blocks using `memweight()`;
  - stops on read error and logs an I/O error.

## Research Notes

The driver is read-only, so bitmap handling is limited to counting free space for `statfs`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/dir.c -->
# File Research: sources/os/linux/linux/fs/qnx4/dir.c

## Role

Implements QNX4 directory iteration and directory inode/file operations.

## Key Function

- `qnx4_readdir()`:
  - walks directory file offsets by QNX4 directory entry size;
  - maps directory logical blocks through `qnx4_block_map()`;
  - reads directory blocks with `sb_bread()`;
  - uses `get_entry_fname()` to skip empty/unused entries;
  - computes inode numbers either directly from block/index or from linked directory entries;
  - emits names with `dir_emit()`.

## Operations

- `qnx4_dir_operations`: generic llseek/read, `iterate_shared`, simple fsync, generic setlease.
- `qnx4_dir_inode_operations`: lookup through `qnx4_lookup`.

## Research Notes

QNX4 directories are arrays of 64-byte records where each record can be a real inode entry or a link entry pointing to the actual inode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/inode.c -->
# File Research: sources/os/linux/linux/fs/qnx4/inode.c

## Role

Main QNX4 filesystem implementation: superblock mount, block mapping, inode loading, statfs, address-space operations, inode cache, and filesystem registration.

## Mount and Superblock

- Always forces `SB_RDONLY`.
- `qnx4_fill_super()` allocates `qnx4_sb_info`, sets 512-byte block size, reads block 1 superblock, checks root directory, locates `.bitmap`, loads root inode, and creates root dentry.
- `qnx4_checkroot()` verifies the root directory name and scans root extents for `.bitmap`.
- `qnx4_kill_sb()` frees copied bitmap inode and private superblock info.

## Block Mapping

- `qnx4_block_map()` maps file logical blocks:
  - first checks the inode's first extent;
  - follows chained extent blocks via `di_xblk`;
  - validates extent block signature `"IamXblk"`;
  - returns physical block numbers adjusted from QNX's 1-based block numbering.
- `qnx4_get_block()` adapts block mapping for buffer/page-cache helpers.

## Inodes

- `qnx4_iget()` reads raw inode entries from inode blocks, converts mode/uid/gid/link count/size/timestamps, copies the raw 64-byte inode entry into private inode state, and installs operations for regular files, directories, or symlinks.
- Regular files use `generic_ro_fops` and qnx4 address-space operations.
- Symlinks use page symlink operations.
- Unexpected inode modes fail with `-EIO`.

## Other Operations

- `qnx4_statfs()` reports block counts from bitmap size and free blocks from bitmap scan.
- `qnx4_read_folio()` and `qnx4_bmap()` use generic block helpers.
- Registers filesystem type `qnx4` and a slab cache for private inode info.

## Research Notes

The driver is intentionally read-only but still performs raw extent-chain parsing. Error handling is mostly conservative: malformed roots, unreadable inodes, invalid extent blocks, or unsupported inode types abort operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/namei.c -->
# File Research: sources/os/linux/linux/fs/qnx4/namei.c

## Role

Implements QNX4 directory lookup.

## Key Functions

- `qnx4_match()` checks one directory entry against a requested name using `get_entry_fname()`.
- `qnx4_find_entry()` scans directory blocks and entries, using `qnx4_block_map()` and `sb_bread()`, and returns the matching buffer plus computed inode number.
- `qnx4_lookup()` resolves link entries to their real inode block/index, loads the inode with `qnx4_iget()`, and returns `d_splice_alias()`.

## Research Notes

The lookup path mirrors readdir's handling of link entries. It does not create or mutate directory entries because the driver is read-only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx4/qnx4.h -->
# File Research: sources/os/linux/linux/fs/qnx4/qnx4.h

## Role

Private QNX4 driver header.

## Key Definitions

- `struct qnx4_sb_info`: stores version and copied bitmap inode entry.
- `struct qnx4_inode_info`: stores raw QNX4 inode entry, `mmu_private`, and embedded VFS inode.
- Helper accessors:
  - `qnx4_sb()`
  - `qnx4_i()`
  - `qnx4_raw_inode()`
- `union qnx4_directory_entry`: overlays inode entries, link entries, and a generic name/status view.

## Directory Entry Helper

- `get_entry_fname()` validates non-empty names and used/link status bits, selects the correct fixed name length for inode vs link entries, applies `strnlen()`, and returns the common name pointer.
- Includes `BUILD_BUG_ON()` checks that status byte offsets match across entry formats.

## Research Notes

The union intentionally uses a synthetic `de_name[48]` to avoid GCC false-positive array-bounds behavior when accessing overlaid QNX4 inode/link name arrays.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx4/qnx4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/Kconfig -->
# File Research: sources/os/linux/linux/fs/qnx6/Kconfig

## Role

Kconfig options for QNX6 filesystem support.

## Contents

- `QNX6FS_FS`: tristate read-only QNX6 filesystem driver.
- Depends on `BLOCK && CRC32`.
- Selects `BUFFER_HEAD`.
- `QNX6FS_DEBUG`: optional extended debug output.

## Research Notes

The driver is explicitly read-only and uses CRC32 superblock validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/Makefile -->
# File Research: sources/os/linux/linux/fs/qnx6/Makefile

## Role

Build rules for the QNX6 filesystem driver.

## Contents

- Builds `qnx6.o` under `CONFIG_QNX6FS_FS`.
- Object list: `inode.o`, `dir.o`, `namei.o`, `super_mmi.o`.
- Adds `-DDEBUG` when `CONFIG_QNX6FS_DEBUG` is enabled.

## Research Notes

The comment still says qnx4 routines, but the object list and target are QNX6-specific.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/dir.c -->
# File Research: sources/os/linux/linux/fs/qnx6/dir.c

## Role

Implements QNX6 directory iteration and name lookup support, including long filename records stored in the filesystem longfile.

## Directory Iteration

- `qnx6_readdir()` walks directory folios and fixed-size directory entries.
- Short names are emitted directly from `de_fname`.
- Long names are detected by `de_size > QNX6_SHORT_NAME_MAX` and resolved through `qnx6_dir_longfilename()`.
- `qnx6_dir_longfilename()` reads the long filename record, validates maximum length, optionally checks checksum, and emits the long name.

## Lookup Helpers

- `qnx6_find_ino()` scans directory pages for a name, starting from cached `i_dir_start_lookup`.
- `qnx6_match()` handles short names.
- `qnx6_long_match()` loads and compares long filename records.
- `qnx6_lfile_checksum()` computes the long filename checksum used by non-MMI filesystems.

## Operations

- `qnx6_dir_operations`: generic llseek/read, `iterate_shared`, simple fsync, generic setlease.
- `qnx6_dir_inode_operations`: lookup through `qnx6_lookup`.

## Research Notes

Long filenames are indirected through a separate private longfile inode. The `mmi_fs` mount option disables checksum enforcement for long names.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/inode.c -->
# File Research: sources/os/linux/linux/fs/qnx6/inode.c

## Role

Main QNX6 filesystem implementation: superblock validation, mount option parsing, block mapping, inode loading, statfs, address-space operations, inode cache, and filesystem registration.

## Mount and Superblock

- Parses `mmi_fs` mount option.
- Always forces read-only mounts.
- Normal QNX6 path:
  - starts with 512-byte superblock reads;
  - tries a bootblock offset first, then offset zero;
  - detects little vs big endian magic;
  - verifies CRC32 checksums for both superblocks;
  - switches block size to on-disk block size;
  - reads the second superblock;
  - chooses the active superblock by serial number.
- MMI path delegates to `qnx6_mmi_fill_super()`.
- Validates inode and longfile tree levels against `QNX6_PTR_MAX_LEVELS`.

## Private Metadata Inodes

- `qnx6_private_inode()` builds internal inodes for the inode table and long filename file from root-node block pointers and tree depth.
- `sbi->inodes` backs inode lookup.
- `sbi->longfile` backs long filename resolution.

## Block Mapping

- `qnx6_block_map()` maps logical file blocks through direct root pointers and optional indirect levels.
- Uses `s_ptrbits = ilog2(blocksize / 4)` to derive pointer fanout.
- Rejects unused block pointers set to all ones.
- `qnx6_get_block()`, `qnx6_read_folio()`, `qnx6_readahead()`, and `qnx6_bmap()` integrate with mpage/generic block helpers.

## Inodes

- `qnx6_iget()` reads inode records from the private inode-table inode, converts endian-aware fields, sets ownership/size/timestamps/block count, stores block pointers/tree depth, and assigns operations for regular files, directories, symlinks, or special inodes.

## Other Operations

- `qnx6_statfs()` reports on-disk block and inode counts.
- `qnx6_checkroot()` verifies that root directory begins with `.` and `..`.
- Registers filesystem type `qnx6` and a slab cache for `qnx6_inode_info`.

## Research Notes

The driver supports endian-flexible QNX6 images and duplicate superblocks. It remains read-only, but its mount path is strict about checksums, tree depth, and root sanity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/namei.c -->
# File Research: sources/os/linux/linux/fs/qnx6/namei.c

## Role

Implements QNX6 dentry lookup.

## Key Function

- `qnx6_lookup()`:
  - rejects names longer than `QNX6_LONG_NAME_MAX`;
  - finds the inode number through `qnx6_find_ino()`;
  - loads the inode with `qnx6_iget()`;
  - returns `d_splice_alias()`.

## Research Notes

All directory scanning and long-name resolution lives in `dir.c`; this file is the VFS lookup wrapper.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/qnx6.h -->
# File Research: sources/os/linux/linux/fs/qnx6/qnx6.h

## Role

Private QNX6 driver header.

## Key Definitions

- Bitwise filesystem integer types `__fs16`, `__fs32`, `__fs64`.
- `struct qnx6_sb_info`: active superblock buffer/pointer, block offset, pointer fanout bits, mount options, endian state, private inode-table inode, and longfile inode.
- `struct qnx6_inode_info`: block pointers, file tree depth, directory lookup hint, and embedded VFS inode.
- Accessors:
  - `QNX6_SB()`
  - `QNX6_I()`

## Endian Helpers

Provides endian-aware conversion helpers:

- `fs64_to_cpu` / `cpu_to_fs64`
- `fs32_to_cpu` / `cpu_to_fs32`
- `fs16_to_cpu` / `cpu_to_fs16`

The selected byte order is stored in `sbi->s_bytesex`.

## API Surface

Declares `qnx6_iget`, `qnx6_lookup`, optional debug superblock printer, directory operations, `qnx6_mmi_fill_super`, and `qnx6_find_ino`.

## Research Notes

Endian abstraction is centralized here, allowing the rest of the QNX6 driver to read normal and big-endian images consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/qnx6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/qnx6/super_mmi.c -->
# File Research: sources/os/linux/linux/fs/qnx6/super_mmi.c

## Role

Handles the QNX6 `mmi_fs` superblock variant.

## Key Functions

- `qnx6_mmi_copy_sb()` copies fields from an MMI superblock layout into the normal `qnx6_super_block` layout, including root nodes for inode, bitmap, and longfile metadata.
- `qnx6_mmi_fill_super()`:
  - reads the first MMI superblock at block 0;
  - validates magic and CRC32 checksum;
  - switches to the on-disk block size;
  - reads the second superblock;
  - validates magic and checksum;
  - chooses the active superblock by serial number;
  - copies the chosen MMI superblock into a normal-layout buffer;
  - sets `sbi->sb_buf`, `sbi->sb`, and `s_blks_off`.

## Research Notes

This adapter lets the main QNX6 mount path consume MMI superblocks as if they were normal QNX6 superblocks after conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/qnx6/super_mmi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/Kconfig -->
# File Research: sources/os/linux/linux/fs/quota/Kconfig

## Role

Defines kernel quota subsystem configuration.

## Options

- `QUOTA`: core disk quota support; selects `QUOTACTL`.
- `QUOTA_NETLINK_INTERFACE`: netlink quota warning delivery.
- `PRINT_QUOTA_WARNING`: obsolete console quota warnings, gated behind `BROKEN`.
- `QUOTA_DEBUG`: additional quota sanity checks.
- `QUOTA_TREE`: generic tree-structured quota file support.
- `QFMT_V1`: old pre-2.4.22 quota format support.
- `QFMT_V2`: vfsv0/vfsv1 quota format support, selecting `QUOTA_TREE`.
- `QUOTACTL`: hidden bool for quota control syscall support.

## Research Notes

The config distinguishes generic quota infrastructure from on-disk quota formats and notification channels. XFS and GFS2 are noted as using their own quota systems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/Makefile -->
# File Research: sources/os/linux/linux/fs/quota/Makefile

## Role

Build rules for the quota subsystem.

## Contents

- `CONFIG_QUOTA`: `dquot.o`
- `CONFIG_QFMT_V1`: `quota_v1.o`
- `CONFIG_QFMT_V2`: `quota_v2.o`
- `CONFIG_QUOTA_TREE`: `quota_tree.o`
- `CONFIG_QUOTACTL`: `quota.o` and `kqid.o`
- `CONFIG_QUOTA_NETLINK_INTERFACE`: `netlink.o`

## Research Notes

The Makefile keeps generic dquot logic, syscall/control logic, format handlers, tree storage, and netlink warnings independently selectable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/compat.h -->
# File Research: sources/os/linux/linux/fs/quota/compat.h

## Role

Defines 32-bit compatibility structures for quota ioctls on compat tasks.

## Structures

- `struct compat_if_dqblk`: compat layout for quota block/inode limits, current usage, timers, and validity mask.
- `struct compat_fs_qfilestat`: compat layout for quota file statistics.
- `struct compat_fs_quota_stat`: compat layout for filesystem quota state, including version, flags, user/group quota file stats, in-core dquot count, time limits, and warning limits.

## Dependencies

Includes `<linux/compat.h>` for fixed compat integer types.

## Research Notes

This header contains ABI layout definitions only. It is consumed by quota ioctl compatibility code outside this grouped file list.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/compat.h -->