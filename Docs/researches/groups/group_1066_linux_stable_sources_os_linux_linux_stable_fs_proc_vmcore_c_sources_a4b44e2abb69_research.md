# Group Research: group_1066_linux_stable_sources_os_linux_linux_stable_fs_proc_vmcore_c_sources_a4b44e2abb69

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/vmcore.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/vmcore.c

## Summary
Implements `/proc/vmcore`, the crash-dump file exposed by the second kernel after kdump. It parses the previous kernel's ELF core headers, normalizes note segments, maps PT_LOAD memory ranges into a synthetic file, supports read and mmap access, and optionally appends device dump notes and device RAM ranges.

## Main Responsibilities
- Maintain `vmcore_list`, a list of physical crash memory ranges and their offsets in the exported vmcore file.
- Read old kernel memory through architecture hooks, honoring encrypted-memory paths and sparse/non-RAM callbacks.
- Merge multiple ELF `PT_NOTE` segments into a single note segment for 32-bit and 64-bit ELF core headers.
- Rewrite `PT_LOAD` program header offsets so the exported file has a contiguous ELF layout.
- Provide `/proc/vmcore` open, read, llseek, release, and mmap operations.
- Register/unregister vmcore callbacks used to filter RAM PFNs or contribute device RAM.
- Optionally append vmcore device dump notes under `CONFIG_PROC_VMCORE_DEVICE_DUMP`.

## Key Interfaces
- `read_from_oldmem()` copies page-aligned slices from the crashed kernel's memory, zeroing pages rejected by `pfn_is_ram()`.
- Weak architecture hooks include `elfcorehdr_alloc()`, `elfcorehdr_free()`, `elfcorehdr_read()`, `elfcorehdr_read_notes()`, `remap_oldmem_pfn_range()`, and `copy_oldmem_page_encrypted()`.
- `read_vmcore()` delegates to `__read_vmcore()` to read ELF headers, merged notes/device dumps, and memory ranges.
- `mmap_vmcore()` maps the vmcore file into userspace when `CONFIG_MMU` is available.
- `register_vmcore_cb()` and `unregister_vmcore_cb()` manage SRCU-protected callback entries.
- `vmcore_add_device_dump()` appends a driver-provided ELF note payload when device dumps are enabled.

## Important Behavior
The file layout starts with copied ELF headers, then the merged note segment, then each aligned crash memory range. During parsing, each original `PT_LOAD` `p_offset` is treated as the source physical address and replaced by the corresponding offset in the exported file.

ELF note handling reads the old kernel's note sections, calculates the real note sizes by walking `Elf{32,64}_Nhdr` entries until a zero name size or a bounds violation, copies note payloads into `elfnotes_buf`, and collapses all `PT_NOTE` headers into one page-aligned `PT_NOTE`.

Device dump notes are inserted before the original notes inside the merged note segment to avoid zero-filled gaps that user tools might misinterpret as valid notes. Adding device dumps rewrites all ELF program headers and updates `proc_vmcore->size`.

The mmap path maps ELF header pages, vmalloc-backed note/device-dump buffers, and oldmem PFNs. If callbacks exist, `remap_oldmem_pfn_checked()` replaces non-RAM pages with the zero page; on s390, the fault handler falls back to page-cache population through `__read_vmcore()`.

## State and Synchronization
`vmcore_mutex` protects open counts, callback registration side effects, and device dump list mutation. Callback traversal uses `DEFINE_STATIC_SRCU(vmcore_cb_srcu)`. `vmcore_opened` records whether userspace has opened `/proc/vmcore`, and `vmcore_open` prevents appending device dumps while the file is open.

## Cross-File Interactions
This file depends on crash-dump declarations in `include/linux/crash_dump.h`, ELF note constants from UAPI ELF headers, architecture-specific oldmem hooks, procfs registration, and optional driver callbacks that identify device RAM or non-RAM PFNs.

## Risks
Correctness depends on preserving ELF offsets after note merging and after optional device dump/device RAM insertion. Callback registration after `/proc/vmcore` has been opened is allowed but warned because the exported file may already be consumed. mmap teardown paths must unmap partially mapped ranges on failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/vmcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc_namespace.c -->
# File Research: sources/os/linux/linux-stable/fs/proc_namespace.c

## Summary
Implements `/proc/<pid>/mounts`, `/proc/<pid>/mountinfo`, and `/proc/<pid>/mountstats`. It opens a target task's mount namespace and root, then renders namespace mount entries using seq_file helpers.

## Main Responsibilities
- Format legacy mount table lines, mountinfo lines, and mount statistics lines.
- Escape mount paths, filesystem names, device names, and option strings for proc output.
- Show superblock options, VFS mount options, idmapped status, propagation tags, and filesystem-specific options/statistics.
- Track mount namespace events for polling on mounts and mountinfo.
- Hold references to the target task's mount namespace and root path while the proc file is open.

## Key Interfaces
- `proc_mounts_operations`, `proc_mountinfo_operations`, and `proc_mountstats_operations` export file operations.
- `show_vfsmnt()` renders `/proc/<pid>/mounts`.
- `show_mountinfo()` renders `/proc/<pid>/mountinfo`.
- `show_vfsstat()` renders `/proc/<pid>/mountstats`.
- `mounts_open_common()` captures the task, mount namespace, and root path shared by all three files.
- `mounts_poll()` reports namespace event changes via `EPOLLERR | EPOLLPRI`.

## Important Behavior
The output is relative to the target task's root. Mountpoints outside that root can cause `seq_path_root()` to return `SEQ_SKIP`, hiding entries from the chrooted view. Mountinfo additionally reports shared/slave/unbindable propagation tags and `propagate_from` when the visible root changes propagation ancestry.

## State and Synchronization
Each open seq_file owns a `struct proc_mounts` with a mount namespace reference, root path reference, and selected show callback. `mounts_release()` drops both references.

## Cross-File Interactions
The file is procfs-adjacent but lives under `fs/` because it relies on namespace internals from `fs/namespace.c`, `pnode.h`, and VFS mount structures.

## Risks
Output correctness depends on escaping fields exactly as proc consumers expect. Polling relies on namespace event counters, so callers should treat `EPOLLPRI` as a signal to reread rather than as a precise change descriptor.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc_namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/pstore/Kconfig

## Summary
Defines Kconfig options for the generic pstore subsystem, pstore frontends, ramoops, pstore zone support, and pstore block backend sizing/configuration.

## Main Responsibilities
- Expose `PSTORE` as the core persistent-store filesystem/framework option.
- Configure default dmesg capture size through `PSTORE_DEFAULT_KMSG_BYTES`.
- Enable optional deflate compression with `PSTORE_COMPRESS`.
- Configure console, pmsg, and ftrace pstore frontends.
- Select dependencies for `PSTORE_RAM`, `PSTORE_ZONE`, and `PSTORE_BLK`.
- Provide pstore/blk defaults for target block device, kmsg size, max reason, pmsg size, console size, and ftrace size.

## Key Interfaces
- `PSTORE` builds the core `pstore.o` code.
- `PSTORE_RAM` builds the `ramoops` backend and selects Reed-Solomon ECC helpers.
- `PSTORE_ZONE` builds the common zone manager used by pstore/blk.
- `PSTORE_BLK` enables persistent storage on block devices and selects `PSTORE_ZONE`.

## Important Behavior
Many pstore/blk sizing options are specified in KB and must be multiples of 4 KB in the runtime validation code. Module parameters can override Kconfig defaults, and the help text explicitly documents that module parameters have priority.

## Cross-File Interactions
The options drive compilation in `fs/pstore/Makefile` and compile-time guards in `platform.c`, `pmsg.c`, `ftrace.c`, `ram.c`, `ram_core.c`, `zone.c`, and `blk.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/pstore/Makefile

## Summary
Build rules for the pstore subsystem and its optional backends/frontends.

## Main Responsibilities
- Build `pstore.o` from `inode.o` and `platform.o` when `CONFIG_PSTORE` is enabled.
- Add `ftrace.o` and `pmsg.o` to `pstore.o` when their frontends are enabled.
- Build `ramoops.o` from `ram.o` and `ram_core.o`.
- Build `pstore_zone.o` from `zone.o`.
- Build `pstore_blk.o` from `blk.o`.

## Cross-File Interactions
The Makefile mirrors Kconfig feature boundaries: `platform.c` and `inode.c` are core; `ram.c`/`ram_core.c` are the RAM backend; `zone.c` is the zone manager; `blk.c` is the block-device backend.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/blk.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/blk.c

## Summary
Implements the pstore/blk backend wrapper. It accepts a registered pstore block-like device, normalizes module/Kconfig sizing, registers the device with pstore/zone, and optionally implements a best-effort generic block-device mode using `kernel_read()` and `kernel_write()`.

## Main Responsibilities
- Define module parameters for kmsg, pmsg, console, ftrace sizes, max dump reason, best-effort mode, and target block device.
- Validate `struct pstore_device_info` and populate its embedded `struct pstore_zone_info`.
- Register and unregister one pstore/blk device at a time.
- Provide exported `register_pstore_device()`, `unregister_pstore_device()`, and `pstore_blk_get_config()`.
- Implement generic block reads/writes for best-effort operation.
- Resolve early boot block device names for built-in best-effort mode.

## Key Interfaces
- `register_pstore_device()` registers a non-block or dedicated backend with pstore/zone.
- `unregister_pstore_device()` removes it.
- `pstore_blk_get_config()` reports normalized block backend configuration.
- `__register_pstore_blk()` opens a block device and sets `zone.total_size`.
- `psblk_generic_blk_read()` and `psblk_generic_blk_write()` are generic storage callbacks.

## Important Behavior
`verify_size()` converts configured KB sizes into bytes, clamps disabled frontends to zero, enforces alignment, updates module parameter values, and stores final values in `dev->zone`. If a backend supplies no frontend flags, it is treated as supporting all frontends.

Best-effort mode requires `best_effort=Y` and a nonempty `blkdev`. It opens the target with `O_RDWR | O_DSYNC | O_NOATIME | O_EXCL`, rejects non-block files, and registers the block size as the storage area. Its write path refuses interrupt or IRQ-disabled contexts, making it unsuitable for reliable panic persistence.

## State and Synchronization
`pstore_blk_lock` protects `psblk_file` and the single global `pstore_device_info`. Register/unregister paths assert this lock for internal helpers.

## Cross-File Interactions
This file is an adapter between external pstore block devices and `zone.c` via `register_pstore_zone()`. The core pstore frontend is still provided by `platform.c` and `inode.c`.

## Risks
The best-effort generic block path cannot write in panic/interrupt contexts and is explicitly weaker than a backend with a dedicated panic-safe write callback. Only one pstore/blk device may be registered globally.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/blk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ftrace.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/ftrace.c

## Summary
Implements persistent function tracing into pstore. It registers an ftrace callback that writes compact call records to the active pstore backend and provides a debugfs knob to enable or disable recording.

## Main Responsibilities
- Capture function IP, parent IP, timestamp, and CPU into `struct pstore_ftrace_record`.
- Adjust and decode IPs when KASLR is active and persistent addresses need normalization.
- Register/unregister ftrace ops based on module parameter or debugfs writes.
- Create `/sys/kernel/debug/pstore/record_ftrace`.
- Merge multiple ftrace logs in timestamp order when reading recovered records.

## Key Interfaces
- `pstore_register_ftrace()` sets up debugfs and optionally starts ftrace recording.
- `pstore_unregister_ftrace()` disables recording and removes debugfs entries.
- `decode_ip()` is used by pstorefs display code to recover original symbols.
- `pstore_ftrace_combine_log()` merges two binary ftrace record streams.

## Important Behavior
The ftrace callback runs `notrace`, avoids recursion with `ftrace_test_recursion_trylock()`, disables local IRQs, and writes directly through `psinfo->write()`. It skips recording while `oops_in_progress` is set.

The timestamp counter intentionally is not atomic; the comment states that speed is preferred over exact ordering. Merge logic sorts by record timestamp and drops any leading partial record bytes by aligning sizes to `sizeof(struct pstore_ftrace_record)`.

## State and Synchronization
`pstore_ftrace_lock` serializes enable/disable operations. `record_ftrace` is both a module parameter and runtime state. `pstore_ftrace_stamp` is a global monotonically increasing best-effort counter.

## Cross-File Interactions
`inode.c` formats ftrace records through seq_file using `decode_ip()`. `ram.c` and `zone.c` call `pstore_ftrace_combine_log()` to merge per-CPU or per-zone logs.

## Risks
Ftrace persistence writes from sensitive contexts and depends on backend write behavior. Timestamp ordering is approximate because the stamp counter is not atomic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ftrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/inode.c

## Summary
Implements the `pstore` filesystem exposed at `/sys/fs/pstore`. It presents backend records as read-only regular files, supports unlink-to-erase, parses mount options, and coordinates record population/removal as backends register and unregister.

## Main Responsibilities
- Maintain the mounted pstore superblock and in-memory list of visible records.
- Create one file per `struct pstore_record`.
- Read ordinary records with `simple_read_from_buffer()` and ftrace records through seq_file decoding.
- Erase backend records on unlink when the backend supports `erase`.
- Parse and show the `kmsg_bytes` mount option.
- Register/unregister the `pstore` filesystem and sysfs mount point.

## Key Interfaces
- `pstore_mkfile()` creates a persistent dentry/inode for one backend record.
- `pstore_get_records()` asks the current backend to repopulate files.
- `pstore_put_backend_records()` removes all visible files for a backend.
- `pstore_init_fs()` and `pstore_exit_fs()` manage filesystem registration.
- `pstore_file_operations` handles open/read/llseek/release for record files.
- `pstore_dir_inode_operations` provides lookup and unlink.

## Important Behavior
Files are named `<type>-<backend>-<id>` with `.enc.z` appended for compressed records before decompression state is cleared. `pstore_mkfile()` de-duplicates by record type, id, and backend pointer to avoid duplicate files during rescans.

The filesystem is single-superblock. `psinfo_lock_root()` only returns a root dentry when both a backend and mounted superblock exist, and locks the root inode so file creation/removal is serialized with directory mutation.

Unlink first removes the record from the in-memory list, clears the dentry backpointer, then invokes the backend `erase()` under the backend read mutex. If no erase method exists, unlink fails with `-EPERM`.

## State and Synchronization
`records_list_lock` protects the global `records_list`. `pstore_sb_lock` protects `pstore_sb`. Backend read/erase operations use `record->psi->read_mutex`.

## Cross-File Interactions
`platform.c` calls `pstore_get_records()` and `pstore_get_backend_records()`. Backends such as `ram.c` and `zone.c` return records that this file materializes. `ftrace.c` provides decode/merge helpers for ftrace records.

## Risks
The filesystem borrows dentry pointers in `pstore_private`, so unlink and backend removal carefully clear them. Record ownership transfers to the filesystem only on successful `pstore_mkfile()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/pstore/internal.h

## Summary
Internal header shared by pstore core, filesystem, ftrace, and pmsg code.

## Main Responsibilities
- Declare global `kmsg_bytes` and `psinfo`.
- Provide ftrace frontend declarations or no-op stubs depending on `CONFIG_PSTORE_FTRACE`.
- Provide pmsg frontend declarations or no-op stubs depending on `CONFIG_PSTORE_PMSG`.
- Declare record population, file creation, record initialization, and filesystem init/exit helpers.

## Key Interfaces
- `pstore_set_kmsg_bytes()`
- `pstore_get_records()`
- `pstore_get_backend_records()`
- `pstore_put_backend_records()`
- `pstore_mkfile()`
- `pstore_record_init()`
- `pstore_init_fs()` and `pstore_exit_fs()`

## Cross-File Interactions
This header connects `platform.c`, `inode.c`, `ftrace.c`, and `pmsg.c` while keeping optional frontends compilable as stubs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/platform.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/platform.c

## Summary
Implements the generic pstore platform layer. It owns backend registration, compression/decompression, kmsg dump integration, optional console/ftrace/pmsg frontend registration, and periodic rescanning of backend records.

## Main Responsibilities
- Register exactly one active `struct pstore_info` backend.
- Save kmsg dumps into backend records during panic/oops/emergency paths.
- Optionally compress dmesg records with zlib deflate.
- Decompress compressed dmesg records when reading from a backend.
- Register console, ftrace, pmsg, and kmsg-dumper frontends according to backend flags.
- Populate pstorefs from backend records and periodically rescan after survivable oopses.
- Manage the `backend`, `compress`, `kmsg_bytes`, and `update_ms` module parameters.

## Key Interfaces
- `pstore_register()` validates and activates a backend.
- `pstore_unregister()` unregisters all frontends, removes files, and clears global backend state.
- `pstore_record_init()` initializes record metadata and timestamp.
- `pstore_get_backend_records()` reads all records from a backend and creates pstorefs files.
- `pstore_type_to_name()` and `pstore_name_to_type()` translate record types.
- `pstore_dump()` is the `kmsg_dumper` callback.

## Important Behavior
`pstore_dump()` snapshots up to `kmsg_bytes` from the end of the kernel log. It avoids blocking in NMI, panic, and emergency paths by using `raw_spin_trylock_irqsave()` where needed. It writes a textual header, optionally compresses the combined header and log data, then calls the backend `write()` for each part.

Compression uses zlib deflate only. Unsupported `compress=` values are logged and treated as `deflate`; `compress=none` disables compression. If compression expands or fails, the code stores as much uncompressed data as fits.

`pstore_register()` validates backend flags and required `read`/`write` callbacks, installs a compatibility `write_user` wrapper when missing, initializes locks, loads existing records, and then registers enabled frontends. `pstore_unregister()` performs the inverse order and flushes timers/work before removing backend records.

`pstore_get_backend_records()` caps backend iteration at 65,536 records to prevent infinite loops, lets backend `read()` allocate record buffers, decompresses dmesg when needed, and transfers ownership to `pstore_mkfile()` on success.

## State and Synchronization
`psinfo_lock` protects global backend registration/unregistration and frontend setup. `psinfo->buf_lock` serializes crash-dump writes. `psinfo->read_mutex` serializes backend read/erase/open/close operations. A timer and work item handle delayed rescans when runtime updates are enabled.

## Cross-File Interactions
`inode.c` provides pstorefs file creation/removal. `ftrace.c` and `pmsg.c` register optional frontends. Backends in `ram.c` and `zone.c` provide `struct pstore_info` implementations.

## Risks
Pstore runs in crash paths, so backend write callbacks must be safe for the reasons they advertise. Compression allocation only happens at registration time, but compression work during dump still consumes CPU in sensitive paths. Only one backend is active globally.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/platform.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/pmsg.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/pmsg.c

## Summary
Implements `/dev/pmsg0`, a character device for userspace messages persisted through pstore.

## Main Responsibilities
- Register a dynamic char device major named `pmsg`.
- Create a device class and `/dev/pmsg0` node with write-only permissions.
- Convert user writes into `PSTORE_TYPE_PMSG` records.
- Serialize writes with a mutex.

## Key Interfaces
- `pstore_register_pmsg()` creates the char device and class.
- `pstore_unregister_pmsg()` destroys them.
- `write_pmsg()` validates user memory, initializes a record, and calls `psinfo->write_user()`.

## Important Behavior
The write path first calls `access_ok()` outside the mutex to fault-check the range as much as possible, then serializes actual backend writes under `pmsg_lock`. It returns the backend result when nonzero, otherwise the byte count.

## Cross-File Interactions
`platform.c` registers this frontend when the backend advertises `PSTORE_FLAGS_PMSG`. `ram.c` and `zone.c` implement pmsg storage paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/pmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ram.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/ram.c

## Summary
Implements the `ramoops` pstore backend. It partitions reserved persistent RAM into dmesg, console, ftrace, and pmsg persistent RAM zones, reads old contents after reboot, writes new crash/console/ftrace/pmsg data, and registers the resulting backend with pstore.

## Main Responsibilities
- Parse module parameters, reserved-memory names, platform data, and device-tree properties.
- Allocate persistent RAM zones for dmesg records, console log, pmsg log, and ftrace records.
- Add ramoops-specific dmesg headers containing timestamp and compression state.
- Read old persistent records and expose them as pstore records.
- Write dmesg, console, ftrace, and pmsg records to appropriate PRZs.
- Erase records by zapping PRZs and freeing old buffers.
- Register a platform driver and optional dummy platform device for module-parameter configuration.

## Key Interfaces
- `ramoops_probe()` configures zones and calls `pstore_register()`.
- `ramoops_remove()` unregisters pstore and frees zones.
- `ramoops_pstore_read()`, `ramoops_pstore_write()`, `ramoops_pstore_write_user()`, and `ramoops_pstore_erase()` implement backend operations.
- `ramoops_init_przs()` allocates arrays of dump/ftrace zones.
- `ramoops_init_prz()` allocates single console/pmsg zones.

## Important Behavior
Dmesg zones are circularly selected by `dump_write_cnt`. Only `record->part == 1` is accepted, so a single crash is not split across multiple ramoops records. Before writing a dmesg record, the target PRZ is zapped so stale data is not appended ahead of the new header.

Ftrace can use either one shared zone or per-CPU zones. Per-CPU ftrace read builds a temporary PRZ and merges all per-CPU logs using `pstore_ftrace_combine_log()`.

Device-tree parsing supports modern reserved-memory bindings and compatibility behavior for older Chromebooks where ramoops was not under `reserved-memory`. Sizes are rounded down to powers of two before zone creation.

## State and Synchronization
Most persistent buffer synchronization lives in `ram_core.c`. `ramoops_context` tracks zone arrays, read/write counters, sizes, flags, ECC config, and the embedded `struct pstore_info`.

## Cross-File Interactions
Uses `persistent_ram_*()` helpers from `ram_core.c` and declarations from `ram_internal.h`. Registers with the pstore platform layer in `platform.c`, which then exposes records through `inode.c`.

## Risks
The backend depends on a correctly reserved physical memory range. Bad sizing can leave no room for a requested zone. Dmesg headers are required for recovered dmesg records; records without valid headers are zapped and skipped.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ram_core.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/ram_core.c

## Summary
Implements persistent RAM zones used by ramoops. It maps physical memory, maintains a circular buffer header, preserves old logs across boot, writes kernel/user data, and optionally protects data with Reed-Solomon ECC.

## Main Responsibilities
- Define `struct persistent_ram_buffer` header with signature, start, size, and data area.
- Map persistent memory using `vmap()` for valid PFNs or `ioremap()`/`ioremap_wc()` for I/O memory.
- Maintain circular write position and valid byte count.
- Copy old persistent data into kernel memory during initialization.
- Write kernel buffers and userspace buffers into circular persistent RAM.
- Encode/decode ECC for data blocks and buffer header.
- Free mappings, ECC state, old logs, labels, and zone structures.

## Key Interfaces
- `persistent_ram_new()` creates and initializes a PRZ.
- `persistent_ram_free()` releases it.
- `persistent_ram_write()` and `persistent_ram_write_user()` append data.
- `persistent_ram_save_old()`, `persistent_ram_old()`, `persistent_ram_old_size()`, and `persistent_ram_free_old()` manage recovered logs.
- `persistent_ram_zap()` clears the live buffer.
- `persistent_ram_ecc_string()` reports ECC correction state.

## Important Behavior
The ring buffer keeps `start` as the oldest valid byte and `size` as valid data length. Writes larger than the zone keep only the tail. Writes may split at the end of the buffer and wrap to offset zero.

ECC space is carved out of the data buffer after mapping. The code reserves parity bytes for each block plus header parity, reduces `buffer_size` accordingly, validates the stored header with ECC, and updates affected parity blocks after writes.

During post-init, a valid signature with sane start/size causes old data to be copied out in logical order. Invalid signatures, invalid counters, or `PRZ_FLAG_ZAP_OLD` cause the live buffer to be reset.

## State and Synchronization
Each PRZ has a raw spinlock unless `PRZ_FLAG_NO_LOCK` is set. The no-lock mode is intended for cases such as per-CPU ftrace where independent writers avoid sharing a zone.

## Cross-File Interactions
`ram.c` uses these APIs for all ramoops storage. `ram_internal.h` exposes the PRZ structure and helper declarations.

## Risks
Persistent memory mapping must match platform memory attributes. ECC sizing can invalidate a zone if parity overhead consumes the buffer. No-lock zones require external design guarantees to avoid concurrent corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ram_core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ram_internal.h -->
# File Research: sources/os/linux/linux-stable/fs/pstore/ram_internal.h

## Summary
Internal header for ramoops persistent RAM zones.

## Main Responsibilities
- Define PRZ flags for no-lock writes and single-boot old-data zapping.
- Define `struct persistent_ram_zone`, including physical mapping, buffer metadata, ECC state, and old-log storage.
- Declare persistent RAM allocation, free, write, zap, old-log, and ECC reporting helpers.

## Key Interfaces
- `persistent_ram_new()`
- `persistent_ram_free()`
- `persistent_ram_zap()`
- `persistent_ram_write()`
- `persistent_ram_write_user()`
- `persistent_ram_save_old()`
- `persistent_ram_old_size()`
- `persistent_ram_old()`
- `persistent_ram_free_old()`
- `persistent_ram_ecc_string()`

## Cross-File Interactions
Included by `ram.c` and `ram_core.c`; it is the private contract between the ramoops backend and its persistent RAM implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/ram_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/zone.c -->
# File Research: sources/os/linux/linux-stable/fs/pstore/zone.c

## Summary
Implements the pstore/zone intermediate backend used by pstore/blk. It partitions a linear storage backend into in-memory zones, recovers persisted zone contents, writes dmesg/pmsg/console/ftrace records, tracks dirty zones, and registers an embedded pstore backend.

## Main Responsibilities
- Define generic zone headers and dmesg subheaders.
- Allocate zones for pmsg, console, ftrace, and dmesg according to `pstore_zone_info`.
- Recover existing records from storage after reboot.
- Write dmesg records into rotating kmsg zones and circular frontend records into their zones.
- Flush dirty zones synchronously or through delayed work.
- Erase records from storage or mark metadata cleared.
- Export `register_pstore_zone()` and `unregister_pstore_zone()`.

## Key Interfaces
- `register_pstore_zone()` validates backend geometry/callbacks, allocates zones, builds `struct pstore_info`, and calls `pstore_register()`.
- `unregister_pstore_zone()` unregisters pstore, flushes dirty zones, frees memory, and resets counters.
- `psz_pstore_read()`, `psz_pstore_write()`, and `psz_pstore_erase()` implement backend operations.
- `psz_recovery()` performs first-use recovery from storage.
- `psz_zone_write()` updates memory and optionally flushes metadata, data, or full zones.

## Important Behavior
The storage area is laid out as pmsg, console, ftrace, then dmesg zones. Each zone has a `psz_buffer` header with signature, data length, start offset, and data. Dmesg zones additionally store `psz_kmsg_header` with magic, timestamp, compression flag, counter, and dump reason.

Recovery treats dmesg specially: it first reads only headers to validate zones, find newest crash sequence, set the next write slot, and recover oops/panic counters; then it reads full data only for valid zones. Console, pmsg, and ftrace use circular old buffers.

Writes prefer not to damage old records before recovery. If storage writes cannot be completed, zones are marked dirty and a delayed cleaner retries. Panic dmesg writes set `on_panic`, suppress non-dmesg writes, and flush all dirty zones when possible.

For kmsg writes, broken zones signaled by `-ENOMSG` cause the writer to try subsequent dmesg zones. The write path temporarily swaps in a fresh buffer so an old in-memory buffer can be restored if the attempted zone fails.

## State and Synchronization
A singleton `psz_context` holds all zones, counters, recovery state, panic state, backend info, and embedded pstore backend. `pstore_zone_info_lock` serializes registration/unregistration. Dirty flags and recovery/panic state are atomic.

## Cross-File Interactions
`blk.c` registers pstore/blk devices through this layer. `platform.c` consumes the embedded `struct pstore_info`. `ftrace.c` supplies log-combining logic for ftrace zone reads.

## Risks
Correctness depends on zone sizes being sector-aligned and large enough for headers. Dirty-zone retry behavior can leave data only in memory until backend writes succeed. Panic writes depend on backend `panic_write` availability for reliable crash persistence.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pstore/zone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/Kconfig

## Summary
Kconfig option for read-only QNX4 filesystem support.

## Main Responsibilities
- Define `QNX4FS_FS` as a tristate filesystem option.
- Depend on block-device support.
- Select `BUFFER_HEAD`.
- Document that the module name is `qnx4`.

## Cross-File Interactions
Controls compilation of `fs/qnx4/Makefile` and the read-only QNX4 filesystem implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/Makefile

## Summary
Build rules for the QNX4 filesystem module.

## Main Responsibilities
- Build `qnx4.o` when `CONFIG_QNX4FS_FS` is enabled.
- Compose the module from `inode.o`, `dir.o`, `namei.o`, and `bitmap.o`.

## Cross-File Interactions
The listed objects implement mount/inode/block mapping, directory iteration, lookup, and free-block counting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/bitmap.c

## Summary
Provides QNX4 free-block counting for `statfs`.

## Main Responsibilities
- Locate bitmap blocks through the cached `.bitmap` inode in `qnx4_sb_info`.
- Read bitmap blocks and count zero bits as free blocks.
- Stop counting on I/O error and return the count accumulated so far.

## Key Interfaces
- `qnx4_count_free_blocks()` is called by `qnx4_statfs()`.

## Important Behavior
The function interprets each byte of bitmap data as eight block bits and computes free space as total bits minus `memweight()` of set bits.

## Cross-File Interactions
`inode.c` caches the `.bitmap` inode during root validation and uses this helper in `qnx4_statfs()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/dir.c

## Summary
Implements QNX4 directory iteration and directory file/inode operations.

## Main Responsibilities
- Walk directory file blocks through `qnx4_block_map()`.
- Interpret each directory entry as either an inode entry or link entry.
- Emit valid names with `dir_emit()`.
- Provide `qnx4_dir_operations` and `qnx4_dir_inode_operations`.

## Key Interfaces
- `qnx4_readdir()` is the `iterate_shared` implementation.
- `qnx4_dir_operations` uses generic llseek/read-dir/fsync/lease helpers.
- `qnx4_dir_inode_operations.lookup` points to `qnx4_lookup()`.

## Important Behavior
QNX4 link entries redirect inode calculation through `dl_inode_blk` and `dl_inode_ndx`; non-link entries calculate inode numbers from the containing block and entry index. Name validation is delegated to `get_entry_fname()`.

## Cross-File Interactions
Uses directory entry helpers from `qnx4.h`, block mapping from `inode.c`, and lookup from `namei.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/inode.c

## Summary
Implements QNX4 mount, superblock validation, inode loading, extent-based block mapping, statfs, address-space operations, inode cache, and filesystem registration.

## Main Responsibilities
- Force QNX4 mounts read-only.
- Validate the root directory and locate the `.bitmap` file.
- Map logical file blocks through the first extent and chained extent blocks.
- Load raw QNX4 inode entries into Linux inodes.
- Provide read-only file, directory, and symlink behavior.
- Register/unregister the `qnx4` filesystem and inode slab cache.

## Key Interfaces
- `qnx4_block_map()` maps logical blocks to physical blocks.
- `qnx4_iget()` reads and initializes an inode.
- `qnx4_fill_super()` mounts and validates a QNX4 filesystem.
- `qnx4_statfs()` reports block/free counts and limits.
- `qnx4_get_tree()` mounts via `get_tree_bdev()`.

## Important Behavior
Block mapping treats QNX4 extent block numbers as one-based on disk, subtracting one for `sb_bread()` and adding `offset - 1` when returning a physical block from an extent. Additional extents are read from chained `qnx4_xblk` blocks with signature `IamXblk`.

Mount validation reads block 1 as the superblock, confirms the root directory name is `/`, scans the root directory for `.bitmap`, and stores a heap copy of that raw inode for later statfs.

`qnx4_iget()` maps regular files to `generic_ro_fops`, directories to QNX4 dir ops, symlinks to page symlink ops, and rejects other modes as bad inodes.

## State and Synchronization
Per-inode raw QNX4 metadata is stored in `struct qnx4_inode_info`. Per-superblock state stores version and cached bitmap inode. The inode cache is created at module init and destroyed after `rcu_barrier()`.

## Cross-File Interactions
`dir.c` and `namei.c` rely on `qnx4_block_map()` and `qnx4_iget()`. `bitmap.c` relies on the cached `.bitmap` inode established during mount.

## Risks
The implementation is read-only and intentionally minimal. Block mapping and directory traversal depend on trusting on-disk extent and directory structures after basic validation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/namei.c

## Summary
Implements QNX4 directory lookup.

## Main Responsibilities
- Scan directory blocks for an entry whose name matches a dentry.
- Handle normal inode entries and link entries.
- Resolve matched inode numbers through `qnx4_iget()`.
- Return aliases through `d_splice_alias()`.

## Key Interfaces
- `qnx4_lookup()` is the exported directory lookup operation.
- `qnx4_find_entry()` scans directory contents.
- `qnx4_match()` validates and compares one directory entry.

## Important Behavior
QNX4 can write placeholder entries with all options zero; `get_entry_fname()` filters invalid/unused entries so lookup does not match them. Link entries replace the initially calculated inode number with the linked inode block/index.

## Cross-File Interactions
Uses `qnx4_block_map()` and `qnx4_iget()` from `inode.c`, and directory entry helpers from `qnx4.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/qnx4.h -->
# File Research: sources/os/linux/linux-stable/fs/qnx4/qnx4.h

## Summary
Private header for QNX4 filesystem implementation.

## Main Responsibilities
- Define QNX4 superblock and inode wrapper structures.
- Declare inode, lookup, bitmap, block-map, and directory operation interfaces.
- Provide accessors for `qnx4_sb_info`, `qnx4_inode_info`, and raw inode data.
- Define `union qnx4_directory_entry` to safely inspect inode and link directory entries.
- Provide `get_entry_fname()` for directory entry validation/name extraction.

## Important Behavior
The directory-entry union uses a fixed 48-byte `de_name` array to avoid compiler confusion over different union member name-array sizes. Compile-time assertions ensure the status byte is at the same offset in all relevant structures.

## Cross-File Interactions
Included by all QNX4 implementation files and backed by UAPI on-disk structure definitions in `include/uapi/linux/qnx4_fs.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx4/qnx4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/Kconfig

## Summary
Kconfig options for read-only QNX6 filesystem support and optional debug logging.

## Main Responsibilities
- Define `QNX6FS_FS` as a tristate option depending on `BLOCK` and `CRC32`.
- Select `BUFFER_HEAD`.
- Document that the module is `qnx6` and currently read-only.
- Define `QNX6FS_DEBUG` to enable extended debug output.

## Cross-File Interactions
Controls the QNX6 object build and optionally adds `-DDEBUG` through the Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/Makefile

## Summary
Build rules for the QNX6 filesystem module.

## Main Responsibilities
- Build `qnx6.o` when `CONFIG_QNX6FS_FS` is enabled.
- Compose the module from `inode.o`, `dir.o`, `namei.o`, and `super_mmi.o`.
- Add debug compiler flags when `CONFIG_QNX6FS_DEBUG` is enabled.

## Cross-File Interactions
The objects cover mount/inode/block mapping, directory iteration/search, lookup, and MMI superblock handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/dir.c

## Summary
Implements QNX6 directory iteration and name lookup helpers, including support for long filenames stored in the filesystem's longfile metadata file.

## Main Responsibilities
- Iterate directory pages and emit short or long filenames.
- Resolve long filename records through the mounted longfile inode.
- Validate long filename size and checksum where applicable.
- Search directories for matching short or long names.
- Cache the last successful lookup page in `i_dir_start_lookup`.

## Key Interfaces
- `qnx6_readdir()` is the directory `iterate_shared` operation.
- `qnx6_find_ino()` searches a directory and returns a matching inode number.
- `qnx6_dir_operations` and `qnx6_dir_inode_operations` provide VFS operations.

## Important Behavior
Short names are stored directly in directory entries. Long names use entries with `de_size == 0xff`; the entry points to a long filename record by block number. Non-MMI filesystems verify the long-name checksum using `qnx6_lfile_checksum()`.

Lookup starts at the cached page from the previous hit and wraps around, improving repeated lookup locality in large directories.

## Cross-File Interactions
`namei.c` calls `qnx6_find_ino()`. Long-name reads use `sbi->longfile`, created in `inode.c` from the superblock's Longfile root node.

## Risks
Long filename integrity is mostly best-effort: checksum mismatches are logged but do not prevent emitting the name. Directory reads depend on the page-cache/block-map path working for both directories and the longfile inode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/inode.c

## Summary
Implements QNX6 mount, superblock selection, block mapping, inode loading, statfs, mount options, address-space operations, inode cache, and filesystem registration.

## Main Responsibilities
- Parse the `mmi_fs` mount option.
- Force QNX6 mounts read-only.
- Detect little-endian and big-endian superblocks.
- Validate primary and secondary superblocks with CRC32 and choose the active one by serial number.
- Support the MMI superblock variant through `super_mmi.c`.
- Build private inodes for the inode table and long filename file.
- Map file logical blocks through direct root pointers and indirect pointer trees.
- Load QNX6 inode entries into Linux inodes.
- Register/unregister the `qnx6` filesystem and inode slab cache.

## Key Interfaces
- `qnx6_iget()` loads a filesystem inode.
- `qnx6_block_map()` maps logical blocks to device blocks.
- `qnx6_fill_super()` performs mount validation/setup.
- `qnx6_private_inode()` creates internal metadata inodes.
- `qnx6_statfs()` reports filesystem statistics.
- `qnx6_parse_param()` handles `mmi_fs`.

## Important Behavior
Superblock handling first reads with a 512-byte block size, validates magic and checksum, then switches to the filesystem block size and rereads. A bootblock offset is tried first, then offset zero. The second superblock is located after the data block count plus the superblock area. The active copy is the one with the greater serial number.

Block mapping uses `di_filelevels` to determine indirect depth. The selected direct pointer is based on high bits of the logical block number; each indirect level indexes a block of 32-bit block pointers using `s_ptrbits = ilog2(blocksize / 4)`.

`qnx6_iget()` reads inode entries from the private inode-table inode via page cache, initializes uid/gid/timestamps/size/blocks, copies direct block pointers and file level, and installs read-only file, directory, symlink, or special inode operations.

## State and Synchronization
`struct qnx6_sb_info` stores active superblock buffer, block offset, pointer-bit geometry, mount options, endian mode, and private metadata inodes. `struct qnx6_inode_info` stores block pointers, file levels, and lookup cache.

## Cross-File Interactions
`dir.c` depends on the longfile private inode and endian helpers. `namei.c` calls `qnx6_iget()`. `super_mmi.c` supplies MMI-specific active-superblock selection.

## Risks
The driver is read-only but still follows on-disk pointer trees. It validates superblocks and pointer-level limits, but corrupted indirect pointers can still cause read failures or skipped data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/namei.c

## Summary
Implements QNX6 dentry lookup.

## Main Responsibilities
- Reject names longer than `QNX6_LONG_NAME_MAX`.
- Search a directory with `qnx6_find_ino()`.
- Load the found inode with `qnx6_iget()`.
- Return the inode through `d_splice_alias()`.

## Key Interfaces
- `qnx6_lookup()` is the directory inode lookup operation.

## Cross-File Interactions
Uses directory search from `dir.c` and inode loading from `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/qnx6.h -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/qnx6.h

## Summary
Private header for the QNX6 filesystem implementation.

## Main Responsibilities
- Define filesystem-endian integer typedefs.
- Define QNX6 superblock and inode wrapper structures.
- Provide endian conversion helpers controlled by mounted filesystem byte order.
- Provide mount option helpers.
- Declare inode, lookup, directory, MMI superblock, and directory-search interfaces.

## Key Interfaces
- `QNX6_SB()` and `QNX6_I()` access private superblock/inode data.
- `fs16_to_cpu()`, `fs32_to_cpu()`, and `fs64_to_cpu()` decode on-disk fields.
- `qnx6_mmi_fill_super()` is declared for MMI mounts.
- `qnx6_find_ino()` is declared for lookup.

## Cross-File Interactions
Included by all QNX6 implementation files and backed by UAPI QNX6 on-disk structures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/qnx6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/super_mmi.c -->
# File Research: sources/os/linux/linux-stable/fs/qnx6/super_mmi.c

## Summary
Implements QNX6 MMI filesystem superblock handling.

## Main Responsibilities
- Read and validate two MMI superblocks.
- Verify magic and CRC32 checksums.
- Switch to the on-disk block size after the first superblock read.
- Convert MMI superblock layout into the standard `qnx6_super_block` layout.
- Select the active superblock by serial number.
- Set QNX6 block offset for MMI layout.

## Key Interfaces
- `qnx6_mmi_fill_super()` is called by `qnx6_fill_super()` when the `mmi_fs` mount option is set.

## Important Behavior
The second MMI superblock is located using `sb_num_blocks + QNX6_SUPERBLOCK_AREA / blocksize`. After selecting the active copy, the code copies the MMI fields into a standard QNX6 superblock structure, writes that structure into the selected buffer, and stores it in `sbi->sb`.

## Cross-File Interactions
Uses endian helpers and debug hooks from `qnx6.h`; returns the active superblock to `inode.c` mount setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/qnx6/super_mmi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/quota/Kconfig

## Summary
Defines Kconfig options for Linux VFS quota support and quota file formats.

## Main Responsibilities
- Define core `QUOTA` support and select `QUOTACTL`.
- Configure optional netlink quota warning reporting.
- Retain obsolete console quota warning option behind `BROKEN`.
- Enable quota sanity checking with `QUOTA_DEBUG`.
- Define generic tree-structured quota file support as `QUOTA_TREE`.
- Enable old V1 quota format support with `QFMT_V1`.
- Enable VFS V0/V1 quota format support with `QFMT_V2`, selecting `QUOTA_TREE`.
- Define internal `QUOTACTL`.

## Cross-File Interactions
Controls the quota objects built by `fs/quota/Makefile` and the availability of VFS quota syscalls, warning paths, and on-disk quota format parsers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/quota/Makefile

## Summary
Build rules for the Linux quota subsystem.

## Main Responsibilities
- Build `dquot.o` for core quota support.
- Build V1 and V2 quota format handlers based on `QFMT_V1` and `QFMT_V2`.
- Build `quota_tree.o` for tree-structured quota files.
- Build `quota.o` and `kqid.o` for quotactl support.
- Build `netlink.o` for quota warning netlink support.

## Cross-File Interactions
The Makefile maps Kconfig quota features to their implementation objects.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/compat.h -->
# File Research: sources/os/linux/linux-stable/fs/quota/compat.h

## Summary
Defines 32-bit compatibility structures used by quota ioctl/syscall handling.

## Main Responsibilities
- Define `compat_if_dqblk` for compatible quota block/inode limit and usage fields.
- Define `compat_fs_qfilestat` for compatible quota file statistics.
- Define `compat_fs_quota_stat` for compatible filesystem quota status.

## Important Behavior
The structures use `compat_u64`, `compat_uint_t`, and `compat_int_t` so 32-bit userspace layouts are stable when handled by a 64-bit kernel.

## Cross-File Interactions
Included by quota syscall/compat handling code outside this group to translate quota status and limit structures between native and compat ABIs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/compat.h -->