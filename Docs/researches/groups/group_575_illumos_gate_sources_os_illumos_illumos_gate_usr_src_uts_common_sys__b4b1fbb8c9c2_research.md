# Group Research: group_575_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__b4b1fbb8c9c2

Scope: `Docs/research_subset_a.md`; source tree `sources/os/illumos/illumos-gate`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dklabel.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dklabel.h

## Scope

Complete file read, 277 lines. This header defines the Sun disk label and VTOC on-disk/user-kernel ABI structures used by illumos disk drivers and disk-label tooling.

## Public Surface

The file exports disk-label constants such as `DKL_MAGIC`, `FKL_MAGIC`, `NDKMAP`, `DK_LABEL_LOC`, `DK_LABEL_SIZE`, `DK_MAX_BLOCKS`, and `DK_ACYL`. It conditionally supports `_SUNOS_VTOC_16` and `_SUNOS_VTOC_8`, selecting partition count and label placement at compile time.

It defines `blkaddr_t` and `blkaddr32_t` if `BLKADDR_TYPE` has not already been defined, switching widths based on `_EXTVTOC`. The visible structures are:

- `struct dk_map`: in-memory partition start cylinder and block count.
- `struct dk_map32`: fixed-width on-disk partition map.
- `struct dk_map2`: SVr4 partition tag/flag pair.
- `struct dkl_partition`: VTOC16 partition tag, flag, start sector, and size.
- `struct dk_vtoc`: VTOC payload, with different layouts for 16-slice and 8-slice systems.
- `struct dk_label`: 512-byte disk-label layout ending in `dkl_magic` and XOR checksum.
- `struct fk_label`: DOS floppy label.
- `struct dk_devid`: 512-byte fabricated device-id storage block.
- `DKD_GETCHKSUM()` and `DKD_FORMCHKSUM()` helpers for `struct dk_devid` checksum byte packing.

## Behavior And Integration

There is no executable function body here. Runtime behavior is supplied by disk-label readers, writers, and ioctls that interpret these exact layouts. The structures intentionally preserve on-disk size and field order, including compatibility aliases like `dkl_asciilabel`, `v_timestamp`, and old `_SUNOS_VTOC_8` names such as `dkl_gap1`.

`struct dk_label` is designed to remain at the start of a 512-byte sector; `LEN_DKL_PAD` computes padding from the selected VTOC layout to keep the label structure at `DK_LABEL_SIZE`.

## Dependencies And Invariants

The header depends on illumos integer, address, and byte-order helper types from `sys/isa_defs.h` and `sys/types32.h`; checksum formation also assumes `hibyte`, `lobyte`, `hiword`, and `loword` are available to includers.

Key invariants are ABI layout stability, fixed 32-bit fields for on-disk structures, correct `_SUNOS_VTOC_16` or `_SUNOS_VTOC_8` selection, `DKL_MAGIC` validation, and checksum agreement across the whole label/devid sector. The duplicate `#include <sys/isa_defs.h>` is harmless but visible.

## Risks

Any field reordering or type-width change can corrupt disk labels or break user/kernel ioctl compatibility. `_EXTVTOC` changes `blkaddr_t` width, so callers must distinguish in-memory address capacity from fixed on-disk `blkaddr32_t`. The checksum macros are multi-statement macros without `do { } while (0)`, so use in conditional statements requires care.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dklabel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/altsctr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/altsctr.h

## Scope

Complete file read, 84 lines. This header defines the alternate-sector partition metadata used by legacy DKTP disk handling.

## Public Surface

It exports:

- `struct alts_parttbl`: alternate sector table header with sanity/version fields, map location/length, remap-entry region metadata, reserved region base, and padding.
- `struct alts_ent`: one bad-sector remap range, with `bad_start`, `bad_end`, and `good_start`.
- Size macros `ALTS_PARTTBL_SIZE` and `ALTS_ENT_SIZE`.
- Sector-map states `ALTS_GOOD` and `ALTS_BAD`.
- Table identity/version constants `ALTS_SANITY` and `ALTS_VERSION1`.
- Entry/search constants `ALTS_ENT_EMPTY`, `ALTS_MAP_UP`, and `ALTS_MAP_DOWN`.

## Behavior And Integration

There is no executable code. Disk drivers and bad-block handlers use these structures to locate an alternate-sector partition map and translate bad sectors to reserved good sectors.

## Dependencies And Invariants

The file assumes fixed-width `uint32_t` is available before or through includers. On-disk consumers must preserve structure widths and offsets. `ALTS_SANITY` and `ALTS_VERSION1` are the primary validation fields.

## Risks

`ALTS_ENT_EMPTY` and `ALTS_MAP_DOWN` are negative macros while the table fields are unsigned, so callers must avoid storing sentinel values directly into `uint32_t` fields without deliberate casting semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/altsctr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/bbh.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/bbh.h

## Scope

Complete file read, 81 lines. This header defines the DKTP bad-block handling object interface.

## Public Surface

The header includes `sys/scsi/scsi_types.h` and exports:

- `struct bbh_cookie`: sector address and contiguous sector length for bad-block handling.
- Address aliases `ck_lsector` and `ck_sector` into `lldaddr_t`.
- `bbh_cookie_t`.
- `struct bbh_handle`: cookie table plus current index/count.
- `struct bbh_obj`: object data pointer plus operation table.
- `struct bbh_objops`: callbacks for init/free, mapping a `buf` into a handle, converting handle to cookie, and freeing a handle.
- Dispatch macros `BBH_INIT`, `BBH_FREE`, `BBH_GETHANDLE`, `BBH_HTOC`, and `BBH_FREEHANDLE`.
- Cookie accessor macros `BBH_GETCK_SECTOR` and `BBH_GETCK_SECLEN`.

## Behavior And Integration

The file implements object-style polymorphism with function pointers and macros. Common disk drivers can call bad-block handlers without knowing the concrete implementation. The handler translates I/O buffers into one or more physical-sector cookies, allowing remap/alternate-sector logic to participate in strategy paths.

## Dependencies And Invariants

It depends on DKTP/SCSI opaque types, `struct buf`, and `lldaddr_t`. The object pointer passed to macros must be a valid `struct bbh_obj *` with a populated `bbh_ops` table.

## Risks

The dispatch macros perform unchecked casts and dereference callbacks directly. A missing callback or wrong object type will fail at runtime. The `ck_sector` alias accesses only the `_p._l` member of `lldaddr_t`, so large-sector users must ensure they use the correct address alias.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/bbh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cm.h

## Scope

Complete file read, 65 lines. This is a small common DKTP kernel header for shared includes, opaque typing, and buffer-sector helpers.

## Public Surface

The file includes `sys/types.h` always and several kernel-only headers under `_KERNEL`, including DDI, allocation, open, errno, and device macros. Under `_KERNEL` it defines:

- `opaque_t` as `void *` if SCSI has not already supplied it.
- `PRF` as `prom_printf`.
- `SET_BP_SEC(bp, X)` and `GET_BP_SEC(bp)` for storing/retrieving a sector value via `buf.b_private`.

## Behavior And Integration

The header gives DKTP code a shared way to pass opaque object pointers and to stash sector metadata inside `struct buf`.

## Dependencies And Invariants

`GET_BP_SEC()` casts `b_private` back to `daddr_t`; this assumes the stored sector value safely round-trips through a pointer-sized field. It is only intended for kernel builds.

## Risks

Using `b_private` for sector storage conflicts with any other subsystem using the same buffer field. The pointer/integer cast is architecture-sensitive and should stay confined to legacy DKTP code that already expects this convention.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdev.h

## Scope

Complete file read, 40 lines. This header provides SCSI device address access macros for DKTP common device code.

## Public Surface

It defines:

- `CMDEV_TARG(devp)` as `(devp)->sd_address.a_target`
- `CMDEV_LUN(devp)` as `(devp)->sd_address.a_lun`

## Behavior And Integration

There is no executable behavior. The macros abstract target and LUN extraction from a `struct scsi_device`-like pointer used by DKTP direct access disk code.

## Dependencies And Invariants

The `devp` argument must refer to an object with `sd_address.a_target` and `sd_address.a_lun` fields. No type checking or null checking is performed.

## Risks

Because these are raw lvalue macros, passing an incompatible pointer produces compile-time or runtime breakage depending on context. They also evaluate `devp` once, so side effects are limited but still undesirable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdk.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdk.h

## Scope

Complete file read, 103 lines. This header defines the common disk driver soft-state structure used by the `cmdk` layer.

## Public Surface

The header includes `sys/cmlb.h` and `sys/dktp/tgdk.h`. It defines:

- `CMDK_UNITSHF` and `CMDK_MAXPART` for minor-number partition packing.
- `CMDK_HWIDLEN`.
- `struct cmdk`: per-device state including devinfo, device number, target disk object, CMLB handle, device id, open state, bad-block handling data, alternate-sector data, and power-management fields.
- Power states `CMDK_SPINDLE_UNINIT`, `CMDK_SPINDLE_OFF`, `CMDK_SPINDLE_ON`.
- Driver flags `CMDK_OPEN`, `CMDK_SUSPEND`, `CMDK_TGDK_OPEN`.
- `CMDKUNIT(dev)` and `CMDKPART(dev)` minor decoding macros.

## Behavior And Integration

`struct cmdk` ties the common disk label/block layer (`cmlb`) to the target disk abstraction (`tgdk`) and bad-block handler (`bbh`). It records per-partition opens with bitmaps and layer counts, supports alternate-sector remap state, and tracks PM suspend/spindle state.

## Dependencies And Invariants

The minor layout reserves 6 low bits for partition number, yielding 64 partitions. `dk_open_reg` and `dk_open_exl` are `uint64_t`, matching that partition count. Alternate-sector fields are protected by `dk_bbh_mutex`; PM fields use `dk_pm_mutex` and `dk_suspend_cv`.

## Risks

Changing `CMDK_UNITSHF` changes device minor ABI interpretation. The structure embeds multiple synchronization domains; callers must use the documented locks around BBH and PM fields. Open bitmaps assume partition numbers are below `CMDK_MAXPART`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmpkt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmpkt.h

## Scope

Complete file read, 80 lines. This header defines the common command packet exchanged between DKTP target and controller layers.

## Public Surface

It exports `struct cmpkt`, with fields for:

- Generic controller, controller-private, and device-private pointers.
- Status block and command block pointers/lengths.
- Completion reason, callback, timeout, and flags.
- Associated `struct buf`, residual byte tracking, bytes left, bytes transferred in the current disk section.
- Starting sector, sectors left, retry count, target iodone callback, fault-recovery packet, private data, and pass-through command pointer.

It defines completion reasons `CPS_SUCCESS`, `CPS_FAILURE`, `CPS_CHKERR`, and `CPS_ABORTED`, plus flag `CPF_NOINTR`.

## Behavior And Integration

`cmpkt` is the central I/O command descriptor passed through controller ops, target disk ops, flow-control queues, and generic disk adapter helpers. The file provides layout and constants only.

## Dependencies And Invariants

The header assumes `opaque_t`, `daddr_t`, and `struct buf` are known through includers. Packet owners must keep status/command block lengths synchronized with their pointed data.

## Risks

Callbacks use old-style `void (*)()` prototypes, so type checking is weak. Multiple private pointers make ownership ambiguous unless each layer follows the DKTP contract. Sector and byte counters use `long`/`daddr_t`, so overflow behavior depends on platform width and request splitting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmpkt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/controller.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/controller.h

## Scope

Complete file read, 105 lines. This header defines the DKTP controller object abstraction and controller-operation dispatch macros.

## Public Surface

It exports:

- `struct ctl_ext`: controller type cookie, controller and target devinfo pointers, target number, and block size.
- `struct ctl_obj`: object data pointer, ops table, extension pointer, and embedded extension storage.
- `struct ctl_objops`: callbacks for packet allocation/free, DMA memory setup/free, I/O setup, transport, reset, abort, get/set capability, ioctl, and reserved slots.
- Access macros such as `CTL_DIP_CTL`, `CTL_DIP_DEV`, `CTL_GET_TYPE`, `CTL_GET_TARG`, and `CTL_GET_BLKSZ`.
- Dispatch macros `CTL_PKTALLOC`, `CTL_PKTFREE`, `CTL_MEMSETUP`, `CTL_MEMFREE`, `CTL_IOSETUP`, `CTL_TRANSPORT`, `CTL_ABORT`, `CTL_RESET`, and `CTL_IOCTL`.
- Transport results `CTL_SEND_SUCCESS`, `CTL_SEND_FAILURE`, and `CTL_SEND_BUSY`.

## Behavior And Integration

The target disk layer uses this object interface to allocate command packets, prepare buffers, send commands to hardware/SCSI transports, and issue reset/abort/ioctl operations without binding to a concrete controller.

## Dependencies And Invariants

The object pointer must be a valid `struct ctl_obj *`, with `c_ext` and `c_ops` initialized. `struct cmpkt`, `struct buf`, `dev_info_t`, `opaque_t`, and callback types must come from included context.

## Risks

`CTL_GET_LKARG` references `c_lkarg`, but `struct ctl_ext` in this header does not define that field. Code using that macro must rely on a different historical layout or will fail to compile. All dispatch macros are unchecked direct function-pointer calls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/controller.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadev.h

## Scope

Complete file read, 41 lines. This is an umbrella include header for DKTP direct-access device code.

## Public Surface

It includes:

- `sys/dktp/controller.h`
- `sys/dktp/cmpkt.h`
- `sys/dktp/gda.h`

It declares no new structures, macros, functions, or constants.

## Behavior And Integration

This header groups the controller, command-packet, and generic disk adapter interfaces under one include for older direct-access disk code.

## Dependencies And Invariants

All meaningful API surface is inherited from the included DKTP headers.

## Risks

Because it re-exports several DKTP headers transitively, including it can hide direct dependencies and increase compile coupling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadk.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadk.h

## Scope

Complete file read, 141 lines. This header defines the direct-access disk target implementation state and function prototypes for the `dadk` target disk object.

## Public Surface

It includes `sys/dktp/tgcom.h` and defines:

- `struct dadk`: target disk state including backpointers, logical/physical geometry, removable/read-only/CD-ROM/cache flags, sector/block shifts, BBH/flow/controller objects, embedded `tgcom_obj`, media state, synchronization, watcher-thread count, kstats, and command-count lock.
- `DAD_SECSIZ` alias to physical sector size.
- Timing/retry constants `DADK_BSY_TIMEOUT`, `DADK_IO_TIME`, `DADK_FLUSH_CACHE_TIME`, `DADK_RETRY_COUNT`, and `DADK_SILENT`.
- `PKT2DADK(pktp)`.
- Packet action codes `COMMAND_DONE`, `COMMAND_DONE_ERROR`, `QUE_COMMAND`, `QUE_SENSE`, and `JUST_RETURN`.
- `dadk_errstats_t` kstat layout.
- Prototypes for init/free/probe/attach/open/close/ioctl/strategy/geometry/I/O-buffer/dump/media/inquiry/cleanup and command-count routines.

## Behavior And Integration

`dadk` implements the `tgdk_objops` target disk contract declared in `tgdk.h`. It bridges SCSI direct-access devices to common disk operations, manages removable media state, coordinates with flow-control and controller objects, and exposes disk error statistics.

## Dependencies And Invariants

It depends on SCSI, DKIO media state, `tgdk_geom`, `tgdk_iob`, kstat, mutex/condition variable, and `struct buf` types from surrounding kernel headers. Media state and watcher thread counters are protected by `dad_mutex`/`dad_state_cv`; command count is protected by `dad_cmd_mutex`.

## Risks

The header declares `static void dadk_watch_thread(struct dadk *dadkp);`; a `static` prototype in a header gives each including translation unit an internal declaration and is only safe if used consistently with implementation visibility. Bitfields encode device attributes compactly but are not ABI-stable across compilers if serialized.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadkio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadkio.h

## Scope

Complete file read, 236 lines. This header defines ioctl command numbers, command codes, error/status values, and request structures for the direct-coupled disk driver interface.

## Public Surface

It defines DIOCTL commands for geometry, physical geometry, model, serial, raw read/write command, and write-cache-enabled state. It conditionally defines `blkaddr_t`/`blkaddr32_t` like `dklabel.h`.

The ABI structures include:

- `dadk_ioc_string_t` and `_SYSCALL32` `dadk_ioc_string32_t`.
- `struct dadkio_derr`: driver error action/severity pair.
- `struct dadkio_status` and `_SYSCALL32` `struct dadkio_status32`.
- `struct dadkio_rwcmd` and `_SYSCALL32` `struct dadkio_rwcmd32`.

It defines direct command codes `DCMD_READ` through `DCMD_FLUSH_CACHE`, driver error codes `DERR_*`, raw read/write command codes, flags such as `DADKIO_FLAG_SILENT`, `DADKIO_ERROR_INFO_LEN`, and `DADKIO_STAT_*` status values.

## Behavior And Integration

This is a shared ioctl ABI used by disk drivers and user/kernel ioctl handlers. `dadkio_rwcmd` carries a command, flags, target block, user buffer, byte length, and status output. The 32-bit variants preserve compatibility for 32-bit processes on 64-bit kernels.

## Dependencies And Invariants

ABI correctness depends on fixed field widths, `_SYSCALL32` conversions, `blkaddr_t` selection, and the 128-byte additional error-info buffer. User pointers are represented as `caddr_t` or `caddr32_t`.

## Risks

The command namespace is old and mixes disk and CD-ROM operations. Callers must validate `buflen`, `bufaddr`, block range, direction, and status copyout carefully. `uint_t buflen` can be narrower than `size_t`, so large I/O requests must be bounded.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/dadkio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fctypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fctypes.h

## Scope

Complete file read, 79 lines. This header defines shared data structures for DKTP flow-control implementations.

## Public Surface

It defines:

- Flow-control maximum outstanding counts `DMULT_MAXCNT` and `DUPLX_MAXCNT`.
- Field aliases for common data embedded in specific flow-control structures.
- `struct fc_data_cmn`: kstat pointer, mutex, and target common object pointer.
- `struct fc_data`: common state, flags, outstanding count, disk queue head, and queue object pointer.
- Disk queue aliases `ds_actf`, `ds_actl`, `ds_waitcnt`, and `ds_bp`.
- `struct fc_que`: queue chain entry with queue object, buffer, current outstanding count, and max count.
- `struct duplx_data`: duplex read and write queues plus common state.

## Behavior And Integration

Flow-control implementations use these structures to track outstanding I/O, queue buffers, and expose kstats while cooperating with queue objects and target common transport.

## Dependencies And Invariants

The header assumes `kstat_t`, `kmutex_t`, `opaque_t`, `struct diskhd`, and `struct buf` are available. Field aliases depend on exact embedded member names.

## Risks

The field-alias macros make refactoring hazardous. Queue counters are `short`, so implementations must honor the small maximum-count constants and not allow unbounded outstanding I/O.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fctypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fdisk.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fdisk.h

## Scope

Complete file read, 173 lines. This header defines the x86/AT386 MBR/fdisk partition sector layout and partition type constants.

## Public Surface

It defines BIOS CHS bounds `MAX_SECT`, `MAX_CYL`, and `MAX_HEAD`; MBR constants `BOOTSZ`, `FD_NUMPART`, `MBB_MAGIC`, `DEFAULT_INTLV`, `MINPSIZE`, and `TSTPAT`.

It exports:

- `struct ipart`: one 16-byte fdisk partition entry with boot flag, CHS fields, system id, relative start sector, and sector count.
- Boot flags `NOTACTIVE` and `ACTIVE`.
- Many `systid` constants for DOS, Windows, Linux, Solaris, BSD, EFI, and other partition types.
- `MAXDOS`.
- `struct mboot`: master boot block with 440-byte boot code, Vista disk-id-compatible fields, four partition slots as bytes, and signature.
- On x86/amd64: `FDISK_PART_TABLE_START` and `MAX_EXT_PARTS`; otherwise `MAX_EXT_PARTS` is 0.

## Behavior And Integration

This header describes sector 0 layout for MBR-partitioned disks. Unix slices are not defined here; they are obtained from the VTOC inside the Solaris partition.

## Dependencies And Invariants

The `BOOTSZ` value of 440 intentionally preserves the Windows Vista disk ID area. `struct mboot.parts` is a byte array to avoid compiler alignment changes in the partition table.

## Risks

MBR layout is byte-exact. Any attempt to embed `struct ipart parts[4]` directly in `struct mboot` can break alignment. CHS constants contain historical fence values and must not be treated as modern capacity limits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/fdisk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/flowctrl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/flowctrl.h

## Scope

Complete file read, 72 lines. This header defines the DKTP flow-control object interface.

## Public Surface

It exports:

- `struct flc_obj`: object data pointer plus operation table.
- `struct flc_objops`: callbacks for init, free, enqueue, dequeue, kstat start, kstat stop, and reserved slots.
- Factory prototypes `dsngl_create()`, `dmult_create()`, `duplx_create()`, and `adapt_create()`.
- Dispatch macros `FLC_INIT`, `FLC_FREE`, `FLC_ENQUE`, `FLC_DEQUE`, `FLC_START_KSTAT`, and `FLC_STOP_KSTAT`.

## Behavior And Integration

The flow-control object mediates buffering and outstanding I/O limits between target common transport and queue objects. Different factories create single, multiple, duplex, or adapter-specific flow-control policies.

## Dependencies And Invariants

The interface assumes `opaque_t`, `struct buf`, and the DKTP object model are available. Objects must have initialized `flc_data` and `flc_ops`.

## Risks

Factory prototypes are old-style declarations without explicit parameter lists. Dispatch macros are unchecked and can call null or mismatched callbacks if object initialization fails.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/flowctrl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/gda.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/gda.h

## Scope

Complete file read, 70 lines. This header defines generic disk adapter helpers and logging/error severity constants.

## Public Surface

It defines:

- `GDA_RTYCNT` retry count.
- `GDA_BP_PKT(bp)` mapping from `buf.av_back` to `struct cmpkt *`.
- Kernel prototypes for inquiry string fill, logging, error message formatting, packet preparation, and packet/free cleanup.
- Geometry packing helpers `GDA_GETGEOM_HEAD`, `GDA_GETGEOM_SEC`, and `GDA_SETGEOM`.
- `GDA_KMFLAG(callback)` converting DMA callback sleep policy to `KM_SLEEP` or `KM_NOSLEEP`.
- Error/severity classes `GDA_ALL`, `GDA_UNKNOWN`, `GDA_INFORMATIONAL`, `GDA_RECOVERED`, `GDA_RETRYABLE`, and `GDA_FATAL`.

## Behavior And Integration

Generic disk adapter code uses this header to connect buffers to command packets, log SCSI/DKTP errors, prepare packets with DMA allocation policy, and encode simple head/sector geometry in a single integer.

## Dependencies And Invariants

The kernel section depends on `dev_info_t`, `struct scsi_device`, `struct cmpkt`, `struct buf`, DDI DMA callback constants, and kernel allocation flags.

## Risks

`GDA_BP_PKT` stores packet linkage in `buf.av_back`, which must not conflict with other queue linkage usage. Geometry packing only retains an 8-bit head and 8-bit sector value, with head shifted into bits 16-23.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/gda.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/quetypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/quetypes.h

## Scope

Complete file read, 44 lines. This header defines the common queue backing data used by DKTP queue implementations.

## Public Surface

It defines:

- `struct que_data`: a queue mutex and `struct diskhd` queue head.
- `q_cnt` alias to `q_tab.b_bcount`.

## Behavior And Integration

Queue implementations use `que_data` to hold a synchronized disk buffer queue and count pending entries via the `diskhd` count field.

## Dependencies And Invariants

The header assumes `kmutex_t` and `struct diskhd` are visible. The `q_cnt` macro depends on the internal use of `b_bcount` as a queue count.

## Risks

Overloading `diskhd.b_bcount` as `q_cnt` is convention-based. Callers must hold `q_mutex` consistently when mutating queue state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/quetypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/queue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/queue.h

## Scope

Complete file read, 64 lines. This header defines the DKTP queue object interface.

## Public Surface

It exports:

- `struct que_obj`: queue data pointer and operation table.
- `struct que_objops`: init, free, insert, delete callbacks, and reserved slots.
- Factory prototypes `qfifo_create()`, `qmerge_create()`, `qsort_create()`, and `qtag_create()`.
- Dispatch macros `QUE_INIT`, `QUE_FREE`, `QUE_ADD`, and `QUE_DEL`.

## Behavior And Integration

The queue object abstracts disk buffer queue policy: FIFO, merge, sorted, or tagged variants. Flow-control and target disk code call the macros without knowing the concrete queue implementation.

## Dependencies And Invariants

The interface assumes `struct que_data`, `struct buf`, and DKTP object conventions. Objects must have valid `que_data` and `que_ops`.

## Risks

Old-style factory prototypes and unchecked callback dispatch provide weak compile-time safety. Queue implementations must agree on ownership and locking of `struct que_data`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgcom.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgcom.h

## Scope

Complete file read, 62 lines. This header defines the DKTP target-common transport object interface.

## Public Surface

It exports:

- `struct tgcom_obj`: common transport data pointer and operation table.
- `struct tgcom_objops`: init, free, packet creation/submission, transport, and reserved callbacks.
- Dispatch macros `TGCOM_INIT`, `TGCOM_FREE`, `TGCOM_PKT`, and `TGCOM_TRANSPORT`.

## Behavior And Integration

`tgcom` is the target-common layer that flow-control and disk target code use to convert buffers into command packets and send them into lower transport/controller code.

## Dependencies And Invariants

It assumes `opaque_t`, `struct buf`, `caddr_t`, and callback conventions. A `tgcom_obj` must be fully initialized before dispatch.

## Risks

Callbacks use unchecked function pointers and old-style callback signatures. Incorrect object wiring can corrupt the I/O path because `TGCOM_PKT` sits between buffers and transport submission.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgcom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgdk.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgdk.h

## Scope

Complete file read, 175 lines. This header defines the target disk object interface for DKTP disk drivers.

## Public Surface

It exports:

- `struct tgdk_ext`: removable/read-only flags, node type, and controller type.
- `struct tgdk_obj`: target object data, operations, extension pointer, and embedded extension storage.
- `struct tgdk_iob`: I/O-buffer handle with buffer, logical block, transfer length, physical sector, byte count/offset, and flags.
- `IOB_BPALLOC` and `IOB_BPBUFALLOC`.
- `struct tgdk_geom`: cylinder/head/sector/sector-size/capacity geometry.
- `struct tgdk_objops`: callbacks for lifecycle, probe/attach/open/close/ioctl/strategy, geometry, I/O-buffer allocation/free/transfer, dump, physical geometry, bad-block object setup, media check, inquiry, cleanup, and reserved slot.
- `dadk_create()` factory prototype.
- Attribute and dispatch macros for all target-disk operations.
- `LBLK2SEC()`, `SETBPERR`, and `DK_MAXRECSIZE`.

## Behavior And Integration

This is the main abstract target disk API used by common disk code. `cmdk` can call `TGDK_*` macros to perform disk operations through a concrete implementation such as `dadk`.

## Dependencies And Invariants

The object pointer must be a valid `struct tgdk_obj *`; `tg_ext` and `tg_ops` must be initialized. Geometry and capacity fields must use consistent sector sizes and shifts. `DK_MAXRECSIZE` caps I/O record size at 256 KiB.

## Risks

`TGDK_INIT` and `TGDK_INIT_X` both dispatch to `tg_init` but with different argument counts, while the declared function pointer takes six arguments; the extended macro relies on implementation/prototype compatibility outside this header. All dispatch macros bypass type and null checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgdk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dl.h

## Scope

Complete file read, 67 lines. This header defines a portable two-word long arithmetic type and related routines.

## Public Surface

It includes `sys/isa_defs.h` and defines `dl_t` as a struct containing high and low words. Field order changes based on `_LONG_LONG_LTOH`.

It declares arithmetic helpers:

- `ladd`, `lsub`, `lmul`, `ldivide`
- `lshiftl`
- `llog10`
- `lexp10`

It also declares constants `lzero`, `lone`, and `lten`.

## Behavior And Integration

This is an ABI/support header for code that uses a software double-length integer representation rather than native `long long`.

## Dependencies And Invariants

Correct binary representation depends on endian/word-order macros. The function implementations are elsewhere.

## Risks

The type is layout-sensitive. Mixing objects compiled with different ISA definitions would break interpretation. It is old-style support code and should not be extended without checking all consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld.h

## Scope

Complete file read, 466 lines. This header defines the Data-Link Driver ioctl ABI plus kernel-only DLD capability and entry point interfaces.

## Public Surface

The shared ioctl surface includes DLD module metadata, driver property names, ioctl command numbers, and structures for:

- link attributes, VLAN attributes, physical attributes
- secure object set/get/unset
- VLAN create/delete
- door server state
- link rename and zone id data
- autopush configuration
- MAC address enumeration
- flow add/remove/modify/walk and flow info
- usage logging
- MAC property get/set
- hardware group enumeration
- transceiver get/read
- LED get/set

The file uses packing pragmas on platforms where 64-bit and 32-bit long-long alignment differs, preserving ioctl layout compatibility.

Under `_KERNEL`, it defines DLD capability constants, enable/disable/query values, `dld_capab_func_t`, direct transmit/receive capability structure, polling capability structure, LSO capability flags/structure, driver entry point prototypes, stream open/close/private hooks, autopush, and flow management functions.

## Behavior And Integration

Userland tools and kernel modules use the ioctl structures to control GLDv3 data links through `/dev/dld`. Kernel IP/DLD integration uses capability negotiation for direct paths, polling/softring behavior, and LSO.

## Dependencies And Invariants

The header depends on `sys/mac.h`, `sys/mac_flow.h`, STREAMS, DLD ioctl command macros from `dld_ioc.h`, and datalink identifiers. The comment explicitly requires identical structure layout and size in ILP32 and LP64.

## Risks

Flexible trailing data in `dld_ioc_macprop_t.pr_val[1]` requires careful allocation and copyin/out sizing. Ioctl command slots are historically reserved or removed; reusing them can break compatibility. Function pointers in capability structures are stored as `uintptr_t`, so consumers must cast carefully.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_impl.h

## Scope

Complete file read, 352 lines. This is the kernel-private implementation header for DLD stream state and helper macros.

## Public Surface

It defines control minor names/numbers, DLD stream type flags, stream modes (`DLD_UNITDATA`, `DLD_FASTPATH`, `DLD_RAW`), and passive-state enum values.

The central type is `struct dld_str_s`, with fields for major/minor, PPA, STREAMS queues, stream type, DLPI state/style/SAP, MAC handles, promiscuity handles, MAC info, priority, notification state, mode, native/poll/direct/LSO state, passive state, flow-control dummy message, pending DLPI queue state, DLS linkage, multicast state, rx callback, active counts, task queue list, private driver data, lowlink and non-IP flags.

It provides data-thread count macros `DLD_DATATHR_INC` and `DLD_DATATHR_DCR`, DLD string/protocol/flow/drv function prototypes, option flags, autopush state type `dld_ap_t`, queue-full macros `DLD_SETQFULL` and `DLD_CLRQFULL`, `DLD_TX`, and debug macro `DLD_DBG`.

## Behavior And Integration

DLD implementation files use this header to manage each open DLPI stream and its interaction with MAC clients, DLS link state, direct transmit, polling, and flow control.

## Dependencies And Invariants

The header documents protection for each field: write-once, serializer-protected, mutex/rwlock-protected, or reference protected. Correct behavior depends on honoring those locking annotations.

## Risks

`DLD_SETQFULL` and `DLD_CLRQFULL` manipulate STREAMS queue state and `ds_tx_flow_mp` under `ds_lock`; misuse can lose flow-control messages. `DLD_DATATHR_DCR` assumes the count is positive and broadcasts only on zero. This is private kernel state and should not be used by external modules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_ioc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_ioc.h

## Scope

Complete file read, 116 lines. This header defines GLDv3 ioctl command numbering and kernel registration of ioctl handlers.

## Public Surface

It defines:

- `DLD_CONTROL_DEV` as `/dev/dld`.
- `DLD_IOC_CMD(modid, cmdid)` and `DLD_IOC_MODID(cmd)`.
- Module ids for DLD, aggregation, VNIC, simnet, IP tunnel, bridge, IB partition, and overlay.
- Convenience command macros `DLDIOC`, `AGGRIOC`, `VNICIOC`, `SIMNETIOC`, `IPTUNIOC`, `BRIDGEIOC`, `IBPARTIOC`, and `OVERLAYIOC`.

Under `_KERNEL`, it defines:

- `dld_ioc_func_t` and `dld_ioc_priv_func_t`.
- `dld_ioc_info_t`, with command, flags, argument size, handler, and privilege hook.
- Copy flags `DLDCOPYIN`, `DLDCOPYOUT`, `DLDCOPYINOUT`.
- `DLDIOCCNT(l)`.
- `dld_ioc_register()` and `dld_ioc_unregister()`.

## Behavior And Integration

GLDv3 modules register their ioctl handlers with DLD by module id. DLD uses `di_argsize` and copy flags to perform common copyin/copyout before invoking module callbacks.

## Dependencies And Invariants

The 32-bit module id and command id split is fixed at 16 bits each. Modules must use unique module ids and command ids to avoid collisions.

## Risks

Incorrect `di_argsize` or copy flags can cause truncated copies, overreads, or ABI mismatch. Registration lifecycle must match module loading/unloading to avoid dangling handler pointers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_ioc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dlpi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dlpi.h

## Scope

Complete file read, 1,632 lines. This header defines the Data Link Provider Interface, version 2.0, plus illumos/Solaris-specific DLPI extensions.

## Public Surface

The file exports:

- Sun DLPI ioctls such as `DLIOCRAW`, `DLIOCNATIVE`, `DLIOCMARGININFO`, `DLIOCIPNETINFO`, `DLIOCLOWLINK`, and `DLIOCHDRINFO`.
- `dl_ipnetinfo_t`.
- DLPI version constants.
- Primitive numbers for local management, Solaris notifications/capabilities/control, connectionless service, connection-oriented service, acknowledged connectionless service, XID/TEST, physical address, and statistics.
- DLPI state constants, error codes, media types, provider service modes, provider styles, originators, disconnect/reset reasons, acknowledged CL status masks, service classes, address types, flags, automatic XID/TEST flags, bind classes, promiscuous modes, and notification bits.
- QOS component structures, QOS range/selection structures, and `union DL_qos_types`.
- Capability definitions for checksum offload, zero-copy, DLD, VRRP, module-id wrapping, and related version/flag constants.
- STREAMS message layout typedefs for every DLPI primitive.
- `union DL_primitives`, allowing primitive inspection via the first `dl_primitive` field.
- `DL_*_SIZE` macros for each primitive structure.
- Kernel helper prototypes for building acknowledgments, checking module ids, attaching/binding/querying through LDI handles, and stringifying errors/primitives/MAC types.

## Behavior And Integration

DLPI providers and consumers use these definitions to exchange typed STREAMS protocol messages. Most message structures use offset/length pairs to refer to variable data that follows the fixed header in the same message block.

The capability section supports negotiation through `DL_CAPABILITY_REQ` and `DL_CAPABILITY_ACK`, including checksum offload and DLD fast function-call negotiation.

## Dependencies And Invariants

The header depends on `sys/types.h` and `sys/stream.h`. All primitive structures rely on the first member being `dl_primitive`. Offset/length fields must be validated against actual message size by consumers. Reserved/growth fields are expected to be zero.

## Risks

This is a broad ABI header: changing constant values, structure fields, or sizes can break drivers, STREAMS modules, and userland. Variable-length tail data is a common parsing risk. Kernel-only DLD/VRRP capability structures are hidden under `_KERNEL`, so code shared with userland must not assume they are always visible.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dlpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls.h

## Scope

Complete file read, 160 lines. This header defines the public kernel-facing Data-Link Services interface and PPA/minor conversion helpers.

## Public Surface

It defines `DLS_MODULE_NAME`, `DLS_INFO`, PPA conversion macros `DLS_PPA2INST`, `DLS_PPA2VID`, `DLS_PPA2MINOR`, `DLS_VIDINST2PPA`, and `DLS_MINOR2INST`.

Under `_KERNEL`, it defines `DLS_MAX_PPA`, `DLS_MAX_MINOR`, receive callback type `dls_rx_t`, forward handle types, SAP/promiscuity constants, and prototypes for DLS open/close/bind/unbind, promiscuous and multicast control, header construction, RX callback management, device-network open/close/rebuild/rename/create/destroy/recreate/hold/release/property wait/query functions, link visibility, management door setup, management create/destroy/update/get functions, iteration, and MAC-name-to-link-id lookup.

## Behavior And Integration

DLD uses DLS to bind streams to MAC-backed data links, manage VLAN PPA mapping, multicast/promiscuous state, and integrate with data-link management state.

## Dependencies And Invariants

The PPA mapping uses `ppa = vid * 1000 + inst`; valid instances are 0-999. Minor numbers are instance plus one.

## Risks

PPA arithmetic encodes VLAN and instance in a decimal-style range, so values outside `DLS_MAX_PPA` can alias or exceed expected minor ranges. Most prototypes are kernel-only and depend on MAC/DLS lifetime rules outside this header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_impl.h

## Scope

Complete file read, 137 lines. This is the private DLS implementation header for link, multicast, and stream-head state.

## Public Surface

It defines:

- `dls_multicst_addr_t`: linked multicast address entry.
- `struct dls_link_s`: link name, DDI instance, MAC handles, notification handle, MAC info, reference counts, stream hash, active counts, unknown packet count, zone ownership/reference, tag mode, and non-IP count.
- `dls_head_t`: stream list head with lock, reference, hash key, condition variable, and removal flag.
- Global `i_dls_link_hash`.
- Internal link lifecycle, hold/release, add/remove, zone, devinfo/dev, active-state, kstat, devnet link hold/open/release, initialization/finalization, transmit loop, receive filtering, promiscuous receive, active set/clear, management init/fini, and physical-dev lookup prototypes.

## Behavior And Integration

DLS implementation files use these structures to map devnet links to MAC clients, maintain per-link stream membership, perform receive acceptance for normal/promiscuous/loopback paths, and expose link kstats.

## Dependencies And Invariants

The locking annotations in field comments are part of the contract: serializer, modhash lock, atomic, and zone/ref rules must be respected. The multicast address size is `MAXMACADDRLEN`.

## Risks

This is private state shared across DLS source files. Hash and reference management errors can leak or prematurely free link state. Zone ownership/reference fields require careful updates during link reassignment and destruction.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_mgmt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_mgmt.h

## Scope

Complete file read, 242 lines. This header defines data-link management classes, media filters, attributes, and the door upcall ABI used between kernel DLS and `dlmgmtd`.

## Public Surface

It defines `datalink_class_t` values for physical links, VLANs, aggregations, VNICs, etherstubs, simnet, bridge, IP tunnel, partition, overlay, and miscellaneous links, plus `DATALINK_CLASS_ALL`.

It defines `datalink_media_t`, `DATALINK_ANY_MEDIATYPE`, and `DATALINK_MEDIA_ACCEPTED()`. It defines link attribute names `FPHYMAJ`, `FPHYINST`, and `FDEVNAME`, and door paths `DLMGMT_TMPFS_DIR` and `DLMGMT_DOOR`.

Door command constants cover create, getattr, destroy, getname, getlinkid, getnext, update, link property init, and set zone id. Flags describe active, persistent, and transient links.

It exports door argument and return structures for create/destroy/update/getattr/getname/getlinkid/getnext/linkprop-init/setzoneid and corresponding return values.

## Behavior And Integration

The kernel uses this ABI to ask the data-link management daemon to create, destroy, update, find, iterate, and zone data links. Several structures include explicit padding to keep layout identical on amd64 and i386.

## Dependencies And Invariants

The door protocol depends on the first `ld_cmd`/`lr_err` fields being readable for dispatch and status. Structure sizes must remain 32-bit/64-bit compatible. `DATALINK_MEDIA_ACCEPTED()` interprets the high 32 bits as flags and low 32 bits as media value.

## Risks

Door ABI changes must be coordinated with `dlmgmtd`. String fields are fixed-size; callers must enforce termination and bounds. The macro name `lr_paddding` is misspelled in a comment only, but padding fields are required for ABI stability.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_mgmt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dnlc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dnlc.h

## Scope

Complete file read, 383 lines. This header defines the Directory Name Lookup Cache and large-directory cache interfaces.

## Public Surface

For the standard DNLC it defines:

- `ncache_t`: hash-chain entry mapping parent vnode and name to target vnode.
- `NCACHE_SIZE(namelen)`.
- `nc_hash_t`: hash bucket with lock.
- Deprecated `struct ncstats`.
- Preferred `struct nc_stats` kstat counters shared with directory caching.
- `DNLCHASH(name, dvp, hash, namlen)`.

Under `_KERNEL` or `_FAKE_KERNEL`, it declares `ncsize`, `negative_cache_vnode`, `DNLC_NO_VNODE`, and DNLC functions for init, enter, update, lookup, purge, purge by vnode/vfs/vnodeops, remove, and cache reduction.

For directory caching it defines:

- `dcfree_t`, `dcentry_t`, `DCENTTRY_SIZE()`, `dircache_t`, `dcanchor_t`, and `dchead_t`.
- Kernel-only `dcret_t` result enum.
- Directory cache functions for start, add entry/free space, complete, purge, lookup, update, remove entry/free space, anchor init/fini.

## Behavior And Integration

The standard DNLC caches recent parent-vnode/name to vnode mappings, including negative entries via `DNLC_NO_VNODE`. The directory cache supports whole-directory caching for large directories with filesystem-supplied handles for entries and free space.

## Dependencies And Invariants

`ncache_t.namlen` and `dcentry_t.de_namelen` are `uchar_t`, so names must fit below 256 bytes excluding null. `DNLCHASH` asserts this. `dcanchor_t.dca_lock` protects the cache pointer.

## Risks

The macro `DCENTTRY_SIZE` appears misspelled with three `T` characters; callers must use the actual exported spelling. Directory caches can be purged due to memory pressure at any time, so filesystems must treat `DNOCACHE`/`DNOMEM` as normal outcomes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dnlc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door.h

## Scope

Complete file read, 333 lines. This header defines illumos door lightweight RPC attributes, data structures, syscall subcodes, and kernel interfaces.

## Public Surface

It defines door creation/status attributes such as `DOOR_UNREF`, `DOOR_PRIVATE`, `DOOR_REFUSE_DESC`, `DOOR_NO_CANCEL`, `DOOR_LOCAL`, `DOOR_REVOKED`, and related masks. It defines descriptor attributes `DOOR_DESCRIPTOR`, kernel-only `DOOR_HANDLE`, and `DOOR_RELEASE`, plus internal flags and parameter ids.

Non-assembly builds get:

- `door_ptr_t`, `door_id_t`, and `door_attr_t`.
- Kernel-only opaque `door_handle_t`.
- `door_desc_t`, `door_info_t`, `door_cred_t`, `door_arg_t`, 32-bit `door_arg32_t`, `door_results`, 32-bit `door_results32`, `door_return_desc_t`, and 32-bit variant.
- Kernel-only `door_node_t`, vnode conversion macros, door dispatch/revoke/fork/bind helpers, globals, and in-kernel door API functions.

It ends with door syscall subcodes: create, revoke, info, call, bind, unbind, unref, credentials, return, getparam, and setparam.

## Behavior And Integration

Doors provide process-local RPC via file descriptors or kernel handles. `door_arg_t` carries request/result data and descriptors; `door_info_t` exposes target procedure/cookie/attributes/unique id. Kernel `door_node_t` ties doors to vnodes, target process, active invocation counts, server pools, and parameter limits.

## Dependencies And Invariants

On amd64 with 32-bit alignment differences, `door_desc_t` and `door_info_t` are packed to avoid special copy conversions. `DOOR_CREATE_MASK`, `DOOR_KI_CREATE_MASK`, and `DOOR_ATTR_MASK` define accepted flag sets.

## Risks

Descriptor passing and result buffers require strict copyin/copyout validation. `door_ptr_t` stores user pointers as 64-bit integer values for ABI stability. Kernel door APIs are marked private and may change incompatibly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_data.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_data.h

## Scope

Complete file read, 126 lines. This kernel-only header defines per-thread data used during door invocations.

## Public Surface

Under `_KERNEL`, it defines:

- `door_layout_t`: stack layout locations for descriptors, data, door info, results, and final stack pointer.
- `door_upcall_t`: credential and maximum reply data/descriptor limits for upcalls.
- `door_client_t`: per-client invocation args, upcall information, temporary buffer, file pointer array, error, condition variable, and state flags.
- `door_server_t`: caller thread, server list, active door, pool, saved layout/stack info, condition variable, and state flags.
- `door_data_t`: combined client/server per-thread data.
- `DOOR_CLIENT()` and `DOOR_SERVER()` accessors.
- Thread hold/release macros `DOOR_T_HELD`, `DOOR_T_HOLD`, and `DOOR_T_RELEASE`.
- `DOOR_ROUND` buffer-size rounding value.

## Behavior And Integration

Each door call affects client state on one thread and server state on another. This split allows a server thread to make nested door calls without clobbering its server-side invocation context.

## Dependencies And Invariants

The header depends on `sys/door.h`, `sys/thread.h`, and `sys/file.h` for kernel builds. Hold/release macros assert correct state and broadcast on release.

## Risks

This is private scheduler/IPC state. Incorrect hold/release pairing can leave threads stuck or allow stack/result teardown too early. Buffer rounding reduces overflow frequency but does not remove the need for result-size checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_impl.h

## Scope

Complete file read, 49 lines. This small header holds common door implementation definitions shared by `sys/door.h` and `sys/proc.h`.

## Public Surface

It includes `sys/condvar.h` and defines:

- `door_pool_t`: a list of server threads plus a condition variable.

## Behavior And Integration

`door_pool_t` is embedded in door-related kernel structures to manage private or process-associated door server thread pools.

## Dependencies And Invariants

The `dp_threads` member points to `_kthread` objects, and `dp_cv` coordinates waiters on pool changes.

## Risks

This type is intentionally minimal and shared across core process and door headers. Changes affect both door IPC and process structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_impl.h -->