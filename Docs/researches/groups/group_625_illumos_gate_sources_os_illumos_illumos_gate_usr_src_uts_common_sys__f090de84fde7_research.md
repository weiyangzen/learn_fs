# Group Research: group_625_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__f090de84fde7

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and every requested source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs.h

## Role

`vfs.h` defines illumos' central virtual filesystem mount abstraction. It supplies the `vfs_t` structure, filesystem identifiers, mount-option tables, VFS operation signatures, filesystem type switch records, VFS feature bits, mount/root operation enums, and kernel helper prototypes used by filesystem implementations and the generic VFS layer.

## Key Interfaces

The file defines:
- `fsid_t`, the two-word filesystem identifier used in `statvfs` and mount lookup.
- `fid_t` and `fid32_t`, fixed-size file identifiers used by stateless file servers and `VFS_VGET`.
- `mntopt_t` and `mntopts_t`, mount-option name/value tables with flags such as `MO_SET`, `MO_HASVALUE`, `MO_NODISPLAY`, and `MO_IGNORE`.
- `vfs_t`, the per-mounted-filesystem object, including global and per-zone mount-list links, `vfs_op`, covered vnode, flags, block size, type index, fsid, private data, device, refcount, resource/mountpoint strings, zone ownership, FEM hooks, and lofi mount ID.
- `vfs_impl_t`, private kernel-side data for feature bitmaps, vnode-operation statistics, high-resolution creation time, and zone references.
- `VFS_OPS`, the canonical VFS operation signature macro used to define `struct vfsops` and the operation-registration union in `vfs_opreg.h`.

The VFS operation set includes `mount`, `unmount`, `root`, `statvfs`, `sync`, `vget`, `mountroot`, `freevfs`, `vnstate`, and `syncfs`. Public macros such as `VFS_MOUNT()` and `VFS_STATVFS()` route through generic `fsop_*` wrappers rather than directly indexing `vfs_op`.

## Flags and Features

Mount flags include policy and state bits such as `VFS_RDONLY`, `VFS_NOSETUID`, `VFS_REMOUNT`, `VFS_UNMOUNTED`, `VFS_XATTR`, `VFS_NODEVICES`, `VFS_NOEXEC`, `VFS_STATS`, and `VFS_XID`.

Feature bits are 64-bit `vfs_feature_t` values and are accessed through `vfs_has_feature()`, `vfs_set_feature()`, and related helpers. Feature examples include extended attributes, case-insensitive behavior, ACL-on-create support, dirent flags, system attribute views, access-filtered dirents, reparse points, and zero-copy cache-buffer support.

## Integration Points

`vfssw_t` and `vfsdef_t` define filesystem-type registration. `vfssw_t` holds the installed filesystem name, init function, flags, mount-option prototype, reference count, lock, and VFS operation vector. `vfsdef_t` is the module-facing filesystem definition record, with version `VFSDEF_VERSION = 5`.

Kernel prototypes cover mount/unmount control, root configuration, VFS locking, global sync, mount list management, option parsing, mountpoint/resource strings, vfssw lookup/refcounting, feature propagation, filesystem ID creation, mounted-device lookup, lofi access, and zone-safety checks.

## Research Notes

This header is a contract boundary. Filesystems should use accessor/helper functions for operation vectors, option tables, mount lists, and reference counts; comments explicitly warn that several fields are private to the generic VFS layer. Changes here affect filesystem modules, mount tools, vnode statistics, zone-visible mount behavior, and kernel ABI expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs_opreg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs_opreg.h

## Role

`vfs_opreg.h` defines the generic operation-registration mechanism used to construct VFS, vnode, FEM, and FSEM operation vectors from named operation-definition tables.

## Key Interfaces

The central type is `fs_func_p`, a union that includes:
- a generic function pointer,
- an error-function pointer,
- all `VFS_OPS`,
- all `VNODE_OPS`,
- all `FEM_OPS`,
- all `FSEM_OPS`.

This lets filesystem code use C99 designated initializers with strong type checking when filling `fs_operation_def_t` arrays.

`fs_operation_def_t` maps an operation name to an implementation function. `fs_operation_trans_def_t` is the master-table entry used by the registration layer: operation name, byte offset in the destination vector, default function, and error function.

## Integration Points

The header exposes:
- `fs_default()` and `fs_error()` placeholders.
- `fs_build_vector()` for constructing an operation vector from a translation table and implementation table.
- `vn_make_ops()` and `vn_freevnodeops()` for vnode operations.
- `vfs_setfsops()`, `vfs_makefsops()`, `vfs_freevfsops()`, and `vfs_freevfsops_by_type()` for VFS operation vectors.

## Research Notes

This header is kernel-only and depends on `vfs.h` and `fem.h`. It is the bridge between string-named operation tables used by filesystem modules and the concrete function-pointer vectors consumed by generic VFS/VOP dispatch.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs_opreg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfstab.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfstab.h

## Role

`vfstab.h` defines the user-facing `/etc/vfstab` parsing and formatting interface. It describes one filesystem table entry and declares lookup helpers for reading entries by special device, mountpoint, or matching template.

## Key Interfaces

The header defines:
- `VFSTAB` as `/etc/vfstab`.
- `VFS_LINE_MAX` as the maximum parsed line length.
- parse error codes `VFS_TOOLONG`, `VFS_TOOMANY`, and `VFS_TOOFEW`.
- `struct vfstab`, with string fields for special device, fsck device, mountpoint, filesystem type, fsck pass, automount flag, and mount options.

Convenience macros:
- `vfsnull(vp)` clears all fields to `NULL`.
- `putvfsent(fd, vp)` writes a vfstab entry, substituting `-` for missing fields.

## Integration Points

The declared library functions are:
- `getvfsent()`
- `getvfsspec()`
- `getvfsfile()`
- `getvfsany()`

These are consumed by userland mount/fsck administration tools rather than kernel VFS code.

## Research Notes

The interface stores pointers, not owned buffers, so callers must respect the parsing library’s lifetime rules. `putvfsent` is a macro around `fprintf`, so it evaluates its arguments directly and expects a valid `FILE *`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfstab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgareg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgareg.h

## Role

`vgareg.h` defines legacy VGA I/O port offsets, memory ranges, text-mode dimensions, register indexes, and bitfield helpers used by VGA console/framebuffer code.

## Key Definitions

The file defines:
- VGA register base `0x3c0`, register window size `0x20`.
- VGA memory base `0xa0000`, memory size `0x20000`.
- text mode dimensions of 80 columns by 25 rows.
- 8-bit graphics depth and colormap-entry counts.

It enumerates register offsets for:
- attribute controller,
- miscellaneous output,
- sequencer,
- DAC,
- graphics controller,
- CRTC,
- CGA status.

It also defines many register bit masks and packing helpers for horizontal/vertical timings, overflow bits, sync timing, scanline registers, display enable, memory mode, graphics mode, attribute mode, palette selection, and text framebuffer bases.

## Integration Points

Consumers pair this header with `vgasubr.h`, which provides functions for accessing indexed VGA registers. The constants are used by low-level console, boot, and framebuffer paths that need direct VGA programming.

## Research Notes

The macros are hardware-layout definitions, not type-safe APIs. Callers must understand indexed-register addressing and preserve reserved bits where required. This header is also relevant to standalone code paths that run before normal kernel services are available.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgareg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgasubr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgasubr.h

## Role

`vgasubr.h` declares helper routines and data tables for programming VGA registers and palettes. It abstracts kernel and standalone access to VGA register mappings.

## Key Interfaces

For kernel builds, `vgaregmap_t` is a pointer to `struct vgaregmap`, which holds a mapped register address, DDI access handle, and mapped flag. For standalone builds, it is a `uint_t`.

The exported functions read and write:
- raw VGA registers,
- CRTC registers,
- sequencer registers,
- graphics-controller registers,
- attribute-controller registers,
- indexed registers,
- DAC colormap entries.

It also exposes `vga_get_hardware_settings()` and debug-only `vga_dump_regs()`.

## Data Tables

The header declares text-mode initialization tables:
- `VGA_ATR_TEXT`
- `VGA_SEQ_TEXT`
- `VGA_CRTC_TEXT`
- `VGA_GRC_TEXT`
- `VGA_TEXT_PALETTES`

It defines register-count constants for each table and `VGA_MISC_TEXT`.

## Research Notes

This is a low-level support header. It expects callers to handle execution context carefully: kernel use involves DDI access handles, while standalone use cannot rely on normal kernel driver services.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgasubr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/videodev2.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/videodev2.h

## Role

`videodev2.h` is an illumos copy/adaptation of the public Video4Linux2 userspace ABI. It defines video-device capabilities, pixel formats, buffer formats, controls, tuners, audio, VBI data structures, and `VIDIOC_*` ioctl numbers.

## Key Interfaces

The header defines:
- legacy V4L1-style `VID_TYPE_*` capability bits.
- `v4l2_fourcc()` and many `V4L2_PIX_FMT_*` FourCC pixel formats.
- enums for fields, buffer types, control types, tuner types, memory models, colorspaces, and priority.
- base geometry types `v4l2_rect` and `v4l2_fract`.
- `struct v4l2_capability` and `V4L2_CAP_*` feature bits.
- `struct v4l2_pix_format`, `v4l2_fmtdesc`, `v4l2_timecode`, JPEG compression settings, request buffers, stream buffers, framebuffer/overlay structures, capture/output parameters, crop structures, standards, inputs, outputs, controls, tuners, modulators, frequencies, audio endpoints, raw VBI, sliced VBI, aggregate `v4l2_format`, and `v4l2_streamparm`.

## ABI and Alignment Notes

The file includes illumos-specific compatibility changes:
- It uses `<sys/ioccom.h>` ioctl encoding.
- It defines `struct v4l2_timeval` using fixed-width `uint64_t` fields instead of native `long`-based `timeval`.
- It uses `#pragma pack(4)` for selected structures when 64-bit kernel alignment differs from 32-bit alignment.
- It adds explicit padding in `v4l2_input` and `v4l2_format` to keep 32-bit applications and 64-bit drivers in agreement.

## Ioctls

The ioctl list covers capability query, format enumeration/get/set/try, buffer request/query/queue/dequeue, streaming on/off, framebuffer, overlay, parameters, video standards, inputs/outputs, controls, tuners, audio, modulators, frequencies, crop, JPEG compression, priority, sliced VBI capability, status logging, and extended controls.

Private ioctl numbers start at `BASE_VIDIOC_PRIVATE = 192`.

## Research Notes

This header is ABI-heavy. Changes to structure layout, packing, enum values, or ioctl numbers can break binary compatibility with applications and drivers. Some old MPEG compression definitions are guarded by `__KERNEL__` and marked obsolete in comments.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/videodev2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vio9p.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vio9p.h

## Role

`vio9p.h` defines the small public ioctl contract for illumos virtio 9P channel devices.

## Key Interfaces

The header defines:
- `VIRTIO_9P_TAGLEN` as 32 bytes, the maximum mount-tag length when the hypervisor advertises the mount-tag feature.
- `VIO9P_IOC_BASE`, using the characters `9` and `P` in the ioctl namespace.
- `VIO9P_IOC_MOUNT_TAG`, the ioctl for retrieving the mount tag.
- `VIO9P_MOUNT_TAG_SIZE`, one byte larger than the maximum tag to allow NUL termination.

## Research Notes

This file is intentionally narrow: it does not define 9P protocol structures, only the illumos device ioctl needed by consumers to discover virtio 9P channel metadata.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vio9p.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/visual_io.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/visual_io.h

## Role

`visual_io.h` defines the Solaris VISUAL framebuffer ioctl interface for device identification, color maps, hardware cursors, software console initialization, console drawing, polled I/O, and framebuffer/terminal-emulator integration.

## Key Interfaces

Public user-facing pieces include:
- `VIS_GETIDENTIFIER` and `struct vis_identifier`.
- cursor-position, cursor-colormap, and cursor-shape structures.
- `VIS_SETCURSOR`, `VIS_GETCURSOR`, `VIS_MOVECURSOR`, and `VIS_GETCURSORPOS`.
- `VIS_GETCMAP` and `VIS_PUTCMAP` with `struct vis_cmap`.

Kernel/standalone console pieces include:
- `VIS_DEVINIT`, `VIS_DEVFINI`, `VIS_CONSCURSOR`, `VIS_CONSDISPLAY`, `VIS_CONSCOPY`, and `VIS_CONSCLEAR`.
- screen coordinate typedefs.
- `color_t`, a union covering mono, 4-bit, 8-bit, 16-bit, 24-bit, and 32-bit pixel encodings.
- `struct vis_consdisplay`, `vis_conscopy`, `vis_conscursor`, and `vis_consclear`.
- `struct vis_polledio`, providing display/copy/cursor callbacks usable in polled contexts.
- `struct vis_devinit`, exchanged between terminal emulator and framebuffer driver.
- `struct visual_ops`, the framebuffer operation table.

## Integration Points

The comments explain the console layering model: framebuffer drivers that support software console operation must expose low-level operations usable by kmdb or other polled contexts where normal DDI services, locks, and copy routines may not be available.

## Research Notes

This header is an ABI and driver-contract file. The most important risks are pointer ownership/copyin behavior for user ioctls and the strict context restrictions for polled console routines.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/visual_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vlan.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vlan.h

## Role

`vlan.h` defines media-independent VLAN tag constants and bitfield helpers.

## Key Interfaces

The header defines:
- VLAN tag size `VLAN_TAGSZ = 4`.
- TPID `VLAN_TPID = 0x8100`.
- masks, sizes, and shifts for VLAN ID, CFI, and priority.
- valid VLAN ID range: none `0`, minimum `1`, maximum `4094`.

Macros:
- `VLAN_TCI(pri, cfi, vid)` constructs a tag-control-information value.
- `VLAN_PRI(tci)`, `VLAN_CFI(tci)`, and `VLAN_ID(tci)` extract fields.
- `VLAN_MBLKPRI(mp)` maps a STREAMS message band to VLAN priority using 32 bands per priority and clamps out-of-range values to zero.

## Research Notes

The macros do not validate input ranges. Callers should sanitize priority, CFI, and VLAN ID before constructing a TCI.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vlan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm.h

## Role

`vm.h` is a small umbrella header for VM subsystem declarations. It includes VM parameter, VM system, and system macro headers, then exposes a few kernel VM entry points.

## Key Interfaces

For kernel builds, it includes `sys/vnode.h` and declares:
- `setupclock()`
- `pageout()`
- `cv_signal_pageout()`
- `queue_io_request(struct vnode *, u_offset_t)`

It also declares `memavail_lock` and `memavail_cv`.

The `WAKE_PAGEOUT_SCANNER(tag)` macro emits a DTrace probe named from the supplied tag and broadcasts on `proc_pageout->p_cv`.

## Research Notes

This file is a coordination header for pageout and memory-availability signaling. The DTrace token-pasting macro requires compile-time probe tag names.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm_usage.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm_usage.h

## Role

`vm_usage.h` defines the `getvmusage()` interface for aggregating resident memory and swap usage by system, zone, project, task, real user, or effective user.

## Key Interfaces

Flag groups include:
- caller-zone scopes: `VMUSAGE_SYSTEM`, `VMUSAGE_ZONE`, `VMUSAGE_PROJECTS`, `VMUSAGE_TASKS`, `VMUSAGE_RUSERS`, `VMUSAGE_EUSERS`.
- all-zone scopes: `VMUSAGE_ALL_ZONES`, `VMUSAGE_ALL_PROJECTS`, `VMUSAGE_ALL_TASKS`, `VMUSAGE_ALL_RUSERS`, `VMUSAGE_ALL_EUSERS`.
- collapsed-zone scopes: `VMUSAGE_COL_PROJECTS`, `VMUSAGE_COL_RUSERS`, `VMUSAGE_COL_EUSERS`.

`vmusage_t` reports zone ID, result type, entity ID, total/private/shared RSS, and total/private/shared swap reservation in bytes.

The user-facing function is:
- `getvmusage(uint_t flags, time_t age, vmusage_t *buf, size_t *nres)`

Kernel-side declarations include:
- `vm_getusage()`
- `vm_usage_init()`

## Research Notes

The comments define zone semantics carefully: non-global zones requesting all-zone or collapsed-zone data are reduced to local-zone scope. `VMUSAGE_SYSTEM` in a non-global zone returns a system-typed result, but only for the calling zone.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm_usage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem.h

## Role

`vmem.h` defines the public interface to the illumos vmem resource allocator. Vmem arenas manage address ranges or other quantum-based resources and can import from parent arenas.

## Key Interfaces

Allocation flags include sleep/no-sleep/panic behavior compatible with `KM_*`, fit policy flags (`VM_BESTFIT`, `VM_FIRSTFIT`, `VM_NEXTFIT`), and special flags such as `VM_MEMLOAD`, `VM_NORELOC`, `VM_ABORT`, and `VM_ENDALLOC`.

Arena-creation flags include:
- `VMC_POPULATOR`
- `VMC_NO_QCACHE`
- `VMC_IDENTIFIER`
- `VMC_XALLOC`
- `VMC_XALIGN`
- `VMC_DUMPSAFE`

Segment type flags support walking allocated/free segments and private span/rotor/walker segment types.

Public types include opaque `vmem_t`, import/free callback types, and alternate `vmem_ximport_t`.

Public functions include:
- `vmem_create()` / `vmem_xcreate()`
- `vmem_destroy()`
- `vmem_alloc()` / `vmem_xalloc()`
- `vmem_free()` / `vmem_xfree()`
- `vmem_add()`
- `vmem_contains()`
- `vmem_walk()`
- `vmem_size()`
- `vmem_qcache_reap()`

Kernel-only helpers include `vmem_init()`, `vmem_update()`, `vmem_is_populator()`, and `vmem_seg_size`.

## Research Notes

`VMEM_REENTRANT` affects locking during `vmem_walk()` callbacks: the arena lock may be dropped, so callbacks must tolerate concurrent arena mutation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem_impl.h

## Role

`vmem_impl.h` defines implementation-private structures for the vmem allocator: segments, freelists, hash tables, quantum caches, kstats, and arena metadata.

## Key Structures

`vmem_seg_t` represents an arena segment. Its first four fields intentionally match `vmem_freelist_t`: start, end, next-of-kind, previous-of-kind. It also has arena links, type, imported flag, audit depth, and optional audit metadata such as thread, timestamp, and stack.

`vmem_freelist_t` is the size-class free-list header format.

`struct vmem` contains:
- arena name, lock, and condition variable,
- arena ID and allocation-failure injection field,
- creation flags, quantum sizing, qcache limits, and import minimum,
- source import/free callbacks and parent source arena,
- global vmem list linkage,
- kstat pointer and embedded kstat data,
- segment freelist,
- allocated-segment hash table and initial hash table,
- free-list bitmap,
- sentinel segment and next-fit rotor,
- quantum cache pointers,
- power-of-two freelists.

## Helpers

The file defines hash indexing macros, `VS_SIZE()`, constants for name length, initial hash size, qcache count, freelist count, and audit stack depth.

`vmem_kstat_t` tracks memory in use/import/total, source ID, allocation/free/wait/fail counts, lookup/search counts, population waits/failures, and `vmem_contains()` metrics.

## Research Notes

This header is for allocator internals, not consumers. The freelist/segment layout coupling is explicit and should be preserved. Changes here require matching changes in vmem implementation and observability consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmem_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmsystm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmsystm.h

## Role

`vmsystm.h` exposes miscellaneous VM subsystem globals, tunables, constants, and helper prototypes used inside the kernel.

## Key Interfaces

It declares page-accounting globals such as `freemem`, `avefree`, `avefree30`, `deficit`, `nscan`, `desscan`, `slowscan`, `fastscan`, `pushes`, `low_mem_scan`, and `n_throttle`.

Writable tunables include `maxpgio`, `lotsfree`, `desfree`, `minfree`, `needfree`, `throttlefree`, `pageout_reserve`, and `pages_before_pager`.

`NOMEMWAIT()` detects contexts that must not sleep while freeing memory: pageout, fsflush, scheduler, or `T_PUSHPAGE` threads.

The header also defines swapout flags, user-range validation return codes, large-page mapping flags, VAC alignment flags, and prototypes for address selection, user access checks, page-size selection, mapping helpers, VM metering, copy-on-write mapin, physical-page temporary mapping, memory PFN checks, cache flushing, boot virtual allocation, and exec stack-page slewing.

## Research Notes

This is an internal VM coordination header. Many declarations are architecture- or subsystem-sensitive, and several globals are core memory-pressure control inputs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmsystm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic.h

## Role

`vnic.h` defines the public ioctl ABI for creating, deleting, inspecting, and modifying virtual NICs.

## Key Interfaces

Diagnostic codes in `vnic_ioc_diag_t` describe extended failure reasons such as duplicate or invalid MAC addresses, invalid factory slots, unsupported factory addresses, invalid prefixes/margins, missing hardware rings, and invalid MTU.

`vnic_mac_addr_type_t` describes how a VNIC address is chosen:
- fixed,
- random,
- factory,
- auto,
- primary,
- VRID-derived,
- unknown.

Ioctl structures:
- `vnic_ioc_create_t` includes VNIC ID, lower link ID, MAC type/address/prefix/slot, VLAN ID, VRID, address family, status, creation flags, diagnostic code, and MAC resource properties.
- `vnic_ioc_delete_t` identifies a VNIC to delete.
- `vnic_info_t` reports configured VNIC properties.
- `vnic_ioc_modify_t` supports changing MAC address and/or resource controls.

Creation flags include duplicate-check bypass, anchor creation, and forced VLAN-based VNIC creation without margin checking.

## ABI Notes

The file uses `#pragma pack(4)` under mixed 64-bit/32-bit long-long alignment conditions to preserve ioctl ABI compatibility.

## Research Notes

This header sits at the datalink/MAC management boundary. The structures include both administrative inputs and diagnostic outputs, so callers should inspect both errno and `vc_diag`/`vm_diag` style fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic_impl.h

## Role

`vnic_impl.h` defines kernel-private VNIC state and VNIC device-management entry points.

## Key Structures

`vnic_t` stores:
- VNIC datalink ID and enabled bit,
- MAC handles for the VNIC and lower link,
- primary and secondary MAC client/unicast handles,
- margin, factory slot, address type, address bytes and length,
- VLAN ID, VRID, address family, force flag,
- lower link ID and MAC notify handle,
- transmit checksum flags, LSO capability, MTU, and link state.

Convenience macros identify the primary MAC client and unicast handles.

## Functions

The header declares:
- `vnic_dev_create()`
- `vnic_dev_modify()`
- `vnic_dev_delete()`
- `vnic_dev_init()`
- `vnic_dev_fini()`
- `vnic_dev_count()`
- `vnic_get_dip()`
- `vnic_info()`

## Research Notes

This is internal to the VNIC driver/control plane. It combines MAC-provider state, MAC-client state, datalink IDs, and user-visible configuration from `vnic.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnic_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnode.h

## Role

`vnode.h` is the primary illumos vnode contract. It defines vnode types, vnode structure layout, vnode flags, vnode attributes, extensible attributes, security attributes, caller context, vnode operation signatures, VOP dispatch macros, vnode lifecycle helpers, vnode path-cache behavior, event notifications, and VM/page integration hooks.

## Core Data Structures

`vopstats_t` records per-operation kstats for VOP calls and byte counts for read/write/readdir.

`vnode_t` contains public fields such as lock, flags, refcount, filesystem-private data, containing VFS, stream pointer, type, and device number. It also contains private fields for mounted VFS, operation vector, page list, locks, FEM hooks, path cache, mmap/open counts, MPSS data, file-operation watches, vnode-specific data, xattr directory vnode, and DNLC refcount.

The header explicitly warns that vnodes must be allocated through `vn_alloc()` and must not be embedded in filesystem-private nodes.

## Path Cache Model

The file documents `v_path` and `v_path_stamp` in detail. Filesystem lookup/create/mkdir code updates cached paths when parent context is known. Directory renames update the renamed vnode directly but leave descendants potentially stale; later lookups refresh stale children by comparing path stamps.

## Attributes

`vattr_t` defines classic vnode attributes: type, mode, owner, group, fsid, node ID, link count, size, timestamps, rdev, block size, block count, and sequence number.

`xoptattr_t` and `xvattr_t` define extensible attributes such as create time, archive/system/readonly/hidden bits, nounlink, immutable, append-only, nodump, opaque, antivirus quarantine/modified/scanfingerprint, reparse, generation, offline, sparse, project inheritance, and project ID.

Macros define classic `AT_*` masks, optional `XAT_*` masks, and helpers to set/check requested and returned xvattr bits.

## Vnode Operations

`VNODE_OPS` defines the complete vnode operation vector, including:
- open/close/read/write/ioctl/setfl,
- getattr/setattr/access,
- lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink,
- fsync/inactive/fid,
- rwlock/rwunlock/seek/cmp/frlock/space/realvp,
- getpage/putpage/map/addmap/delmap,
- poll/dump/pathconf/pageio/dumpctl/dispose,
- get/set security attributes,
- share locks,
- vnode events,
- zero-copy buffer request/return.

The file declares `fop_*` generic dispatch wrappers and defines `VOP_*` macros that route through those wrappers.

## Security, Events, and Context

`vsecattr_t` carries ACL and ACE data for `VOP_GETSECATTR` and `VOP_SETSECATTR`.

`caller_context_t` carries caller PID, system ID, caller ID, and flags such as `CC_DONTBLOCK` and `CC_WOULDBLOCK`.

`vnevent_t` enumerates rename, remove, create, link, mount-over, truncate, and pre-rename notifications. Helper functions emit these events.

## Lifecycle and VM Integration

Kernel helpers cover vnode allocation/reinit/recycle/free, read-only/open/mapped checks, open-count transitions, flock and mandatory-lock checks, cached-data checks, operation-vector accessors, mountpoint locks, spec vnode creation, path manipulation, vnode-specific data, xattr/reparse initialization, caller ID allocation, MPSS/pageio decisions, and vnode reference macros.

`VN_HOLD` and `VN_RELE` wrappers centralize reference-count changes and emit DTrace probes. `VN_DISPOSE()` routes page disposal through `VOP_DISPOSE()` when the page belongs to a real vnode and otherwise frees/destroys kernel-address-space pages.

## Research Notes

This header is one of the most sensitive ABI/internal-contract files in the VFS stack. Filesystems should treat most vnode fields as private and use `vn_*`, `VOP_*`, and operation-registration helpers. Attribute bitmap macros contain assertions using bitwise OR checks; users must initialize `xvattr_t` with `xva_init()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vscan.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vscan.h

## Role

`vscan.h` defines the kernel/user interface for the illumos virus-scan service module and its `vscand` daemon.

## Key Interfaces

The header defines the device path prefix `/dev/vscan/vscan` and ioctl commands for:
- enabling the door rendezvous,
- disabling during daemon shutdown,
- updating configuration,
- returning scan results,
- setting maximum in-progress requests.

Scan statuses include undefined, no scan required, error, clean, infected, and scanning.

`vs_scan_req_t` is sent to the daemon and includes request index, sequence number, file size, flags, modified/quarantined indicators, path, and scanstamp.

`vs_scan_rsp_t` is the async daemon response with index, sequence number, result, and updated scanstamp.

`vs_config_t` carries file-type filters, maximum file size, and allow/deny behavior for oversized files.

## Kernel Hooks

Kernel declarations cover vscan service lifecycle, configuration, in-use check, result/abort handling, vnode lookup by request, door lifecycle/open/close, scanning a file via door, and driver node creation.

## Research Notes

This header depends on `AV_SCANSTAMP_SZ` from `vnode.h`. It is a coordination ABI between filesystem access paths, the vscan kernel service, and the external daemon.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vscan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt.h

## Role

`vt.h` defines the public virtual-terminal ioctl interface shared with other operating systems plus Solaris-specific console-user and display metadata operations.

## Key Interfaces

Public ioctls include:
- `VT_OPENQRY`
- `VT_SETMODE`
- `VT_GETMODE`
- `VT_RELDISP`
- `VT_ACTIVATE`
- `VT_WAITACTIVE`
- `VT_GETSTATE`
- `VT_ENABLED`
- `VT_GET_CONSUSER`
- `VT_SET_CONSUSER`

`struct vt_mode` configures automatic vs process-controlled switching, write-wait behavior, and signals for release/acquire/forced release.

`struct vt_stat` returns active VT, signal, and open-state mask.

Project-private ioctls configure VT count, display info/login state, target console, real active console, and console-user reset.

`struct vt_dispinfo` carries display owner PID, display number, and login state.

## Research Notes

The header separates public compatibility ioctls from illumos/private control ioctls. `VT_SET_TARGET` and `VT_GETACTIVE` exist to hide the vtdaemon special console from ordinary `VT_GETSTATE` consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt_impl.h

## Role

`vt_impl.h` defines the kernel-private state and functions for the virtual console/terminal implementation.

## Key Structures

`vc_waitactive_msg_t` queues pending `VT_WAITACTIVE` messages with source minor, target minor, and STREAMS message pointer.

`vc_state_t` is the per-VT soft state. It stores:
- minor number and AVL linkage,
- switching mode, wait flag, release/acquire signals, controlling PID, target switch minor, and flags,
- display number and login state,
- terminal emulator state and tty common state,
- STREAMS bufcall/timeout IDs and write queue,
- optional pending firmware character,
- a mutex protecting `vc_flags`.

Flags cover tty initialization, open state, stopped output, delay, and busy transmission.

## Integration Points

The header declares ioctl/open/close/cleanup functions, hotkey checking, minor-to-state lookup, global VT state variables, attachment/init helpers, active/console-user string helpers, minor validation, and resize support.

Global state includes the wscons device info pointer, AVL root of VTs, active console, console-user target, global lock, and last console.

## Research Notes

This header is internal to console STREAMS/VT code and depends on `vt.h`, keyboard/display headers, terminal emulator state, tty common state, AVL, and list infrastructure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtdaemon.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtdaemon.h

## Role

`vtdaemon.h` defines the small door-based interface used to communicate with the virtual-terminal daemon.

## Key Interfaces

The daemon door path is:
- `/var/run/vt/vtdaemon_door`

Event codes:
- `VT_EV_X_EXIT`, carrying a VT number.
- `VT_EV_HOTKEYS`, carrying a VT number.

`vt_cmd_arg_t` contains the event code and VT number.

## Research Notes

This header is intentionally minimal and is paired with the VT implementation and daemon. It defines control-plane messages, not terminal data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtdaemon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtoc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtoc.h

## Role

`vtoc.h` defines the illumos VTOC partition-table ABI, extended VTOC layout, compatibility conversion macros, partition tags/flags, error codes, and read/write routines.

## Key Interfaces

The file defines:
- `V_NUMPAR` from `NDKMAP`.
- sanity/version constants `VTOC_SANE`, `V_VERSION`, and `V_EXTVERSION`.
- partition tags for root, swap, usr, backup, EFI/GPT system/reserved, VxVM, BIOS boot, NetBSD FFS, FreeBSD partition types, and unknown.
- permission flags `V_UNMNT` and `V_RONLY`.
- VTOC operation error returns such as `VT_ERROR`, `VT_EIO`, `VT_EINVAL`, `VT_ENOTSUP`, `VT_ENOSPC`, and `VT_EOVERFLOW`.

Structures:
- `struct partition` uses `daddr_t` and `long` sector counts.
- `struct vtoc` is the classic layout with boot info, sanity, version, volume name, sector size, partition count, reserved words, partition array, timestamps, and ASCII label.
- `struct extpartition` and `struct extvtoc` use 64-bit disk addresses/sizes.

## Compatibility

Kernel macros convert between `vtoc` and `extvtoc`. Under `_SYSCALL32`, the file defines `partition32`, `vtoc32`, and conversion macros between 32-bit, native, and extended layouts, including timestamp clamping to `TIME32_MAX`.

## Functions

The public routines are:
- `read_vtoc()`
- `write_vtoc()`
- `read_extvtoc()`
- `write_extvtoc()`

## Research Notes

The comments explain that Sun/illumos VTOC is not a literal AT&T second-sector VTOC; several fields are synthesized from disk labels and unsupported fields are returned as zero. Conversion macros cast sizes and starts, so overflow handling belongs in callers or the routines that use these macros.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtrace.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtrace.h

## Role

`vtrace.h` preserves legacy vtrace facility and event IDs and maps enabled trace macros to DTrace static probes in debug/lint builds. The comments state that vtrace has been subsumed by DTrace and that new tracepoints should use DTrace directly.

## Key Contents

The header defines facility IDs for traps, interrupts, dispatcher, VM, process, STREAMS, TCP, UDP, IP, ARP, Ethernet drivers, SCSI, callout, filesystems, kernel RPC, scheduling, physical I/O, meta disk, sockfs, devmap, and DADA/IDE target paths.

It then defines event tags for each facility. Major groups include:
- trap and interrupt entry/exit points,
- dispatcher scheduling/switching/preemption events,
- VM pageout, segmap, segvn, anon, swap, page creation/free/hash events,
- process exec/exit/fork,
- scheduler swap-in/swap-out decisions,
- STREAMS queue/message events,
- TCP/UDP/IP/ARP open/close/read/write/service events,
- legacy Ethernet driver events,
- physio lock/fault/buffer phases,
- SCSI ESP/ISP/FAS and sd path events,
- callout timeout/untimeout events,
- specfs/tmpfs/swapfs/UFS/NFS/KRPC events,
- FIFO/rlogin/sockfs/devmap/DAD events.

## Trace Macros

When `DEBUG`, `lint`, or `__lint` is defined, `TRACE_0` through `TRACE_5` expand to calls to generated `__dtrace_probe___vtrace_<tag>()` functions with up to five `ulong_t` arguments.

Otherwise, all `TRACE_*` macros compile away.

## Research Notes

The numeric constants are historical compatibility data and comments say they should not be changed or extended. Consumers should treat this as an observability compatibility layer, not as a modern tracing API.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_event.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_event.h

## Role

`vuid_event.h` defines the Virtual User Input Device event namespace, `Firm_event` wire structure, and ioctls for devices that can emit VUID-formatted input events.

## Key Interfaces

The VUID address space is segmented into 256-code device ranges. Device IDs include ASCII, TOP, ISO, wheel, lightpen, button, dial, SunView, panel, scroll, workstation, and customer-reserved ranges.

Macros compute segment ranges:
- `vuid_first(devid)`
- `vuid_last(devid)`
- `vuid_in_range(devid, id)`

The workstation range contains virtual keyboard and locator codes:
- shift keys and modifier states,
- button events,
- left/right/top/bottom key groups,
- keypad keys,
- mouse button aliases,
- locator delta and absolute axes,
- batching,
- mouse capability-change events,
- absolute mouse type,
- keyboard layout change.

`Firm_event` contains event ID, pair type, pair offset, value, and timestamp. On LP64, the timestamp is `timeval32`; otherwise it is native `timeval`.

Pair types describe how an event updates associated state: none, set, delta, or absolute.

## Ioctls

VUID format ioctls select native byte stream vs `Firm_event` stream. VUID address ioctls set or get the active segment address for a physical input device. x86 variants use different ioctl numbers to avoid VT conflicts.

`Vuid_addr_probe` carries the default base and requested/current address.

## Research Notes

This is a legacy input ABI designed for human input devices and event-state maintenance. It explicitly excludes high-volume data devices. The structure layout and ioctl values are compatibility-sensitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_queue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_queue.h

## Role

`vuid_queue.h` defines the public interface for a small queue package that stores pending `Firm_event` VUID input events.

## Key Structures

`Vuid_queue` holds:
- top and bottom queue nodes,
- a free-list pointer,
- current item count,
- queue capacity.

Macros expose used count, available capacity, size, empty state, and full state.

`Vuid_q_node` stores next/previous links and one `Firm_event`.

Status codes are:
- `VUID_Q_OK`
- `VUID_Q_OVERFLOW`
- `VUID_Q_EMPTY`

## Functions

The header declares old-style unprototyped functions for:
- queue initialization over caller-provided storage,
- putting events into timestamp-dependent queue position,
- getting and peeking,
- putting an event back at the top,
- compressing valuator events,
- identifying valuator events,
- deleting a node.

## Research Notes

The queue owns no allocation; callers provide and later release the backing storage. Compression is designed for input-event streams where high-frequency valuator updates can be collapsed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_queue.h -->