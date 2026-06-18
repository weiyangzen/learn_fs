# Group Research: group_584_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__8bf8681e5b8f

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock_impl.h

This header defines the private in-kernel implementation structures and macros for illumos file/record locking. It is not the public `flock` API; it describes the local lock manager’s graph model, lock lifecycle, dependency tracking, and process-level deadlock detection support.

Key structures:
- `edge_t` models dependency edges between lock descriptors, with both adjacency and incoming-edge list links.
- `lock_descriptor_t` represents an active, sleeping, granted, interrupted, cancelled, or dead lock request. It stores vnode, range, original `flock64_t`, owner/process metadata, NLM state, zone, optional OFD-style file reference, callback hooks, graph links, and wait condition variable.
- `graph_t` owns per-hash-bucket lock state: a mutex, circular active/sleeping lock lists, graph index, and traversal mark.
- `proc_vertex_t`, `proc_edge_t`, and `proc_graph_t` model process dependency graphs used for deadlock detection across lock owners.

Important constants and state:
- `FLK_INITIAL_STATE` through `FLK_DEAD_STATE` define the lock lifecycle. The comment documents allowed transitions and the functions or wakeups responsible for each transition.
- Legacy `l_state` bit flags include `ACTIVE_LOCK`, `SLEEPING_LOCK`, `IO_LOCK`, `QUERY_LOCK`, `LOCKMGR_LOCK`, `PXFS_LOCK`, and `NBMAND_LOCK`.
- `HASH_SIZE` is 32, and `HASH_INDEX(vp)` hashes vnodes into lock graphs.
- `PXFS_LOCK_BLOCKED` is a special `reclock()` result for blocking PXFS lock requests.

Core macros:
- Owner/range tests include `SAME_OWNER`, `PROC_SAME_OWNER`, `OVERLAP`, `BLOCKS`, and `COVERS`.
- Status predicates include `IS_ACTIVE`, `IS_SLEEPING`, `IS_GRANTED`, `IS_INTERRUPTED`, `IS_CANCELLED`, and `IS_DEAD`.
- Queue/list macros manipulate active/sleeping lists and graph edge lists.
- Wakeup macros `GRANT_WAKEUP`, `CANCEL_WAKEUP`, and `INTERRUPT_WAKEUP` update status bits and signal waiters, except for PXFS locks, which do not sleep in the local lock manager.
- `COPY` copies selected lock request fields, including graph, vnode, type, byte range, flock payload, zone, and process vertex.

External interface:
- Exposes internal lock graph state through `lock_graph[HASH_SIZE]` and `flk_edge_cache`.
- Declares lock-manager routines used by PXFS: `flk_execute_request`, `flk_cancel_sleeping_lock`, `flk_set_state`, and `flk_get_lock_graph`.
- Declares `cl_flk_state_transition_notify()`, a weak-stub style callback for the PXFS server module.
- Declares global `pgraph`.

Dependencies and relationships:
- The file bridges local vnode byte-range locking, NFS/NLM state, PXFS cluster locking, and process-level deadlock detection.
- `l_ofd` participates in ownership identity, so OFD-style locks are distinguished even with the same pid/sysid.
- Many definitions are tightly coupled to `flock.c` and private lock manager invariants.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/flock_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/fs/zfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/fs/zfs.h

This header defines ZFS Fault Management Architecture event class names and payload member names. It contains constants only; there are no structures or functions.

Primary class:
- `ZFS_ERROR_CLASS` is `"fs.zfs"`.

Ereport subclasses:
- General ZFS error reports include checksum, authentication, I/O, data, delay, zpool, I/O failure, probe failure, log replay, and config-cache write failures.
- Vdev-specific reports include unknown device, open failure, corrupt data, no replicas, bad GUID sum, too small, bad label, and bad ashift.

Payload names:
- Pool metadata: pool name/id, failmode, GUID, and pool context.
- Vdev metadata: GUID, type, path, devid, FRU, state, ashift, and delay counters.
- Parent vdev metadata: parent GUID, type, path, and devid.
- ZIO location/error metadata: objset, object, level, block id, errno, offset, and size.
- Checksum diagnostics: expected/actual checksum, algorithm, byteswap flag, bad offset range data, set/clear histograms, and bit counters.

Other constants:
- Failmode values are `"wait"`, `"continue"`, and `"panic"`.
- Resource event names include removed, autoreplace, and statechange.

Dependencies and relationships:
- Used by ZFS kernel/userland FMA producers and consumers to agree on nvlist field names and event class suffixes.
- Complements `sys/fm/protocol.h`, which defines generic FMA event and FMRI field names.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/fs/zfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/ddi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/ddi.h

This header defines DDI/device-driver Fault Management Architecture class and payload strings for I/O and driver defect reporting.

Primary constants:
- `DDI_DVR_MAX_CLASS` is 32.
- `DDI_IO_CLASS` is `"io"`.

Device ereport classes:
- Generic device errors include invalid state, no response, stall, bad interrupt limit, internal correctable/uncorrectable errors, firmware corrupt, and firmware mismatch.
- Service impact classes include lost, degraded, restored, and unaffected.
- Generic NIC event support includes `DDI_FM_NIC`, `DDI_FM_TXR_ERROR`, and valid TX ring error values such as whitelist, not supported, over temperature, hardware failure, and unknown.

Driver defect reporting:
- Driver defect prefix is `DVR_ERPT` (`"ddi."`).
- Defect suffixes describe invalid context, invalid semantics, bad FM capability, and invalid structure version.
- Payload fields include driver name, stack, stack depth, and driver-specific error data.

Dependencies and relationships:
- This is a naming-contract header for FMA nvlist producers and consumers.
- Driver code can include it to emit class/payload names without hard-coded strings.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/ddi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/disk.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/disk.h

This small header defines disk-related FMA fault class names.

Primary class:
- `DISK_ERROR_CLASS` is `"io.disk"`.

Fault classes:
- `FM_FAULT_DISK_PREDFAIL` for predictive failure.
- `FM_FAULT_DISK_OVERTEMP` for over-temperature.
- `FM_FAULT_DISK_TESTFAIL` for self-test failure.
- `FM_FAULT_SSM_WEAROUT` for solid-state media wearout.

Dependencies and relationships:
- Complements SCSI transport ereports in `sys/fm/io/scsi.h`.
- Used by disk diagnosis/reporting components to classify diagnosed disk faults.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/opl_mc_fm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/opl_mc_fm.h

This header defines FMA class and payload names for OPL memory-controller events.

Event classes:
- Base class is `MC_OPL_ERROR_CLASS` (`"asic.mac"`).
- Subclasses include `"ptrl"` and `"mi"`.
- Ereport definitions cover UE, CE, ICE, CMPE, MUE, and SUE.

Payload names:
- Board, bank, status, error address, error log, syndrome, DIMM slot, DRAM location, physical address, and fault type.
- Resource name is `"resource"`.
- `MC_OPL_NO_UNUM` is an empty string for absent unum data.

Dependencies and relationships:
- This is a platform-specific FMA protocol header for OPL memory hardware.
- It is a string-contract header, not an implementation header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/opl_mc_fm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/pci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/pci.h

This header defines PCI, PCI-X, and PCI Express FMA event subclass and payload names.

PCI event names:
- Base subclasses include `"pci"` and secondary `"sec"`.
- Common PCI events cover parity, SERR, master abort, target abort, delayed transaction timeout, target errors, and not responding.
- Payload fields include PCI status, command, secondary status, bridge control, and physical address.

PCI-X event names:
- Subclasses include `"pcix"` and secondary prefix `"sec-"`.
- Events cover ECC correctable/uncorrectable address/attribute/data errors, split transaction messages, split disabled/delayed/outstanding, and unexpected split.
- Payload fields include PCI-X status/command, bridge status, ECC control/status, and ECC attributes.

PCI Express event names:
- Base subclass is `"pciex"`.
- Events are grouped by physical/link/transaction/root-complex/bridge domains, including receiver/transition errors, bad DLLP/TLP, replay timeout, completion abort/timeout, ECRC, flow control protocol, malformed TLP, poisoned TLP, unsupported request, root-complex messages, and bridge secondary errors.
- Severity/class strings include correctable, fatal, nonfatal, no advertised error, and advisory nonfatal.
- Payload fields include device/link/root status, correctable/uncorrectable error status, severity, source id/validity, advanced control, and captured header dwords.

Other constants:
- `PCIEX_FABRIC` names a common fabric class.

Dependencies and relationships:
- Used by PCI bus nexus and device fault-management code.
- Complements platform-specific PCI headers such as `sun4_fire.h` and `sun4upci.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/pci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/scsi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/scsi.h

This header defines SCSI disk-transport FMA ereport names and payload fields.

Primary classes:
- `SCSI_ERROR_CLASS` is `"io.scsi"`.
- `SCSI_DISK_CLASS` is `"disk"`.

Ereport types:
- Predictive failure with ASC/ASCQ payload fields.
- Over-temperature with current and threshold temperature payload fields.
- Solid-state media wearout with current and threshold wearout fields.
- Self-test failure with result code, address, timestamp, and segment fields.

Dependencies and relationships:
- Intended for userland disk-transport modules reporting disk-originated SCSI errors.
- Complements diagnosed disk fault names in `sys/fm/io/disk.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/scsi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4_fire.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4_fire.h

This header defines FMA event and payload names for sun4 Fire/Oberon PCI Express platform components.

Top-level platform names:
- `PCIEX_FIRE` is `"fire"`.
- `PCIEX_OBERON` is `"oberon"`.

Ereport domains:
- JBC errors for JBus bridge conditions such as parity, timeout, illegal access, unsolicited read/interrupt, and EBus timeout.
- UBC errors for Oberon DMA/memory/PIO read/write UE/AXA cases.
- DMC errors for MSI, message, event queue, bypass, translation, TTE, TBW, and TTC failures.
- PEC errors for internal header buffers, unsupported/completion/protocol conditions, link state changes, PCIe transaction/link errors, and uncorrectable buffer/header/data cases.

Payload fields:
- Primary-error marker.
- PEC payload register fields for ILU and TLU error log/status/enable/capture headers.
- DMC payload fields for IMU/MMU register state and fault address/status.
- JBC payload fields for DMC/JBus register state and logs.
- UBC payload fields for error logs, unum/resource, device id, and CPU vector.

Dependencies and relationships:
- Platform-specific supplement to generic PCIe FMA names in `sys/fm/io/pci.h`.
- Used by Fire/Oberon nexus fault-reporting code to keep emitted nvlist names stable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4_fire.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4upci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4upci.h

This header defines FMA event and payload names for sun4u PCI host bridges and related interconnects.

Platform/device class names:
- PCI host bridge families include Psycho (`"psy"`), Schizo (`"sch"`), Tomatillo (`"tom"`), and XMITS.

Ereport classes:
- PBM errors include target timeout, retry limit, secondary master/target/parity cases, and target-side PBM errors.
- Schizo/Tomatillo errors include MMU, bus unusable, slot lock, streaming buffer, and Tomatillo MMU bad/protection/invalid/timeout/UE cases.
- Psycho-specific class includes streaming buffer error.
- ECC memory errors distinguish DMA read/write and PIO UE/CE cases, including secondary variants.
- Safari events cover parity, unmapped/timeout/bus/status errors, bad commands, SSM disabled, PLL, queue timeouts, and CPU parity/bidi cases.
- JBus events cover parity, illegal byte/coherence, snoop errors, bad command, unmapped, timeout, bus, and PCI-related snoop cases.

Payload fields:
- PBM register/log fields.
- IOMMU control and fault address fields.
- ECC error state, syndrome, type, disposition, unum, and memory resource.
- Safari register/log/resource fields.
- JBus register/log/resource fields.

Dependencies and relationships:
- Platform-specific FMA protocol header for older SPARC PCI platforms.
- Complements generic PCI FMA naming in `sys/fm/io/pci.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4upci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/protocol.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/protocol.h

This header defines the generic illumos Fault Management Architecture event protocol: common nvlist member names, class categories, FMRI schemes, event versions, ENA format helpers, and constructor prototypes.

Common event fields:
- Common names include `class` and `version`.
- Category classes include ereport, fault, defect, resource, list, and ireport.
- List event class names include suspect, isolated, repaired, updated, and resolved.

Ereport/list/fault/resource payload names:
- Ereports use detector and ENA.
- Ireports use detector, UUID, priority, and attributes.
- Suspect/list events use UUID, diagnosis code/time, diagnosis engine, fault list, status bits, injected marker, message, retire/response/severity.
- Fault events use ASRU, FRU, FRU label, certainty, resource, and location.
- Resource events use resource plus ASRU and transport-specific payload fields.

Status and version constants:
- Version constants are mostly `0`, with CPU scheme using version 1.
- Suspect status bits include faulty, unusable, not present, degraded, repaired, replaced, and acquitted.

ENA support:
- Defines format mask and formats 0, 1, 2.
- Defines bit masks and shifts for generation, id/cpuid, and time fields.
- Declares helpers to generate, increment, decode, and inspect ENAs.

FMRI scheme support:
- Common FMRI fields include authority, scheme, service authority, and facility.
- Authority fields include chassis id, product serial/id, domain, server, and host id.
- Schemes include fmd, dev, hc, svc, cpu, mem, mod, pkg, legacy-hc, zfs, sw, path, and pcie.
- Each scheme has version constants and member names for its specific fields, such as HC lists, device paths, package identifiers, service names, CPU cache data, memory unum/physaddr/offset, module package/name/id, ZFS pool/vdev, software object/site/context, path digraph, and PCIe list elements.

Constructors and utilities:
- Declares nvlist allocator helpers `fm_nva_xcreate`, `fm_nva_xdestroy`, `fm_nvlist_create`, and `fm_nvlist_destroy`.
- Declares setters for ereports, payloads, HC/dev/DE/CPU/mem/ZFS FMRIs, authority, and HC creation.

Dependencies and relationships:
- Includes kernel or userland nvpair headers depending on `_KERNEL`.
- This is the central naming and helper interface used by all specific FMA headers in this group.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/util.h

This header defines shared FMA utility constants and kernel-only ereport transport helpers.

Shared constants:
- `FM_MAX_CLASS` is 100.
- Error channel is `"com.sun:fm:error"`.
- Kernel event publisher is `"fm"`.

Dump-device ereport transport:
- Ereport dump records use `ERPT_MAGIC`.
- Limits include maximum errors, data size, event channel size, and high-water mark.
- `erpt_dump_t` is a fixed-layout header followed by packed native nvlist data. It includes magic, checksum, size, reserved padding, high-resolution time, high-resolution base, and corresponding wall-clock base time.
- Comments emphasize identical representation for 32-bit and 64-bit producers/consumers.

Kernel-only definitions:
- Stack depth and symbol size constants for stack payloads.
- Errorq drain PIL.
- Stack payload field name.
- Externs for `ereport_errorq`, dump buffer, and dump length.
- Function declarations for FM init, nvlist printing, panic/banner, dump/post, stack payload addition, and `is_fm_panic()`.

Dependencies and relationships:
- Includes `sys/nvpair.h` and `sys/errorq.h`.
- Works with `sys/fm/protocol.h` event construction by providing kernel transport, panic, and dump support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/font.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/font.h

This header defines console font data structures and rendering conversion interfaces.

Font maps:
- `enum vfnt_map` distinguishes normal, normal right-hand, bold, bold right-hand, and map count.
- `font_map` maps source glyphs to target glyph ranges.
- `font_info` is a fixed-size boot-passed summary containing checksum, dimensions, bitmap size, and per-map counts.

In-memory font structures:
- `struct font` holds four mapping tables, bitmap bytes, glyph width/height, and map counts.
- `bitmap_data_t` describes bitmap dimensions, compressed/uncompressed size, compressed data pointer, and associated `struct font`.
- `FONT_FLAGS` indicates whether a font was auto-loaded, manually loaded, passed by bootloader, built in, or marked for reload.
- `struct fontlist` stores a named font, flag, data pointer, loader callback, and STAILQ linkage.

File format:
- `FONT_HEADER_MAGIC` is `"VFNT0002"`.
- `struct font_header` is packed and contains magic, glyph dimensions, glyph count, and four map counts.

Globals and defaults:
- `fonts` is the global font list.
- SPARC defaults to `font_data_12x22`; other platforms default to `font_data_8x16`.
- `BORDER_PIXELS` defines console border spacing.

Functions:
- Reset font flags, select a font, look up a glyph, and convert font bitmap data to 4/8/16/24/32-bit pixel buffers.

Dependencies and relationships:
- Used by console/framebuffer code and boot handoff paths.
- The bootloader-passed format avoids pointer-size assumptions by copying fixed-size metadata and byte arrays.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/font.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fork.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fork.h

This header declares extended fork interfaces and flags visible outside strict POSIX/XOPEN profiles.

Interfaces:
- Userland declarations for `forkx(int)`, `forkallx(int)`, and `vforkx(int)`.
- `vforkx()` is annotated as returning twice.

Flags:
- `FORK_NOSIGCHLD` prevents SIGCHLD delivery to the parent when the child terminates, while still allowing job-control stop/continue notifications when requested.
- `FORK_WAITPID` requires reaping by a specific wait on the child PID and blocks wait-for-any or wait-for-process-group reaping. It also prevents automatic reaping from ignored SIGCHLD disposition.

Dependencies and relationships:
- `fork()`, `forkall()`, and `vfork()` are documented as equivalent to the corresponding `*x()` calls with zero flags.
- Definitions are hidden when strict XOPEN/POSIX profile rules exclude extensions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fork.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/autofs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/autofs.h

This header defines kernel autofs mount/node state plus the shared door/syscall interface used between the kernel and automount daemon.

Kernel mount state:
- `fninfo_t` is per-autofs-mount metadata: mount/root vnodes, RPC netconfig/address, mount path, map/subdir/key/options strings and lengths, refcount, flags, timeouts, and zone id.

Kernel node state:
- `fnnode_t` is the autofs inode equivalent. It stores name/symlink, mode/uid/gid/link count, error, node id, directory offset/size, vnode, parent/sibling/child/trigger links, action list, credential for user-relative matching, locks, timestamps, mount condition variable, traversal tracking (`fn_seen`, `fn_thread`), and global pointer.
- `autofs_globals` stores root node, node count, unmount-thread state, verbosity, zone id, daemon pid, daemon door lock, and door handle.

Locking model:
- `fn_lock` protects most per-node fields.
- `fn_rwlock` protects directory/list traversal and fields such as `fn_dirents`, `fn_next`, `fn_size`, and `fn_linkcnt`.
- Lock ordering is `fn_rwlock` before `fn_lock`.

Flags:
- `MF_INPROG`, `MF_WAITING`, `MF_LOOKUP`, `MF_ATTR_WAIT`, `MF_IK_MOUNT`, `MF_DIRECT`, `MF_TRIGGER`, `MF_THISUID_MATCH_RQD`, and `MF_MOUNTPOINT` encode ongoing daemon operations, mount style, trigger/user-relative semantics, and mountpoint state.
- `AUTOFS_MODE` and `AUTOFS_BLOCKSIZE` define default mode/block size.

Kernel helpers:
- Search, enter, make/free/disconnect nodes, wait for mounts, call daemon, trigger lookup/mount threads, unmount subtrees, shutdown zones, and logging/debug helpers.
- `AUTOFS_BLOCK_OTHERS` and `AUTOFS_UNBLOCK_OTHERS` synchronize mount/lookup operations on a node.

Door/shared ABI:
- Command ids include null, mount, unmount, readdir, lookup, srvinfo, and mntinfo.
- `autofs_door_args_t` and `autofs_door_res_t` carry command plus XDR-encoded argument/result buffers.
- Security data structures include DES and GSS client data.
- `RESTRICTED_MNTOPTS` lists mount options inherited under the `restrict` option.

Syscall:
- `enum autofssys_op` defines unmount-all and set-door operations.
- Kernel declares `autofssys()`.

Dependencies and relationships:
- Ties VFS/vnode state, RPC/XDR protocol structures, doors, zones, and automount daemon communication.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/autofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/bootfs_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/bootfs_impl.h

This private header defines the in-kernel bootfs data structures.

Node model:
- `bootfs_node_t` is the filesystem-specific vnode data for bootfs.
- It stores entry name, vnode, AVL tree of directory entries, AVL/list linkage, physical-memory address, size, parent pointer, and attributes.
- The file comments state bootfs is read-only and node contents are immutable, so node locking is unnecessary.

Filesystem state:
- `bootfs_stat_t` exposes kstat counters for files, directories, bytes, duplicates, and discards.
- `bootfs_t` stores VFS pointer, mount path, root node, kstat pointer, all-node list, minor number, inode count, and stats.

Functions and globals:
- Construction/destruction for `bootfs_t`.
- Node cache constructor/destructor.
- Vnode operations table and template.
- Externs for node cache and bootfs major number.

Dependencies and relationships:
- Uses AVL for directory contents and list linkage for all-node tracking.
- Designed for a persistent-memory boot filesystem presented through vnode/VFS interfaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/bootfs_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/decomp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/decomp.h

This header defines a generic compressed-file header format and kernel decompression vnode wrapper state.

Compressed header:
- Magic values distinguish ZLIB and GZIP.
- Version is `CH_VERSION` 1.
- Algorithm id `CH_ALG_ZLIB` is 1.
- `struct comphdr` contains magic, version, algorithm, uncompressed file size, block size, and a variable-length block map.

Utility macro:
- `ZMAXBUF(n)` estimates the maximum compressed buffer size for zlib-style output.

Kernel decompression node:
- `struct dcnode` links a wrapper vnode to a backing vnode.
- Stores a buffer cache, lock, hash/LRU links, parsed compression header, header size, maximum zlib buffer size, and mapping count.
- Conversion macros map vnode to dcnode and dcnode to vnode.

Kernel API:
- `decompvp()` returns a decompression vnode wrapping a supplied vnode with credentials and caller context.

Dependencies and relationships:
- Provides decompression support as a vnode layer, not as a standalone filesystem.
- The block map in `comphdr` allows random access to compressed blocks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/decomp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/dv_node.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/dv_node.h

This header defines devfs vnode-private `dv_node` structures and helper interfaces.

Node model:
- `dvnode_t` represents device filesystem nodes: directories for nexus drivers and character/block device nodes for devices.
- Fields include name/length, vnode, contents rwlock, underlying `dev_info_t`, parent pointer, AVL directory entries, AVL link, persistent attribute vnode, in-memory attributes, fake inode, flags, link count, busy count, device policy, default mode, and linked sdev node state.

Locking:
- `dv_contents` protects mutable directory/device fields below it and must be held for read before inspection and write before modification.

Flags and defaults:
- Node flags include out-of-date directory, ignore filesystem permissions, internal node, ACL present, and default mode set.
- Root inode is 2.
- Default uid/gid/modes are defined for directories and devices.
- Cleaning flags include force, reset permissions, and directory-lock-held.

Filesystem state:
- `devfs_data` stores root devfs node and VFS pointer.
- `dv_fid` overlays VFS fid for `VFS_VGET`.

Attribute macros:
- Compare and merge minor permissions (`mperm_t`) with vnode attributes.
- Shadow-node flags control creation and whether `dv_contents` is already write-held.

Traversal/helpers:
- AVL traversal macros expose first/next directory entry.
- Externs declare node cache init/fini, mkdir/root/create/destroy/insert/shadow/find/fill/clean/walk, devfs lookups, policy lookup, permission reset, remove-driver cleanup, and vnode ops.

Debugging:
- DEBUG builds expose `devfs_debug` flags and conditional printf-style macros.

Dependencies and relationships:
- Includes `sdev_impl.h`, tying legacy devfs and dynamic `/dev` support together.
- Uses device policy and devinfo holds to connect filesystem entries to device tree state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/dv_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/fifonode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/fifonode.h

This header defines FIFOFS/pipe vnode-private data, flags, and kernel interfaces.

Locking:
- `fifolock_t` contains the primary FIFO mutex, reference count, open/close sync flag, condition variable, and padding.
- Comments document fields protected by `flk_lock`, including message queues, counts, flags, open/read/write counts, timestamps, sync counters, and lock ref/sync state.
- FIFO allocation list linkage is protected separately by the ftable lock.

Node model:
- `fifonode_t` stores vnode, real shadowed vnode, pipe inode, peer pipe end, message queue head/tail, shared FIFO lock, byte count, wait condition, writer/reader/open/sync/wait counts, timestamps, list linkage, peer credential/pid, sync state, and flags.
- `fifodata_t` bundles one shared `fifolock_t` and two `fifonode_t` objects for pipe pairs.

Flags:
- Include pipe/send-end/open/close/connld/fast-mode states, reader/writer wait flags, signal/poll/high-water/read-write-busy states, open/read/write occurred markers, band polling, stay-fast, and wait-for-mode-change.
- High/low water marks are `16 KiB` and `0`.

Conversions:
- `VTOF` maps vnode to fifonode.
- `FTOV` maps fifonode to vnode.

Kernel interfaces:
- Vnode ops/template, fnode and pipe caches.
- Initialization, stream/open/close/cleanup/remove, id allocation, vnode conversion, pipe creation, fast flush/mode transitions, stream info, and reader/writer wakeups.
- `Fifohiwat` is tunable only under `FIFODEBUG`; otherwise it aliases the constant.

Dependencies and relationships:
- FIFOFS can operate in a fast internal mode or transition to STREAMS mode.
- Supports both named FIFOs shadowing real filesystem nodes and anonymous pipes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/fifonode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_impl.h

This header declares internal High Sierra/ISO filesystem routines and globals.

Core routines:
- Page writeback helper `hsfs_putapage()`.
- Sector read helper `hs_readsector()`.
- Node construction/reconstruction from directory entries and disk locations.
- Directory lookup and hash lookup.
- Node free and hash synchronization.
- Directory parsing and directory entry filling.
- Name conversion for ISO/High Sierra, Joliet, and uppercase handling.
- Access checks and date parsing.
- Bogus-disk warning logging and directory validation.
- hsnode cache init/fini.

Globals:
- Vnode ops template and vnode ops pointer.
- Mount table lock and mount table list head.

Dependencies and relationships:
- Depends on structures declared in HSFS node/specification headers.
- Serves as the internal function declaration hub for HSFS implementation files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_isospec.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_isospec.h

This header defines ISO 9660 on-disk layout constants and byte-offset accessor macros.

Integer parsing:
- `ZERO` through `THREE`, `MSB_INT`, `LSB_INT`, `MSB_SHORT`, and `LSB_SHORT` parse multi-byte fields.
- `BOTH_SHORT` and `BOTH_INT` use native direct loads on x86/amd64, but bytewise little-endian extraction on SPARC to avoid unaligned access issues.

Volume descriptor:
- ISO sector size is 2048 bytes, with volume descriptors starting at sector 16.
- Volume descriptor types include boot, primary, supplementary, partition, UNIX extension, and end-of-volume.
- Defines ISO identifier string `"CD001"`, version values, string lengths, and date lengths.
- Provides address and value macros for descriptor fields such as type, standard id/version, system/volume ids, volume size, supplementary escape, set size/sequence, block size, path table locations, root directory, publisher/preparer/application/copyright/abstract/bibliographic ids, timestamps, and file structure version.

Directory records:
- Defines fixed directory-entry sizes and maximum name lengths.
- Provides address/value macros for directory length, XAR length, extent LBN/size, creation date, flags, interleave data, volume set, name length/name, system use area, padding, and SUA length.
- Defines directory flags and prohibited flag combinations.
- Provides date field macros and tests for regular files/directories.

Filename limits:
- ISO v1/v2 and Joliet name length constants are defined, including implementation maxima.

Path table:
- Defines fixed path-table entry size and accessor macros for name length, XAR length, extent LBN, parent number, and name.

Dependencies and relationships:
- Uses macro-based byte offsets instead of C structs to represent unaligned portable disc data.
- Works with HSFS parser code and SUSP/RRIP handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_isospec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_node.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_node.h

This header defines HSFS in-core node, volume, mount, fid, and I/O scheduling state.

Directory entry abstraction:
- `hs_direntry` normalizes on-disk directory data into extent location/size, timestamps, vnode type, mode, link count, owner/group, inode, device number, XAR metadata, interleave fields, and symlink data.

Path table structures:
- `ptable` stores path-table entry name data.
- `ptable_idx` links a directory’s path-table entry to its parent and child range.

Node model:
- `hsnode` is the in-core file node, with hash/free list links, vnode pointer, cached directory entry, node id, directory entry disk location, path-table index, directory search offset, page mapping count, sequence, flags, read-ahead state, and contents lock.
- Node ids use the starting extent for directories and usually files, with `HS_DUMMY_INO` used for empty files.

Volume and mount:
- `hs_volume` is immutable after initialization and contains volume size, logical-block size/shift data, file structure version, default uid/gid/protection, creation/modification times, root dir entry, path table location/length, volume set data, and volume id.
- `hsfs` contains mount-list linkage, magic, VFS/root/device vnodes, volume type, parsed volume, path tables, extension flags, SUA offset, name-length limits, error flags, mount name/options, hsnode hash/free lists, kstat counters, and I/O scheduling queue.

I/O scheduling:
- `hio` represents a read request in AVL trees ordered by offset and deadline.
- `hio_info` tracks read-ahead request buffers, virtual addresses, semaphores, pages, and filesystem pointer.
- `hsfs_queue` stores circular-look scheduling state, preallocated coalescing buffer, locks, offset/deadline AVL trees, read-ahead taskq, max read-ahead, and device max transfer.

Constants/macros:
- Volume types include High Sierra, ISO, ISO v2, and Joliet.
- Error bit offsets track nonconformant media cases such as lower-case names, bad root dir, unsupported type, bad file lengths, and bad SUA length.
- Conversion macros map VFS/vnode to HSFS/hsnode and convert logical blocks, sectors, and byte offsets.

Dependencies and relationships:
- This is the central in-core state header for HSFS.
- Paired with `hsfs_spec.h`, `hsfs_isospec.h`, `hsfs_susp.h`, and `hsfs_rrip.h` for on-disk parsing and extensions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_rrip.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_rrip.h

This header defines Rock Ridge Interchange Protocol support constants, byte-offset macros, and parser prototypes for HSFS.

Mount flags:
- HSFS-specific flags disable RRIP, trailing-dot handling, lowercase mapping, trailing-space handling, ISO version info, Joliet, Joliet truncation, ISO-9660:1999, or enable inode behavior for newer mkisofs images.
- `MS_NO_RRIP` is retained as a legacy generic mount flag but comments mark it as deprecated in favor of `HSFSMNT_NORRIP`.

RRIP identity:
- Version constants are all 1.
- Extension id is `"RRIP_1991A"`, with fixed descriptive/source strings.
- `IS_RRIP_IMPLEMENTED(fsp)` tests implementation state through SUSP extension bits.

Signatures:
- RRIP SUSP signatures include `CL`, `NM`, `PL`, `PN`, `PX`, `RE`, `RR`, `SL`, and `TF`.

Time fields:
- `TF` macros parse flags and locate creation, modification, access, and attribute timestamps.
- Time flags distinguish creation, modify, access, attributes, backup, expiration, effective, and long-time format.
- `IS_TIME_BIT_SET` must return 1 or 0 because offset macros sum bit-presence results.

POSIX metadata:
- `PX` macros parse mode, link count, uid, gid, and inode.
- `PN` macros parse major/minor device numbers.

Name and symlink handling:
- Name flags cover continuation, current, parent, root, volume root, and host.
- Higher-level parser flags record name changed and symlink complete states.
- Max supported RRIP filename length is 255.
- Symbolic-link macros parse SL fields and components.

Directory relocation:
- Defines child-link, parent-link, and relocated-directory flags.
- `CL` and `PL` macros parse child/parent LBNs.

Kernel parser API:
- Declares handlers for RRIP name, file attributes, device nodes, times, symlinks, parent/child links, relocated directories, Rock Ridge record, root-dir checking, and RRIP name copying.

Dependencies and relationships:
- Requires SUSP parsing context (`sig_args_t`) from `hsfs_susp.h`.
- Extends ISO/HSFS directory entries with POSIX semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_rrip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_spec.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_spec.h

This header defines original High Sierra filesystem on-disk layout constants and accessor macros.

Integer parsing:
- Provides the same byte-access and MSB/LSB/BOTH integer macros used by ISO parsing.
- SPARC uses bytewise parsing to avoid unaligned accesses.

Volume descriptor:
- High Sierra sector size is 2048 bytes and volume descriptors start at sector 16.
- Max file offset is 4 GiB minus 1.
- Volume descriptor types include boot, standard file structure, coded character file structure, unspecified, and end-of-volume.
- Identifier string is `"CDROM"`.
- Defines lengths for system/volume/set/publisher/preparer/application/copyright/abstract/date fields.
- Accessor macros cover descriptor LBN, type, standard id/version, system/volume ids, size, set size/sequence, block size, path table locations, root dir, metadata strings, dates, and file structure version.

Path table:
- Defines fixed entry size and accessors for extent LBN, XAR length, name length, parent number, and name.
- SPARC uses MSB parsing for extent LBN; other platforms directly dereference.

Directory records:
- Defines root record/fixed directory/user extension sizes and maximum name length.
- Accessors cover directory length, XAR length, extent LBN/size, creation date, flags, reserved/interleave/volume set, name length/name, and UNIX extension mode/uid/gid.
- Flag definitions mirror ISO style: existence, directory, associated, record, protection, unused, last extent, and prohibited combinations.
- Provides date macros and regular-file/directory tests.

Kernel declarations:
- Date parsing routines are declared under `_KERNEL`.

Dependencies and relationships:
- Represents High Sierra pre-ISO format, while `hsfs_isospec.h` represents ISO 9660.
- HSFS mount code chooses among HS, ISO, ISO v2, and Joliet formats using these layout definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_spec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_susp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_susp.h

This header defines System Use Sharing Protocol support for HSFS, including SUSP field parsing helpers and extension dispatch structures.

Return codes:
- SUSP parser returns negative sentinel codes for null pointer, end of parsing, end of SUA, continuation request, allocation failure, invalid data, and relocated-directory handling.

Extension implementation bits:
- Macros set, clear, and test extension bits in `hsfs_ext_impl`.
- Defined bits include SUSP present and prohibited file/dir type present.
- SUSP-specific macros mark and test whether SUSP is implemented.

SUSP signatures:
- Defines signatures `SP`, `CE`, `PD`, `ER`, and `ST`.
- SUSP version is 1.

System Use Field access:
- Generic SUF macros parse signature length, field length, and version.
- Extension Reference macros parse id/description/source lengths, extension version, and locate extension id/description/source strings.
- Continuation Area macros parse block location, offset, and length.
- Sharing Protocol macros parse check bytes and SUA offset.
- Check bytes are `0xBE` and `0xEF`.

Dispatch structures:
- `ext_signature_t` maps a two-character extension signature to a handler function.
- `extension_name_t` maps extension names and versions to signature tables.
- `cont_info_t` carries continuation area location/offset/length.
- `sig_args_t` bundles arguments passed to signature handlers, including dir entry pointer, name buffer/length, flags, name flags, current SUF pointer, parsed hs_direntry, filesystem pointer, and continuation info.

Kernel declarations:
- Declares handlers for SUSP SP, ER, CE, PD, and ST fields.
- Declares RRIP and SUSP signature tables, extension-name table, SUSP SP pointer, and `parse_sua()`.

Dependencies and relationships:
- Provides the extension dispatch substrate used by RRIP support in `hsfs_rrip.h`.
- Uses ISO/HSFS directory record system-use areas to discover and process filesystem extensions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_susp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_info.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_info.h

This header defines loopback filesystem per-mount and hash-table state.

Hashing:
- `lobucket` holds a per-bucket lock, lnode chain, vnode count, and padding to avoid false sharing.
- `lo_retired_ht` tracks retired hash tables for deferred cleanup.

Mount state:
- `loinfo` stores real VFS, loopback VFS, root vnode, inherited and denied mount flags, outstanding vnode count, volatile hashtable size/table pointer, list of loopback VFS mappings, locks for that list and hash table/retired state, and filesystem behavior flags.
- Inheritable mount flags include readonly, nosetuid, nodevices, xattr, nbmand, and noexec.

Mount options/flags:
- `MNTOPT_LOFS_NOSUB` and `MNTOPT_LOFS_SUB` control submount traversal.
- `LO_NOSUB` provides NFS-server-like lookup semantics where mountpoints are not traversed.

Cross-VFS mapping:
- `lfsnode` records a real VFS/root and a new loopback VFS for real filesystems encountered during loopback namespace traversal.

Conversion:
- `vtoli()` maps VFS to `loinfo`.

Kernel API:
- Functions for resolving real VFS, subsystem init/fini, hashtable setup/destroy, and vnode/vfs operation globals.

Dependencies and relationships:
- Paired with `lofs_node.h`, which defines individual lnodes.
- Handles loopback views that may cross underlying VFS boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_info.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_node.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_node.h

This header defines loopback filesystem per-vnode lnode state.

Node model:
- `lnode_t` stores hash-chain linkage, real vnode pointer, looping flags, and placeholder loopback vnode pointer.
- The lnode is the client-side “inode” for a loopback file.

Flags:
- `LO_LOOPING` indicates detected loopback recursion.
- `LO_AUTOLOOP` indicates autonode loop detection.
- `LOF_FORCE` forces creation of a new lnode when passed to `makelonode()`.

Conversions:
- `ltov()` maps lnode to loopback vnode.
- `vtol()` maps vnode to lnode.
- `realvp()` maps a loopback vnode to the underlying real vnode.

Kernel API:
- `makelonode()` creates or finds an lnode for a real vnode and mount.
- `freelonode()` frees an lnode.

Dependencies and relationships:
- Includes `lofs_info.h` for mount-level state.
- The lnode hash table is managed per mount via `loinfo`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/mntdata.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/mntdata.h

This header defines mntfs node, snapshot, and element structures used to expose mount table data.

Mount elements:
- `mntelem_t` stores list links, birth/death/vfs ctime, reference count, hidden flag, text buffer/size, and parsed `extmnttab` payload.
- Macros test whether an element is alive or dead based on death timestamp.

Snapshots:
- `mntsnap_t` stores snapshot time, last mount-table mtime, first/next element pointers, flags, element count, text size, and read offsets.
- Flags include show-hidden and rewind/refresh requirements.

Node state:
- `mntnode_t` stores vnode, mounted-on vnode, rwlock, node flags, and two snapshots: one for read and one for ioctl.

Filesystem state:
- Kernel `mntdata_t` stores zone reference, open count, cached normal/hidden snapshot sizes and mtimes, and embedded mntnode.

Conversions:
- `VTOM`, `MTOV`, and `MTOD` map between vnode, mntnode, and mount filesystem data.

Kernel API:
- Exposes `mntvnodeops`.
- `mntfs_getmntopts()` formats mount options for a VFS.

Dependencies and relationships:
- Used by mntfs to present `/etc/mnttab`-style data as a filesystem view.
- Supports hidden mounts via `MS_NOMNTTAB`-related snapshot handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/mntdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/namenode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/namenode.h

This header defines NAMEFS structures for mounting file descriptors into the filesystem namespace.

User/kernel ABI:
- `struct namefd` carries a file descriptor from userland to kernel for `fattach()`/NAMEFS use.

Kernel node model:
- `namenode` stores the mounted-file-descriptor vnode, flags, copied attributes, original file vnode, file pointer, original mountpoint vnode, list linkage, and a lock protecting attributes.
- `NMNMNT` indicates a namenode is not mounted.

Hashing:
- `NM_FILEVP_HASH_SIZE` is 64.
- `NM_FILEVP_HASH(vp)` hashes by shifted vnode pointer into `nm_filevp_hash`.

Conversions:
- `VTONM` maps vnode to namenode.
- `NMTOV` maps namenode to vnode.

Kernel API:
- Initialization, unmount-all, insert/remove/find, node number allocation/free, vnode ops/template, table lock.
- `nm_walk_mounts()` walks NAMEFS mounts for a vnode with a callback.

Dependencies and relationships:
- NAMEFS is used by `fattach()` to bind an open file descriptor into a path.
- Stores both the mounted file vnode and the mountpoint vnode to support lookup/unmount behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/namenode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_dir.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_dir.h

This header defines FAT/PCFS directory-entry formats, filename rules, long-filename handling, and directory search result structures.

Short directory entries:
- `PCFNAMESIZE` is 8, `PCFEXTSIZE` is 3, max long name is 255, and long-name chunk size is 13 UTF-16 characters.
- `struct pctime` stores DOS time/date fields.
- Time/date bit shifts and masks decode seconds, minutes, hours, day, month, and year.
- `struct pcdir` is the traditional FAT 8.3 entry with filename, extension, attributes, NT attrs, creation/last access/modify times, starting cluster low/high fields, and file size.

Long filename entries:
- `struct pcdir_lfn` overlays FAT directory entries for VFAT long names.
- It contains ordinal, three UTF-16 name fragments, LFN attribute/type/checksum, and unused cluster field.
- LFN detection requires enabled long filenames, R/H/S/V attributes only, and valid ordinal 1..20.
- The header documents reverse ordering, checksum association with the short name, case-insensitive long-name lookup, and `0xff` padding behavior.

Attributes and name tests:
- FAT attributes include readonly, hidden, system, label, directory, and archive.
- `PCA_IS_HIDDEN` hides labels and hidden/system files unless the mount flag shows them.
- Macros detect dot/dotdot in long and short forms.
- `pc_invalchar` and `pc_validchar` enforce uppercase ASCII 8.3 character restrictions.

Directory search:
- `pcslot` records lookup result status, disk block, offset, buffer, entry pointer, and dot/dotdot flags.
- `pc_dirent` mirrors `dirent64` layout with a 512-byte name buffer for 256 UTF-16 bytes.

Kernel API:
- Time conversion, LFN validation, read/match/extract long/short names, checksum, chunk setting, name conversion, and starting-cluster get/set helpers.
- Private tunable `enable_long_filenames` controls VFAT LFN recognition.

Dependencies and relationships:
- Includes `pc_node.h` after initial structure declarations because directory code depends on PCFS node types and attributes.
- Works with `pc_fs.h` mount state and FAT cluster logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_fs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_fs.h

This header defines PCFS/FAT mount state, boot-sector accessors, validation masks, FAT32 fsinfo, cluster constants, and filesystem helper interfaces.

Design notes:
- PCFS aims to remain mostly stateless except while files are open, allowing removable media changes.
- Disk changes are detected by comparing in-core directory entries with on-disk entries during directory searches.
- Files and directories use separate vnode op vectors and tables.
- FAT32 support introduces 32-bit clusters, non-fixed root directory location, fsinfo maintenance, optional alternate FAT behavior, and chunked FAT reads for large FATs.

Types:
- `pc_cluster16_t` and `pc_cluster32_t` define cluster-width types.
- Legacy `bootsec` and `fat32_bootsec` structs exist for compatibility, but active code uses byte-offset accessors.

Boot-sector access:
- Defines offsets for generic BPB, FAT12/16 extended BPB, and FAT32 extended BPB fields.
- `LE_16_NA` and `LE_32_NA` parse unaligned little-endian fields.
- `bpb_get_*` macros read sector size, sectors per cluster, reserved sectors, FAT count/size, media byte, geometry, hidden/total sectors, signatures, FAT32 root/fsinfo/backup fields, volume ids/labels, and filesystem type strings.

Validation:
- Macros validate sector size, sectors per cluster, cluster size, FAT count, reserved sectors, signatures, media descriptors, volume labels, OEM names, FAT type strings, jump boot instructions, FAT32 version, and extended flags.
- Individual `BPB_*_OK` bits record validation results.
- `FAT12_VALIDMSK`, `FAT16_VALIDMSK`, and `FAT32_VALIDMSK` define required structural checks; FAT32 deliberately does not require a boot signature to tolerate older SYSLINUX overwrites.
- Supported FAT32 FS version is 0.

FAT32 fsinfo:
- `fat_fsi_t` stores free cluster count and next-free search hint.
- `fat_od_fsi_t` models on-disk FAT32 FSI sector signatures and fields.
- `FSISIG_OK` validates lead/structure/trail signatures.
- `FSINFO_UNKNOWN` marks invalid free/next data.

Mount state:
- `struct pcfs` stores VFS, flags, drive, FAT type, device vnode/dev, sector/cluster geometry, FAT/root/data starts, cluster count, active node refs, next free cluster, in-core FAT, FAT changemap, invalidation/verify times, filesystem lock owner/count, fsinfo, mount list link, root vnode, timezone, media size/descriptor, last-cluster marker, root cluster, and root timestamp.
- Flags include FAT modified, locked/wanted, no check, boot partition, show hidden, PCMCIA pseudo floppy, fold case, fsinfo valid, irrecoverable write interference, no clamp time, and no atime.

Cluster and address macros:
- Define reserved/bad/last/free cluster constants for FAT12/16/32.
- Convert between offsets, logical blocks, clusters, disk blocks, and device block addresses.
- Check valid cluster range and directory entries per sector/cluster.

Mount args/options:
- Supports old and current mount arguments with timezone/DST/flags.
- Mount options include hidden/nohidden, foldcase/nofoldcase, clamptime/noclamptime, timezone, and secsize.

Kernel API:
- Lock/unlock filesystem, read/invalidate/sync FAT, count/allocate/set clusters, mark FAT updates, and query FAT-changed map.
- Debug print macros are gated by `pcfsdebuglevel`.

Dependencies and relationships:
- Works closely with `pc_dir.h`, `pc_node.h`, and `pc_label.h`.
- Stores FAT and filesystem layout state needed by vnode operations and directory lookup/update code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_label.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_label.h

This header defines PC master boot block, partition, DOS/FAT identifier, media descriptor, sector-size, and endian conversion constants.

Boot block and partition offsets:
- Defines offsets for BPB fields such as bytes per sector, sectors per cluster, reserved sectors, FAT count, root entries, sector count, media byte, sectors per FAT, geometry, and hidden sectors.
- Partition table starts at `0x1be` with four entries.
- FAT type-string offsets differ for FAT12/16 and FAT32.
- BPB starts at `0xb`; DOS signature is at `0x1fe`.

Partition and FAT identifiers:
- DOS partition system indicators cover FAT12, FAT16, huge FAT16, FAT32, FAT32 LBA, and FAT16 LBA variants.
- Defines maximum sector/cluster thresholds for FAT12.
- Jump opcodes and DOS signature constants are defined.

Media descriptors:
- Includes fixed disk and common floppy media descriptor byte values.
- Comment notes media-descriptor identification is unreliable.
- PC filesystem sector size constant is 512.

Endian helpers:
- On little-endian systems, `ltohs`, `ltohi`, `htols`, and `htoli` direct-reference storage.
- On big-endian systems, helpers assemble values by byte extraction.

Dependencies and relationships:
- Older/low-level companion to `pc_fs.h` BPB parsing.
- Provides partition and media constants used by PCFS mounting and validation paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_label.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_node.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_node.h

This header defines PCFS in-core file/directory node structures and node operation declarations.

FID:
- `pc_fid` overlays VFS fid with length, directory-entry block, directory-entry offset, and creation-time generation approximation.

Node model:
- `pcnode` stores active-list links, flags, vnode, file size, starting cluster, directory-entry disk block/offset, cached directory entry, last visited cluster, and last cluster index.
- File nodes are identified by directory entry block/offset, while directory nodes use starting cluster.

Flags:
- Data modified, node changed, invalid, external vnode reference held, accessed, and release-hold states.

Conversions and node ids:
- `PCTOV` maps pcnode to vnode.
- `VTOPC` maps vnode to pcnode.
- `pc_makenodeid()` makes a pseudo inode: directories use negative cluster-based ids, files use directory-entry position.

Hashing:
- `NPCHASH` is currently 1, so file/directory hash macros collapse to one bucket.
- `pchead` stores linked-list heads.

Kernel API:
- Vnode ops for files and directories plus templates.
- Global file and directory head arrays.
- Node lifecycle, mark modified/accessed, sync/update, block mapping/allocation/free, filesystem verification/disk-change handling, directory lookup/enter/remove/rename, block-at-offset, truncate, file cluster sizing, page writeback, and bad filesystem marking.

Dependencies and relationships:
- Depends on `struct pcdir` from `pc_dir.h` and FAT/mount state from `pc_fs.h`.
- The cached directory entry is central to removable-media change detection.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pxfs_ki.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pxfs_ki.h

This header defines kernel interface stubs for PXFS asynchronous I/O.

Interfaces:
- `clpxfs_aio_write(vnode_t *, struct aio_req *, cred_t *)`.
- `clpxfs_aio_read(vnode_t *, struct aio_req *, cred_t *)`.

Dependencies and relationships:
- Includes VFS, vnode, and AIO request definitions.
- The comments identify these as kernel interface stubs to PXFS routines, specifically for KAIO integration.
- Related to PXFS lock hooks in `flock_impl.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pxfs_ki.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_impl.h

This private header defines the implementation state for the `/dev` filesystem (`sdev`), including dynamic device nodes, profiles, plugin support, devfsadm communication, negative caching, vnode operation selection, and debug support.

Mount/profile ABI:
- `sdev_mountargs` currently carries `sdev_attrdir`.
- Profile nvpair names cover mount point, include, exclude, symlink, and map entries.
- `sdev_door_arg_t` and `sdev_door_res_t` define devfsadm/devname door command/result payloads.
- Supported devfsadm command is run-all; errors include invalid, EPERM, and not supported.

Profile and instance data:
- `sdev_dprof` stores profile nvlists for names, maps, symlinks, and glob include/exclude directories.
- `devname_handle` binds a handle to an `sdev_node` plus callback arguments.
- Global-zone instance data stores a handle and namespace generation.
- Local-zone data stores cached directory/devtree generations, origin global node, and profile.

Node model:
- `sdev_node_t` stores name, length, absolute path, symlink target, vnode, contents rwlock, parent, AVL directory entries/link, backing attribute vnode, in-memory attributes, inode, link count, state, flags, lookup synchronization lock/cv/flags, per-instance global/local union, plugin-list link, and private pointer.
- Node states are zombie, init, and ready.
- Directory traversal macros wrap AVL first/next.
- Conversion/hold/release macros bridge vnode and sdev_node.

Flags:
- Node flags include build/out-of-date, global, persisted, no negative cache, dynamic vnode ops, validate during search, invalid attributes, subdir match, and zoned subdir.
- Lookup flags include lookup in progress, readdir in progress, and waiting for devfsadm.
- Default uid/gid/modes are defined for root, directories, devices, and symlinks.

Filesystem instance:
- `sdev_data` stores mount list links, root node, VFS pointer, mount args, and ACL flavor.
- `sdev_fid` overlays VFS fid with length, inode, and generation.

Synchronization/devfsadm:
- Macros manage devfsadm state: stopped, running, ran once.
- `SDEV_BLOCK_OTHERS`, `SDEV_UNBLOCK_OTHERS`, and lookup-wait helpers coordinate concurrent lookup/readdir/devfsadm actions.
- Boot states progress through initial, reconfig, system available, and complete.

Negative cache:
- `sdev_nc_list_t` stores list, mutex, rwlock, flags, and entry count.
- `sdev_nc_node_t` stores missing-name entries, source flags, expiration count, and list linkage.
- Flags identify dirty/writing/write-enabled lists and active/persistent/current-boot entries.
- Devname-cache nvlist identifiers define persistent cache format.

Vnode/plugin helpers:
- Declares generic lookup/readdir/setattr/inactive helper functions, cache lookup/update, root/node construction, dynamic filldir, node ready/destroy/update, shadowing, stale/cleandir/rename, attribute/default helpers, backstore lookup, profile functions, validators for devpts/devnet/devipnet/devvt/devzvol, and devinfo/modctl helpers.
- `sdev_vop_table_t` maps subdirectory names to vnode ops templates, global vnode-op containers, validators, and flags.
- Plugin lifecycle and node-ready hooks integrate with `sdev_plugin.h`.

Globals:
- Exposes locks, devtype, node cache, vnode ops for base and special subtrees, mount origins, operation tables, negative cache pointer, reconfig and negative-cache tunables, and taskq.

Debugging:
- DEBUG builds expose many per-subsystem debug flags and conditional trace macros, including failed lookup tracing.

Dependencies and relationships:
- This is the main implementation contract for `/dev` dynamic filesystem internals.
- It is used by devfs/sdev vnode operations, devfsadm integration, non-global zone `/dev` profiles, plugin modules, and special dynamic subdirectories.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_plugin.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_plugin.h

This header defines the kernel plugin interface for sdev dynamic `/dev` nodes.

Opaque handles:
- `sdev_plugin_hdl_t` identifies a registered plugin.
- `sdev_ctx_t` identifies an sdev callback context.

Validation results:
- Invalid, skip, valid, and stale outcomes are represented by `sdev_plugin_validate_t`.

Plugin flags:
- `SDEV_PLUGIN_NO_NCACHE` disables negative cache use.
- `SDEV_PLUGIN_SUBDIR` marks plugin handling for subdirectories.
- Valid flags are masked by `SDEV_PLUGIN_FLAGS_MASK`.

Plugin operations:
- `sp_valid_f` validates a context.
- `sp_filldir_f` fills a directory.
- `sp_inactive_f` handles inactive nodes.
- `sdev_plugin_ops_t` stores version, flags, and callbacks.
- Plugin interface version is 1.

Registration and context helpers:
- Register/unregister plugin by name.
- Query context flags, name, path, minor number, vnode type.
- Create directories and special nodes through plugin callbacks.

Dependencies and relationships:
- The implementation side is declared in `sdev_impl.h`.
- Provides a narrow extension interface for modules that populate or validate dynamic `/dev` subtrees.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_plugin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_ioctl.h

This header defines project-private SMBFS ioctl payloads and command numbers.

Payload:
- `ioc_sdbuf_t` describes a user-space security descriptor buffer with address, allocated size, used size, and selector such as DACL security information.

Ioctls:
- `SMBFSIO_GETSD` uses `_IO('f', 81)`.
- `SMBFSIO_SETSD` uses `_IO('f', 82)`.
- Both use `ioc_sdbuf_t` data.

Dependencies and relationships:
- Provides SMBFS-specific get/set security descriptor operations.
- Reuses FS-specific ioctl number space from `sys/filio.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_mount.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_mount.h

This header defines the user/kernel mount argument interface for SMBFS.

Versioning:
- Major version is 1, minor is 3300, combined `SMBFS_VERSION` encodes both.
- Version string is `"1.33"`.
- VFS name is `"smbfs"`.

Mount options and flags:
- Defines ACL/noACL option strings.
- `SMBFS_MF_SOFT`, `SMBFS_MF_INTR`, and `SMBFS_MF_NOAC` control soft mounts, interruptibility, and attribute caching.
- Attribute cache flags mark which min/max file/dir cache times were explicitly set.

Mount argument structures:
- `smbfs_args` carries version, device fd, flags, uid/gid, file/dir modes, and attribute cache min/max values.
- Under `_SYSCALL32`, `smbfs_args32` provides fixed-width 32-bit syscall layout.

Dependencies and relationships:
- Used by `mount_smbfs` and the kernel SMBFS mount path.
- The file’s comments note origins from Darwin SMBFS definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/snode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/snode.h

This header defines specfs special-file snode state, flags, and kernel interfaces.

Purpose:
- An snode represents an active special file.
- Filesystems that support special files convert normal vnodes to special vnodes with `specvp()`.
- `s_commonvp` points to a common vnode used for device data caching, preventing cache aliasing across multiple filesystem entries for the same device.
- Kernel-created snodes may have no real vnode and use their own vnode as common vnode.

Node model:
- `snode` stores stable-table link, associated vnode, real vnode, common vnode, device number, devinfo pointer, read-ahead offset, sync list link, device policy, block-device size, flags, fsid, times, open count, mapping count, lock, and condition variable.
- Comments identify which fields are protected by `stable_lock`, `spec_syncbusy`, or `s_lock`.

Flags:
- Update/access/change time bits, private open, 64-bit/any-offset support, open/close serialization, waiter, clone/self-clone, needs close, device association, size valid, multiplexed stream, no flush, closing, and fenced for I/O retire.

Kernel conversions:
- `VTOS`, `VTOCS`, and `STOV` map between vnode, common snode, and vnode.

Kernel API:
- Specfs VFS/vnode operation accessors, snode cache, common vnode creation/lookup, controlling terminal creation, delete/mark, init, device close, putpage, segmap, devfs-associated specvp creation, devinfo association/hold, sync, snode walk, open-count lookup, clone checks, fencing/unfencing, and size invalidation.
- Async putpage globals are declared.

Size constants:
- `UNKNOWN_SIZE` is `MAXOFFSET_T` for devices without size properties.
- On 32-bit kernels, `SPEC_MAXOFFSET_T` limits block-driver offsets due to 32-bit `daddr_t`.

Hashing:
- Stable table size is 256 and hashes by major+minor.
- Stable table and locks are declared.

Dependencies and relationships:
- Bridges VFS special-file entries, device driver opens/closes, devinfo association, page cache aliasing, and device retirement fencing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/snode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/swapnode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/swapnode.h

This header declares swapfs global reservation values and vnode interfaces.

Globals:
- `swapfs_minfree` is the amount of available resident memory unavailable to swapfs.
- `swapfs_desfree` is another free-memory threshold.
- `swapfs_reserve` is unavailable for swap reservation by non-privileged processes.

Interfaces:
- `swap_vnodeops` exposes swapfs vnode operations.
- `swapfs_getvp(ulong_t)` returns a swapfs vnode.

Debugging:
- Under `SWAPFS_DEBUG`, exposes `swapfs_debug`, `SWAPFS_PRINT`, and debug bit categories for subroutines, vnode ops, VFS ops, page creation, and putpage.
- Without debug, print macro compiles away.

Dependencies and relationships:
- Swapfs is a vnode-backed pseudo filesystem for anonymous/swap reservations.
- This header is intentionally small and mostly exports globals to swapfs implementation units.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/swapnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmp.h

This header defines tmpfs per-mount state, memory limits, conversion macros, and internal operation declarations.

Mount state:
- `tmount` stores VFS pointer, root tmpnode, mount path, anonymous reservation limit, reserved anonymous pages, pseudo device number, generation number, contents lock, and per-mount rename lock.
- All fields are protected by `tm_contents`; renames are protected by `tm_renamelck`.

Conversions:
- `VFSTOTM`, `VTOTM`, `VTOTN`, and `TNTOV` map VFS/vnode/tmpnode state.
- `tmpnode_hold` and `tmpnode_rele` wrap vnode hold/release.

Directory operation enums:
- `de_op` distinguishes create, mkdir, link, and rename for directory enter.
- `dr_op` distinguishes remove, rmdir, and rename for directory remove.

Memory limits:
- `TMPMINFREE` defaults to 2 MiB and represents anonymous memory tmpfs leaves free for the rest of the system.
- `tmpfs_minfree` is exported in pages.
- `TMPMAXFRACKMEM` limits tmpfs kernel metadata memory to 1/25 of physical memory unless patched via `tmpfs_maxkmem`.
- `tmp_kmemspace` tracks metadata memory use.

Internal API:
- tmpnode init/truncate/growmap.
- Directory lookup/delete/init/truncate/enter.
- tmpfs memory allocate/free.
- anonymous memory reservation.
- access and sticky-remove checks.
- mount option number/mode conversion helpers.

Other:
- `TMP_MUSTHAVE` is a memory-allocation/reservation flag.

Dependencies and relationships:
- Tmpfs combines vnode/tmpnode metadata with anonymous memory reservation accounting.
- This header complements tmpnode definitions elsewhere by defining mount-level controls and internal helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmp.h -->