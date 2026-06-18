# subset-b-005748 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/vmcore.c -->
# sources/distributed-fs/ceph-client/fs/proc/vmcore.c

## Purpose
`vmcore.c` exposes the previous kernel's crash dump as `/proc/vmcore`, presenting crash-kernel ELF headers, note data, PT_LOAD memory ranges, optional device dumps, and optional device RAM as a single synthetic ELF core file.

## Important APIs, types, and functions
Global state includes `vmcore_list`, `elfcorebuf`, `elfnotes_buf`, `vmcore_size`, `proc_vmcore`, `vmcore_cb_list`, and optional `vmcoredd_list`. External APIs are `read_from_oldmem`, `register_vmcore_cb`, `unregister_vmcore_cb`, `vmcore_add_device_dump`, and `vmcore_cleanup`. Core helpers parse ELF32/ELF64 headers, merge PT_NOTE segments, rewrite PT_LOAD offsets, read or mmap old memory, and add device RAM PT_LOAD ranges.

## Control flow
`vmcore_init` asks architecture code to provide the ELF core header, validates the ELF class, reads all program headers, collapses multiple PT_NOTE headers into one page-aligned note segment, builds `vmcore_list` from PT_LOAD records, computes `vmcore_size`, and creates `/proc/vmcore`. Reads walk the synthetic layout in order: ELF header buffer, device dump notes, normal notes, then old-memory ranges. `mmap` mirrors that layout, using direct pfn remap where possible and a fault handler fallback on s390.

## State and persistence
The file is runtime state in the capture kernel, backed by memory from the crashed kernel and by vmalloc/device dump buffers. `vmcore_opened` prevents late device dump/RAM mutation from silently changing an already observed core image. SRCU-protected callbacks can mark PFNs as not RAM, causing reads and mappings to return zero pages.

## Dependencies and integration points
This code depends on crash dump boot parameters, architecture-specific oldmem helpers, ELF core validation, procfs, vmalloc, `kmsg_dump`-adjacent crash infrastructure, optional confidential-computing encrypted oldmem reads, and optional device dump/device RAM callback providers.

## Risks and test signals
Risks include malformed ELF headers, integer/rounding mistakes when rewriting note and load offsets, stale callback lifetime during read/mmap, zero-page substitution for device memory, encrypted-memory read mismatches, and late device dump insertion racing open. Test signals include ELF32 and ELF64 vmcore boot tests, sparse RAM callback tests, `/proc/vmcore` read and mmap comparison, device dump notes in crash tools, and invalid PT_NOTE truncation warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/vmcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc_namespace.c -->
# sources/distributed-fs/ceph-client/fs/proc_namespace.c

## Purpose
`proc_namespace.c` implements `/proc/<pid>/mounts`, `/proc/<pid>/mountinfo`, and `/proc/<pid>/mountstats`, formatting a task's mount namespace through seq_file operations.

## Important APIs, types, and functions
Important functions are `mounts_open_common`, `mounts_poll`, `show_vfsmnt`, `show_mountinfo`, `show_vfsstat`, `show_sb_opts`, `show_vfsmnt_opts`, `mangle`, and `mounts_release`. It fills `struct proc_mounts` with a referenced `mnt_namespace`, root path, and selected show callback.

## Control flow
Open resolves the target task, pins its mount namespace and fs root under `task_lock`, opens a private seq_file using `mounts_op`, and records the namespace event counter for polling. Iteration is delegated to mount namespace seq operations; each mount is formatted in legacy mounts, modern mountinfo, or mountstats syntax. Release drops the saved root path and namespace reference.

## State and persistence
The state is a per-open snapshot of task root and namespace reference, while poll observes live namespace event changes through `ns->event` and `ns->poll`. No persistent storage is written.

## Dependencies and integration points
It integrates procfs task lookup, VFS namespace internals, `security_sb_show_options`, superblock show hooks, path escaping, idmapped mount display, propagation tags, and filesystem-specific statistics hooks.

## Risks and test signals
Risks include namespace lifetime races, chroot-relative path hiding via `SEQ_SKIP`, incorrect escaping of mount fields, stale poll events, and discrepancies between mount option sources. Test signals include bind/shared/slave/unbindable mounts, idmapped mounts, chrooted readers, filesystems with custom `show_devname`/`show_options`/`show_stats`, and poll after namespace mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/Kconfig -->
# sources/distributed-fs/ceph-client/fs/pstore/Kconfig

## Purpose
This Kconfig file defines the pstore feature matrix: generic persistent store support, compression, console/pmsg/ftrace frontends, RAM backend, zone manager, and block backend options.

## Important APIs, types, and functions
It introduces symbols `PSTORE`, `PSTORE_DEFAULT_KMSG_BYTES`, `PSTORE_COMPRESS`, `PSTORE_CONSOLE`, `PSTORE_PMSG`, `PSTORE_FTRACE`, `PSTORE_RAM`, `PSTORE_ZONE`, `PSTORE_BLK`, and block backend size/device parameters.

## Control flow
Selections wire dependencies at build time: pstore compression selects zlib inflate/deflate, pmsg selects RT mutexes, ftrace depends on function tracer/debugfs, RAM selects Reed-Solomon ECC support, and block selects `PSTORE_ZONE`.

## State and persistence
The file controls compiled-in capabilities and default module parameter values. Runtime persistence is implemented by the selected backends, not by Kconfig itself.

## Dependencies and integration points
It integrates with architecture I/O memory support, block support, ftrace/debugfs, zlib, Reed-Solomon libraries, and pstore admin documentation.

## Risks and test signals
Risks are invalid default sizing, feature combinations that expose frontends without backend capacity, and confusion between module parameters and Kconfig defaults. Test signals are build coverage for pstore disabled, each frontend alone, RAM, block, compression disabled, and combined frontend/backend configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/Makefile -->
# sources/distributed-fs/ceph-client/fs/pstore/Makefile

## Purpose
The Makefile maps pstore Kconfig symbols to built objects and modules.

## Important APIs, types, and functions
It builds `pstore.o` from `inode.o` and `platform.o`, conditionally adds `ftrace.o` and `pmsg.o`, builds `ramoops.o` from `ram.o` and `ram_core.o`, `pstore_zone.o` from `zone.o`, and `pstore_blk.o` from `blk.o`.

## Control flow
The kernel build system includes objects according to `CONFIG_PSTORE*` symbols. Frontend objects are linked into the generic pstore module, while RAM, zone, and block backends remain separate objects/modules.

## State and persistence
No runtime state exists here; it defines build composition and therefore which persistence mechanisms can exist at runtime.

## Dependencies and integration points
It integrates Kbuild, pstore core, frontend options, and backend modules.

## Risks and test signals
Risks are missing object inclusion for a selected feature or link errors when optional stubs and real implementations diverge. Test signals are allmodconfig, builtin-only pstore, modular ramoops, modular pstore_blk, and configurations with ftrace or pmsg disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/blk.c -->
# sources/distributed-fs/ceph-client/fs/pstore/blk.c

## Purpose
`blk.c` implements the pstore block-device frontend to the pstore/zone manager, registering either a dedicated `pstore_device_info` supplied by another driver or a best-effort generic block device.

## Important APIs, types, and functions
External APIs are `register_pstore_device`, `unregister_pstore_device`, and `pstore_blk_get_config`. Important helpers include `__register_pstore_device`, `__register_pstore_blk`, `psblk_generic_blk_read`, `psblk_generic_blk_write`, `early_boot_devpath`, `__best_effort_init`, and `__best_effort_exit`.

## Control flow
Registration validates zone callbacks and total size, applies module/Kconfig sizes for kmsg, pmsg, console, and ftrace, sets zone ownership, and calls `register_pstore_zone`. Best-effort mode resolves and opens `blkdev`, verifies it is a block device, derives total bytes, and exposes kernel read/write callbacks to the zone manager.

## State and persistence
Global state under `pstore_blk_lock` tracks `psblk_file` and the active `pstore_device_info`. Persistent data lives on the configured block device and is partitioned by `zone.c`.

## Dependencies and integration points
It depends on block devices, kernel file I/O, early boot device lookup for built-in use, module parameters, and the exported pstore/zone backend registration API.

## Risks and test signals
Risks include using best-effort writes without a panic-safe `panic_write`, block-device exclusive open failures, size alignment surprises, single-backend conflicts, and write rejection from interrupt context. Test signals include invalid `blkdev`, PARTUUID/major-minor resolution, aligned and unaligned size parameters, unregister cleanup, and panic/oops capture with and without a dedicated panic writer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/blk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ftrace.c -->
# sources/distributed-fs/ceph-client/fs/pstore/ftrace.c

## Purpose
`ftrace.c` records function trace records into the active pstore backend and exposes a debugfs knob to enable or disable recording.

## Important APIs, types, and functions
Key functions are `pstore_register_ftrace`, `pstore_unregister_ftrace`, `pstore_set_ftrace_enabled`, `pstore_ftrace_call`, `adjust_ip`, `decode_ip`, and `pstore_ftrace_combine_log`. State includes `pstore_ftrace_ops`, `record_ftrace`, `pstore_ftrace_lock`, `pstore_ftrace_stamp`, and the debugfs directory.

## Control flow
Registration creates `/sys/kernel/debug/pstore/record_ftrace`, optionally registers global ftrace ops, and writes each callback as a `PSTORE_TYPE_FTRACE` record through `psinfo->write`. The callback avoids oops recursion, disables local IRQs while creating the record, stores CPU and timestamp metadata, and lets the backend choose the zone.

## State and persistence
Runtime state is the enable flag and timestamp counter. Persistence is delegated to the backend ftrace storage. KASLR-aware address adjustment supports decoding after reboot.

## Dependencies and integration points
It depends on function tracer internals, debugfs, pstore frontend records, SMP CPU encoding helpers, and optional KASLR built-in address handling.

## Risks and test signals
Risks include recursion, tracing during unstable oops paths, timestamp races by design, KASLR address decode errors, and memory allocation failures while combining per-CPU logs. Test signals include toggling the debugfs knob, per-CPU ftrace recovery, KASLR built-in boot, disabled backend write support, and trace ordering after merge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/inode.c -->
# sources/distributed-fs/ceph-client/fs/pstore/inode.c

## Purpose
`inode.c` implements the pstore filesystem mounted at `/sys/fs/pstore`, presenting persistent backend records as read-only files and erasing backend records when files are unlinked.

## Important APIs, types, and functions
Public pstore helpers are `pstore_init_fs`, `pstore_exit_fs`, `pstore_get_records`, `pstore_put_backend_records`, and `pstore_mkfile`. Internal state includes `records_list`, `records_list_lock`, `pstore_sb`, `pstore_private`, and mount context option `kmsg_bytes`.

## Control flow
Mount creates a single ramfs-like superblock, applies `kmsg_bytes`, stores the root in `pstore_sb`, and calls `pstore_get_records` to read backend entries. `pstore_mkfile` deduplicates records by backend/type/id, creates a persistent dentry, and stores the `pstore_record` in inode private data. Reads use simple buffers except ftrace, which formats binary trace records through seq_file. Unlink removes the file from `records_list` and calls backend `erase`.

## State and persistence
Filesystem state is volatile dentries/inodes backed by backend record buffers. The actual persistent state is erased only through backend callbacks. Remount updates global `kmsg_bytes`.

## Dependencies and integration points
It integrates VFS fs_context, sysfs mount point creation, simple directory operations, seq_file, pstore platform code, and backend read/erase locking through `psi->read_mutex`.

## Risks and test signals
Risks include duplicate record handling, unregister while mounted, unlink races, ftrace record alignment, remount option propagation, and backend erase failure. Test signals include mounting before and after backend registration, repeated rescans, unlink with and without erase support, ftrace file reads, remount `kmsg_bytes`, and backend unregister removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/internal.h -->
# sources/distributed-fs/ceph-client/fs/pstore/internal.h

## Purpose
`internal.h` is the private interface between pstore core, filesystem presentation, and optional ftrace/pmsg frontends.

## Important APIs, types, and functions
It declares `kmsg_bytes`, `psinfo`, `pstore_set_kmsg_bytes`, record retrieval helpers, `pstore_mkfile`, `pstore_record_init`, filesystem init/exit hooks, and optional ftrace/pmsg registration functions with stub fallbacks.

## Control flow
Compile-time conditionals keep core call sites simple: when ftrace or pmsg is disabled, registration helpers become no-ops and ftrace log combining returns an empty result.

## State and persistence
The header owns no state directly, but exposes global pstore state and current backend pointer used by the compiled pstore objects.

## Dependencies and integration points
It depends on `linux/pstore.h`, time/types headers, and optional frontend configurations.

## Risks and test signals
Risks include signature drift between stubs and implementations, accidental use of `psinfo` before registration, and frontend-disabled behavior masking missing backend support. Test signals are compile coverage for all optional frontend combinations and runtime registration with pmsg/ftrace disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/platform.c -->
# sources/distributed-fs/ceph-client/fs/pstore/platform.c

## Purpose
`platform.c` is the generic pstore core. It registers one backend, captures kmsg dumps, optional console/ftrace/pmsg streams, compresses dmesg records, and populates the pstore filesystem from backend records.

## Important APIs, types, and functions
Exported APIs include `pstore_register`, `pstore_unregister`, `pstore_type_to_name`, `pstore_name_to_type`, `pstore_record_init`, `pstore_get_backend_records`, and `pstore_set_kmsg_bytes`. Key helpers are `pstore_dump`, compression allocation/free, `decompress_record`, console write hook, `pstore_write_user_compat`, and timer/workqueue update functions.

## Control flow
Backend registration validates flags and read/write callbacks, installs default `write_user` if needed, initializes backend locks, allocates compression buffers for dmesg, scans existing records, and registers enabled frontends. Kmsg dumping snapshots up to `kmsg_bytes`, optionally deflates data, writes one or more records, and schedules delayed filesystem refresh for oops records. Backend reads loop up to 65,536 records, decompress supported dmesg entries, and pass them to `pstore_mkfile`.

## State and persistence
Only one backend is active in global `psinfo`. Persistent state is backend-owned; core state includes compression buffers, oops counters, refresh timer/work item, selected backend parameter, and filesystem record buffers.

## Dependencies and integration points
It integrates kmsg dumpers, consoles, pstorefs, zlib, timers/workqueues, module parameters, optional frontends, and backend callback contracts.

## Risks and test signals
Risks include blocking in panic/NMI paths, compression workspace allocation failure, backend read loops, single-backend conflicts, decompression trust in record metadata, and unregister races with timer/work. Test signals include panic and oops capture, compression fallback, backend selection parameter, console/pmsg/ftrace registration, delayed oops refresh, and corrupt compressed record handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/pmsg.c -->
# sources/distributed-fs/ceph-client/fs/pstore/pmsg.c

## Purpose
`pmsg.c` exposes `/dev/pmsg0`, a write-only user-space channel that stores messages in the active pstore backend as `PSTORE_TYPE_PMSG`.

## Important APIs, types, and functions
Important functions are `write_pmsg`, `pstore_register_pmsg`, `pstore_unregister_pmsg`, and `pmsg_devnode`. State includes `pmsg_lock`, `pmsg_class`, and dynamically allocated `pmsg_major`.

## Control flow
Registration allocates a char-device major, creates a class with mode `0220`, and creates `pmsg0`. Writes validate nonzero count and `access_ok`, initialize a pstore record, serialize with `pmsg_lock`, and call `psinfo->write_user`.

## State and persistence
The char device has no persistent state. Message bytes persist only if the backend implements and stores `PSTORE_TYPE_PMSG`.

## Dependencies and integration points
It integrates char devices, class/device creation, uaccess checks, pstore platform registration, and backend `write_user`.

## Risks and test signals
Risks include missing backend `write_user`, unregister after partial registration, large user writes, and concurrent writers. Test signals include device node mode, write with invalid user pointer, backend failure propagation, unregister cleanup, and reboot recovery of pmsg records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/pmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ram.c -->
# sources/distributed-fs/ceph-client/fs/pstore/ram.c

## Purpose
`ram.c` implements the `ramoops` pstore backend, carving reserved RAM into persistent dmesg, console, pmsg, and ftrace zones.

## Important APIs, types, and functions
Core state is `struct ramoops_context`, with arrays of `persistent_ram_zone` pointers, sizes, counters, ECC config, and embedded `pstore_info`. Important functions include `ramoops_probe`, `ramoops_pstore_read`, `ramoops_pstore_write`, `ramoops_pstore_write_user`, `ramoops_pstore_erase`, `ramoops_init_przs`, `ramoops_init_prz`, `ramoops_parse_dt`, and dummy module-parameter platform-device setup.

## Control flow
Probe parses platform data or device tree, rounds zone sizes down to powers of two, allocates dmesg/console/pmsg/ftrace PRZs in order, allocates the dmesg scratch buffer, sets pstore frontend flags, and registers with pstore. Reads enumerate old dmesg zones first, then console, pmsg, and ftrace. Writes route by record type; dmesg takes only part 1, zaps the target zone, writes a ramoops header, and advances the circular write counter.

## State and persistence
Persistent state is a reserved physical memory region with PRZ headers, circular data, optional ECC, and old-log snapshots saved after boot. Runtime counters track read/write positions and per-CPU ftrace merging.

## Dependencies and integration points
It depends on platform devices, reserved memory/device tree bindings, pstore core, `ram_core.c`, ECC configuration, module parameters, and optional pmsg/ftrace/console frontends.

## Risks and test signals
Risks include overlapping or undersized memory regions, old invalid headers, power-of-two truncation surprises, per-CPU ftrace allocation failure, ECC metadata sizing, and pmsg calling the wrong write path. Test signals include DT and module-param boot, all zone types, dmesg header parsing, erase/unlink, ECC correction notices, per-CPU ftrace merge, and reboot recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ram_core.c -->
# sources/distributed-fs/ceph-client/fs/pstore/ram_core.c

## Purpose
`ram_core.c` provides persistent circular RAM-zone management for `ramoops`, including mapping physical memory, validating headers, preserving old logs, wrapping writes, and optional Reed-Solomon ECC.

## Important APIs, types, and functions
Important exported functions are `persistent_ram_new`, `persistent_ram_free`, `persistent_ram_write`, `persistent_ram_write_user`, `persistent_ram_save_old`, `persistent_ram_old`, `persistent_ram_old_size`, `persistent_ram_free_old`, `persistent_ram_zap`, and `persistent_ram_ecc_string`. Internal state is `struct persistent_ram_buffer` plus `struct persistent_ram_zone`.

## Control flow
Zone creation maps the physical range via `vmap` for valid RAM PFNs or `ioremap` for I/O memory, initializes ECC layout, checks the signature, saves existing data if valid, or zaps invalid/single-use buffers. Writes trim oversized input to the last buffer-size bytes, update `size` and `start`, copy data in one or two wrapped pieces, and refresh ECC for data and header.

## State and persistence
The PRZ header and data live in reserved RAM across reboots. Runtime state includes mapping addresses, ECC decoder/workspace, corrected/bad counters, and an allocated `old_log` snapshot used by pstore reads.

## Dependencies and integration points
It depends on raw spinlocks, atomic metadata, vmap/ioremap, memregion ownership, uaccess, Reed-Solomon libraries, and `ram_internal.h`.

## Risks and test signals
Risks include ECC area consuming the buffer, invalid header recovery, wraparound copy errors, lockless ftrace writes, mapping type mismatch, and leaking memregions on failure. Test signals include valid old buffer recovery, invalid signature zap, user and kernel writes crossing buffer end, ECC correction/uncorrectable reporting, pfn_valid and I/O mappings, and free/unmap cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ram_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ram_internal.h -->
# sources/distributed-fs/ceph-client/fs/pstore/ram_internal.h

## Purpose
`ram_internal.h` defines the private `ramoops` persistent RAM zone structure, flags, and function prototypes shared by `ram.c` and `ram_core.c`.

## Important APIs, types, and functions
It defines `PRZ_FLAG_NO_LOCK`, `PRZ_FLAG_ZAP_OLD`, `struct persistent_ram_zone`, and prototypes for PRZ allocation, freeing, zapping, writing, old-log handling, and ECC notice formatting.

## Control flow
The flags guide runtime behavior: some zones use locking for updates, ftrace-style zones can skip locking for speed, and single-boot lifetime zones are zapped after their old contents are copied.

## State and persistence
The structure bridges persistent memory metadata and runtime-only helpers: physical address, mapping, buffer header, ECC layout, old-log copy, and type/label.

## Dependencies and integration points
It depends on `linux/pstore_ram.h`, Reed-Solomon types through included structures, and the pstore type enum.

## Risks and test signals
Risks include caller disagreement about flags, stale old-log pointers, ECC configuration mismatch, and no-lock writes on zones with multiple writers. Test signals are compile coverage for `ram.c`/`ram_core.c`, PRZ lifecycle tests, ftrace no-lock operation, and zap-old behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/ram_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/zone.c -->
# sources/distributed-fs/ceph-client/fs/pstore/zone.c

## Purpose
`zone.c` is an intermediate pstore backend that divides one contiguous storage device into in-memory zones for kmsg, pmsg, console, and ftrace, then flushes those zones to block-like storage.

## Important APIs, types, and functions
Public APIs are `register_pstore_zone` and `unregister_pstore_zone`. Core structures are `psz_buffer`, `psz_kmsg_header`, `pstore_zone`, and `psz_context`. Important helpers cover zone allocation, recovery, dirty flushing, circular writes, kmsg header read/write, record erase, pstore read/write callbacks, and delayed cleaner work.

## Control flow
Registration validates size/alignment and read/write callbacks, allocates zones in pmsg, console, ftrace, and dmesg order, allocates a dmesg pstore buffer, sets frontend flags, and registers with pstore. Reads lazily recover storage into memory, choosing active kmsg write position from timestamps and preserving old pmsg/console/ftrace buffers. Writes update in-memory circular buffers and attempt immediate flush; panic kmsg writes use `panic_write` if available and then flush dirty zones.

## State and persistence
Persistent state lives in backend storage as per-zone `psz_buffer` headers and data. Runtime state tracks write/read counters, recovered/on-panic atomics, dirty flags, and old buffers for recovered records.

## Dependencies and integration points
It integrates pstore core, pstore/blk or other `pstore_zone_info` providers, delayed work, block-sector alignment, kmsg dump reasons, and pstore ftrace log merging.

## Risks and test signals
Risks include dirty data not flushed before unregister, recovery trusting corrupted metadata, panic-path writes without `panic_write`, broken-zone retry behavior, ftrace per-CPU size division, erase semantics with new data present, and single backend ownership. Test signals include corrupted signatures/datalen, backend `-ENOMSG` injection, panic writes, delayed flush retry, unlink erase, ftrace merge, and all size alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pstore/zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/Kconfig -->
# sources/distributed-fs/ceph-client/fs/qnx4/Kconfig

## Purpose
This Kconfig entry enables read-only QNX4 filesystem support.

## Important APIs, types, and functions
It defines `QNX4FS_FS` as a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`.

## Control flow
When selected, Kbuild can build the `qnx4` module or builtin driver; otherwise the QNX4 VFS code is excluded.

## State and persistence
It controls build-time availability only. Mounted filesystems are read-only and do not persist kernel-side modifications.

## Dependencies and integration points
It integrates with the block layer, buffer-head based reads, and filesystem module aliasing.

## Risks and test signals
Risks are limited to build selection and user expectations: the help text mentions QNX6/RTP even though QNX6 has a separate driver. Test signals are built-in and module builds with block support enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/Makefile -->
# sources/distributed-fs/ceph-client/fs/qnx4/Makefile

## Purpose
The Makefile builds the QNX4 filesystem object from its component source files.

## Important APIs, types, and functions
It maps `CONFIG_QNX4FS_FS` to `qnx4.o`, composed from `inode.o`, `dir.o`, `namei.o`, and `bitmap.o`.

## Control flow
Kbuild links all QNX4 implementation units only when the filesystem is selected.

## State and persistence
No runtime state exists; it defines module composition.

## Dependencies and integration points
It integrates Kconfig selection with VFS filesystem registration code.

## Risks and test signals
Risks are missing object inclusion or stale build naming. Test signals are module and builtin builds plus `modinfo`/filesystem alias availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/qnx4/bitmap.c

## Purpose
`bitmap.c` counts free blocks in the QNX4 allocation bitmap for `statfs`.

## Important APIs, types, and functions
The file provides `qnx4_count_free_blocks`, using `qnx4_sb(sb)->BitMap`, `sb_bread`, and `memweight`.

## Control flow
It reads bitmap blocks beginning at the bitmap inode's first extent, counts zero bits as free blocks across `di_size` bytes, and stops on I/O failure.

## State and persistence
It only reads on-disk bitmap data through buffer heads. No in-memory bitmap cache is maintained beyond the copied bitmap inode in superblock info.

## Dependencies and integration points
It depends on QNX4 superblock state, block-size constants, buffer heads, little-endian fields, and `qnx4_statfs`.

## Risks and test signals
Risks include trusting bitmap inode size/extent fields, partial counts after I/O errors, and mismatch between bits and real block count. Test signals include `statfs` on valid images, corrupt bitmap extent, short bitmap size, and I/O-error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/dir.c -->
# sources/distributed-fs/ceph-client/fs/qnx4/dir.c

## Purpose
`dir.c` implements QNX4 directory iteration.

## Important APIs, types, and functions
The main function is `qnx4_readdir`; exported operation tables are `qnx4_dir_operations` and `qnx4_dir_inode_operations`.

## Control flow
`qnx4_readdir` maps each directory file block through `qnx4_block_map`, reads the block, iterates fixed-size directory entries, extracts either direct inode names or link-entry names with `get_entry_fname`, computes inode numbers, and emits entries through `dir_emit`.

## State and persistence
Iteration state is `ctx->pos`. On-disk directories are read-only fixed-size entries; no mutations are performed.

## Dependencies and integration points
It depends on QNX4 inode extents, buffer-head reads, VFS dir context APIs, file lease helpers, and the shared directory-entry union in `qnx4.h`.

## Risks and test signals
Risks include invalid block maps, link-entry inode calculation, malformed status/name bytes, and returning success after read failures. Test signals include short and long link-style names, sparse/corrupt directory extents, interrupted `dir_emit`, and directory position resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/inode.c -->
# sources/distributed-fs/ceph-client/fs/qnx4/inode.c

## Purpose
`inode.c` registers and mounts the read-only QNX4 filesystem, validates the root/bitmap metadata, maps file extents, and instantiates VFS inodes.

## Important APIs, types, and functions
Important functions are `qnx4_fill_super`, `qnx4_checkroot`, `qnx4_iget`, `qnx4_block_map`, `try_extent`, `qnx4_get_block`, `qnx4_statfs`, `qnx4_kill_sb`, and inode cache lifecycle functions.

## Control flow
Mount allocates `qnx4_sb_info`, sets a 512-byte block size, reads block 1 as the superblock, validates the root directory and finds `.bitmap`, loads the root inode, and creates the root dentry. Block mapping first checks the inode's first extent, then follows extent blocks with signature `IamXblk`. `qnx4_iget` reads the raw inode entry, populates mode, ownership, timestamps, size, blocks, and assigns file, directory, or symlink operations.

## State and persistence
The driver is read-only. Runtime state includes the copied bitmap inode, inode cache entries, and raw inode data embedded in `qnx4_inode_info`.

## Dependencies and integration points
It depends on block devices, buffer heads, VFS fs_context/get_tree_bdev, generic block read/bmap helpers, slab inode cache, and QNX4 on-disk structures.

## Risks and test signals
Risks include leaks on early mount failure, extent-chain corruption, `qnx4_block_map` returning `-EIO` as an unsigned block, missing release of bad extent blocks, and strict root bitmap assumptions. Test signals include valid QNX4 images, corrupt root name, missing `.bitmap`, multi-extent files, symlink reads, statfs, remount read-only, and malformed inode modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/namei.c -->
# sources/distributed-fs/ceph-client/fs/qnx4/namei.c

## Purpose
`namei.c` implements QNX4 pathname lookup inside directories.

## Important APIs, types, and functions
Important functions are `qnx4_lookup`, `qnx4_find_entry`, and `qnx4_match`.

## Control flow
Lookup scans the directory block by block using `qnx4_block_map`, compares fixed-size entries with the requested name, handles link entries by resolving the real inode block/index, releases the directory buffer, and returns `d_splice_alias(qnx4_iget(...), dentry)`.

## State and persistence
It reads directory entries only; no dcache-persistent state beyond normal VFS aliasing is created.

## Dependencies and integration points
It depends on QNX4 directory-entry status interpretation from `qnx4.h`, buffer-head reads, VFS dentry lookup, and inode instantiation in `qnx4_iget`.

## Risks and test signals
Risks include entry offset arithmetic, linked-entry inode conversion, malformed names/status bytes, and skipped unreadable blocks hiding entries. Test signals include direct and linked entries, missing names, corrupt blocks, maximum-length names, and lookup/dcache alias behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/qnx4.h -->
# sources/distributed-fs/ceph-client/fs/qnx4/qnx4.h

## Purpose
`qnx4.h` provides private QNX4 filesystem structures, helpers, operation declarations, and directory-entry interpretation.

## Important APIs, types, and functions
It defines `struct qnx4_sb_info`, `struct qnx4_inode_info`, `union qnx4_directory_entry`, inline accessors `qnx4_sb`, `qnx4_i`, `qnx4_raw_inode`, and `get_entry_fname`.

## Control flow
`get_entry_fname` validates the status byte, handles used versus link entries, picks the correct maximum name size, and returns a length-limited name pointer for lookup and readdir.

## State and persistence
The header describes per-superblock and per-inode runtime state, including a copied raw inode and bitmap inode pointer. It has no storage effects itself.

## Dependencies and integration points
It depends on VFS types and `linux/qnx4_fs.h`, and is shared by inode, dir, namei, and bitmap code.

## Risks and test signals
Risks include assumptions about union field layout, status-bit interpretation, name truncation, and stale debug macros. Test signals include compile-time `BUILD_BUG_ON` layout checks, direct/link entries, empty entries, and max-size names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx4/qnx4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/Kconfig -->
# sources/distributed-fs/ceph-client/fs/qnx6/Kconfig

## Purpose
This Kconfig file enables read-only QNX6 filesystem support and optional debug output.

## Important APIs, types, and functions
It defines `QNX6FS_FS`, depending on `BLOCK && CRC32` and selecting `BUFFER_HEAD`, plus `QNX6FS_DEBUG`.

## Control flow
Selecting the filesystem includes the QNX6 module or builtin driver; enabling debug adds verbose diagnostic code through Makefile `ccflags`.

## State and persistence
The file only controls build-time availability. The runtime driver mounts QNX6 read-only.

## Dependencies and integration points
It integrates with the block layer, CRC32 checksum validation, buffer heads, and optional debug instrumentation.

## Risks and test signals
Risks are missing CRC dependency coverage or noisy debug builds. Test signals are module/builtin builds with and without `QNX6FS_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/Makefile -->
# sources/distributed-fs/ceph-client/fs/qnx6/Makefile

## Purpose
The Makefile builds the QNX6 filesystem object and applies optional debug flags.

## Important APIs, types, and functions
It maps `CONFIG_QNX6FS_FS` to `qnx6.o`, composed from `inode.o`, `dir.o`, `namei.o`, and `super_mmi.o`, and adds `-DDEBUG` for `CONFIG_QNX6FS_DEBUG`.

## Control flow
Kbuild links all QNX6 source units only when the filesystem is selected.

## State and persistence
No runtime state exists here.

## Dependencies and integration points
It integrates QNX6 Kconfig symbols with VFS module build output.

## Risks and test signals
Risks include stale comment naming QNX4 and missing source objects. Test signals are normal, debug, module, and builtin builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/dir.c -->
# sources/distributed-fs/ceph-client/fs/qnx6/dir.c

## Purpose
`dir.c` implements QNX6 directory iteration and name lookup, including short names stored in directory entries and long names stored in the special longfile.

## Important APIs, types, and functions
Important functions are `qnx6_readdir`, `qnx6_find_ino`, `qnx6_dir_longfilename`, `qnx6_longname`, `qnx6_long_match`, `qnx6_match`, and `qnx6_lfile_checksum`. It exports `qnx6_dir_operations` and `qnx6_dir_inode_operations`.

## Control flow
Directory folios are read through the file mapping. Readdir aligns `ctx->pos`, walks fixed-size entries, emits short names directly, and resolves long names by reading the longfile block referenced by the directory entry. Lookup starts from the cached `i_dir_start_lookup` page, wraps around the directory, and returns the matching inode number.

## State and persistence
State is read-only. Runtime lookup acceleration stores the last successful page in `qnx6_inode_info.i_dir_start_lookup`; persistent names remain on disk.

## Dependencies and integration points
It depends on folio mapping APIs, QNX6 endian helpers, longfile private inode, VFS dir context, and checksum behavior that differs for `mmi_fs`.

## Risks and test signals
Risks include the `last_entry` byte/entry calculation, long filename folio offset math, checksum warnings not rejecting names, stale lookup hint, and malformed `de_size`. Test signals include short names, long names, MMI and non-MMI checksums, lookup wraparound, interrupted `dir_emit`, and corrupt longfile pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/inode.c -->
# sources/distributed-fs/ceph-client/fs/qnx6/inode.c

## Purpose
`inode.c` registers and mounts the read-only QNX6 filesystem, validates mirrored superblocks, maps indirect block trees, and instantiates VFS inodes.

## Important APIs, types, and functions
Key functions are `qnx6_fill_super`, `qnx6_check_first_superblock`, `qnx6_private_inode`, `qnx6_iget`, `qnx6_block_map`, `qnx6_get_block`, `qnx6_checkroot`, `qnx6_statfs`, `qnx6_parse_param`, and inode cache lifecycle functions.

## Control flow
Mount allocates `qnx6_sb_info`, parses the optional `mmi_fs` flag, reads/checks the active superblock pair, selects the highest serial, sets the real block size and block offset, verifies indirect depth, creates private inodes for the inode table and longfile, instantiates the root inode, and validates `.`/`..`. File block mapping uses direct root pointers plus up to `di_filelevels` of indirect pointer blocks.

## State and persistence
The driver is read-only. Runtime state includes active superblock buffer, endian setting, block offset, pointer-bit width, private inodes, and per-inode direct pointers/file levels.

## Dependencies and integration points
It depends on block devices, CRC32, buffer heads, folios/mpage, VFS fs_context, QNX6 endian wrappers, and optional MMI superblock handling.

## Risks and test signals
Risks include stale `sb1` use after MMI path, unreleased buffer heads on some error paths, indirect pointer corruption, endian detection gaps, block offset mistakes, and unsupported write semantics. Test signals include little- and big-endian images, bootblock and no-bootblock layouts, mirrored superblock serial selection, MMI mount option, deep indirect files, symlinks/special inodes, statfs, and corrupt CRCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/namei.c -->
# sources/distributed-fs/ceph-client/fs/qnx6/namei.c

## Purpose
`namei.c` implements the QNX6 dentry lookup bridge from VFS to directory scanning.

## Important APIs, types, and functions
The file provides `qnx6_lookup`, which calls `qnx6_find_ino` and then `qnx6_iget`.

## Control flow
Lookup rejects names longer than `QNX6_LONG_NAME_MAX`, asks `dir.c` to find the inode number, instantiates the inode when found, and returns it through `d_splice_alias`.

## State and persistence
No persistent state is changed. Dcache aliases and the directory's lookup hint are managed by VFS and `qnx6_find_ino`.

## Dependencies and integration points
It depends on QNX6 directory scanning, VFS dentry aliasing, and inode construction in `qnx6_iget`.

## Risks and test signals
Risks include name length boundary errors, propagating `qnx6_iget` errors only through debug logging, and stale lookup cache in the directory. Test signals include missing names, max-length long names, overlong names, inode read errors, and aliasing hard-linked entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/qnx6.h -->
# sources/distributed-fs/ceph-client/fs/qnx6/qnx6.h

## Purpose
`qnx6.h` defines private QNX6 filesystem state, endian-aware on-disk integer helpers, mount option helpers, and cross-file declarations.

## Important APIs, types, and functions
It defines `__fs16`, `__fs32`, `__fs64`, `struct qnx6_sb_info`, `struct qnx6_inode_info`, accessors `QNX6_SB`/`QNX6_I`, mount-option macros, and conversion helpers `fs16_to_cpu`, `fs32_to_cpu`, `fs64_to_cpu`, plus CPU-to-filesystem variants.

## Control flow
Runtime endianness stored in `s_bytesex` controls every on-disk integer conversion, allowing the same code to read little- and big-endian images.

## State and persistence
The header defines runtime superblock and inode-private state but does not mutate storage.

## Dependencies and integration points
It depends on VFS/pagemap types and `linux/qnx6_fs.h`, and is shared by QNX6 inode, dir, namei, and MMI superblock code.

## Risks and test signals
Risks include missing endian conversions at call sites, mount option bit misuse, and private inode lifetime issues. Test signals include endian-swapped filesystem images, MMI option display, direct/indirect pointer conversions, and compile coverage with debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/qnx6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/super_mmi.c -->
# sources/distributed-fs/ceph-client/fs/qnx6/super_mmi.c

## Purpose
`super_mmi.c` handles QNX6 MMI filesystem superblock layout, where mirrored superblocks have a slightly different structure and fixed offset semantics.

## Important APIs, types, and functions
Important functions are `qnx6_mmi_fill_super` and `qnx6_mmi_copy_sb`.

## Control flow
It reads superblock 1, validates magic and CRC, derives the second superblock location from block count and superblock area, switches to the filesystem block size, rereads superblock 1, reads/checks superblock 2, chooses the newer serial, copies MMI fields into a normal `qnx6_super_block` shape, stores the active buffer in `qnx6_sb_info`, and sets `s_blks_off`.

## State and persistence
It reads mirrored on-disk superblocks and stores the selected active one in runtime superblock state. No writes occur.

## Dependencies and integration points
It depends on buffer heads, CRC32, QNX6 endian helpers, MMI on-disk structures, and `qnx6_fill_super` when the `mmi_fs` mount option is set.

## Risks and test signals
Risks include checksum diagnostic typo, block-size change invalidating buffer heads, serial comparison errors, missing endian detection for MMI, and memory allocation failure for the temporary converted superblock. Test signals include valid MMI images with either mirror active, corrupt magic/checksum in each mirror, alternate block sizes, and mount failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/qnx6/super_mmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/Kconfig -->
# sources/distributed-fs/ceph-client/fs/quota/Kconfig

## Purpose
This Kconfig file defines Linux quota subsystem options, quota control support, legacy and v2 on-disk quota formats, netlink notifications, and debug checks.

## Important APIs, types, and functions
It defines `QUOTA`, `QUOTA_NETLINK_INTERFACE`, `PRINT_QUOTA_WARNING`, `QUOTA_DEBUG`, `QUOTA_TREE`, `QFMT_V1`, `QFMT_V2`, and `QUOTACTL`.

## Control flow
Enabling `QUOTA` selects `QUOTACTL`; selecting v2 quota format selects `QUOTA_TREE`; netlink warnings depend on `QUOTACTL && NET`; obsolete console warnings are gated behind `BROKEN`.

## State and persistence
The file controls compiled quota capability and supported on-disk quota formats. Runtime quota state is implemented in the quota source files built by the Makefile.

## Dependencies and integration points
It integrates VFS quota operations, supported filesystems, netlink warning delivery, and quota userspace ABI support.

## Risks and test signals
Risks include missing support for needed quota formats, unexpected omission of netlink warning support, and confusion with filesystems that use independent quota systems. Test signals include builds with quota disabled, v1 only, v2 with quota tree, netlink enabled/disabled, and quota debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/Makefile -->
# sources/distributed-fs/ceph-client/fs/quota/Makefile

## Purpose
The quota Makefile maps quota Kconfig symbols to subsystem object files.

## Important APIs, types, and functions
It builds `dquot.o` for `CONFIG_QUOTA`, old and v2 format handlers for `QFMT_V1`/`QFMT_V2`, `quota_tree.o`, quota syscall/control helpers `quota.o` and `kqid.o`, and optional `netlink.o`.

## Control flow
Kbuild composes the quota subsystem according to selected features.

## State and persistence
No runtime state exists here; build composition determines which quota formats and notification paths are available.

## Dependencies and integration points
It integrates VFS quota core, quota format handlers, quota tree support, quotactl ABI, kernel quota IDs, and netlink warnings.

## Risks and test signals
Risks include object omission for selected symbols or link dependency drift between `QFMT_V2` and `QUOTA_TREE`. Test signals are all quota configuration combinations and module/builtin link tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/compat.h -->
# sources/distributed-fs/ceph-client/fs/quota/compat.h

## Purpose
`compat.h` defines 32-bit userspace compatibility layouts for quota ioctl data structures.

## Important APIs, types, and functions
It declares `struct compat_if_dqblk`, `struct compat_fs_qfilestat`, and `struct compat_fs_quota_stat` using `compat_*` fixed ABI types.

## Control flow
There are no functions; quota compat ioctl handlers include these definitions when translating between 32-bit userspace structures and native kernel quota structures.

## State and persistence
The header has no runtime state. It preserves ABI layout compatibility for quota state exchanged with userspace.

## Dependencies and integration points
It depends on `linux/compat.h` and integrates with quota ioctl compatibility code and filesystem quota stat reporting.

## Risks and test signals
Risks include field layout drift from userspace ABI, signedness/width mismatches, and missing fields compared with native structures. Test signals include 32-bit quotactl tests on a 64-bit kernel, structure size/layout checks, and quota stat/block limit round trips with large values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/compat.h -->
