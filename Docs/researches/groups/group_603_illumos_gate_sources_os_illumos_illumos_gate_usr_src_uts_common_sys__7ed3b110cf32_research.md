# Group Research: group_603_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__7ed3b110cf32

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi.h

Core LSI MPT MPI v1.x protocol header for illumos MPT storage drivers.

Key responsibilities:
- Defines MPI/header version constants, IOC states, fault codes, PCI doorbell/register offsets, interrupt bits, and message-frame descriptor fields.
- Defines message function IDs for SCSI, IOC, config, FC, RAID, SAS, LAN, inband, diagnostic, reset, and handshake operations.
- Defines scatter/gather element layouts for 32-bit/64-bit simple SGEs, chain SGEs, transaction-context SGEs, and unions used in request frames.
- Provides SGE flag, length, chain-offset, and context-reply manipulation macros.
- Defines common request/reply message headers, common IOC status codes, IOC log-info type masks, and SMP passthrough request/reply structures.

Dependencies:
- Uses fixed-width integer types and is consumed by the sibling MPT headers for config, IOC, initiator, and RAID message formats.

Notable risks:
- This is hardware/firmware ABI. Struct layout, field widths, bit masks, and magic constants must match LSI MPI firmware exactly.
- Several macros mutate fields with read-modify-write semantics; callers must avoid accidental flag/length accumulation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_cnfg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_cnfg.h

MPT MPI configuration-page ABI header for adapter, port, device, RAID, LAN, and SAS topology configuration.

Key responsibilities:
- Defines generic and extended config page headers, config request/reply messages, config actions, page attributes, page types, extended page types, and page-address encodings.
- Defines manufacturing pages for chip, board, VPD, hardware settings, inquiry data, integrated RAID settings, base WWID, and product-specific data.
- Defines IO Unit and IOC pages for adapter identity, BIOS flags, GPIO, reply coalescing, EEDP, RAID volume/physical disk inventories, and enclosure processors.
- Defines SCSI port/device pages for physical capabilities, termination/scanning/init policy, negotiated/requested parameters, and domain validation controls.
- Defines Fibre Channel port/device pages for WWN/port identity, topology, speed, persistent targets, aliases, statistics, symbolic names, and attached-node data.
- Defines RAID volume and physical disk config pages, including volume status/settings, disk inquiry data, error data, hot spare pools, and multi-path physical disk paths.
- Defines LAN and inband pages.
- Defines SAS IO Unit, expander, device, and PHY extended pages for link rates, persistent mappings, discovery state, enclosure handles, SAS addresses, device handles, topology, routing, and PHY error counters.

Dependencies:
- Relies on types and SGE/version definitions from `mpi.h`.
- Some FC protocol flag macros refer to IOC port-facts protocol constants defined in `mpi_ioc.h`.

Notable risks:
- Many pages use compile-time one-element arrays with comments requiring callers to inspect `Header.PageLength` or `ExtPageLength` at runtime.
- Constants encode firmware NVRAM and topology contracts; changing values or packing would break adapter configuration.
- The file intentionally contains legacy and newer-page definitions together, so consumers must use page versions and lengths defensively.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_cnfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_init.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_init.h

MPT MPI SCSI initiator message header.

Key responsibilities:
- Defines SCSI I/O request and reply frames, including target/bus, CDB, LUN, control bits, data length, sense buffer address, SGL, transfer count, sense count, task tag, and response info.
- Defines SCSI I/O message flags for sense buffer width/location.
- Defines LUN addressing masks, data direction flags, task attribute flags, and task-management bits in the SCSI I/O control word.
- Defines SCSI status codes, SCSI state flags, and response-info values.
- Defines SCSI task management request/reply frames and task types for abort, reset, and LUN reset operations.
- Defines simple enclosure processor request/status message support.

Dependencies:
- Uses `sge_io_union_t` and common function/status constants from `mpi.h`.

Notable risks:
- Driver command construction must keep CDB length, sense buffer length/addressing, control direction, and SGL contents consistent.
- Task management values are firmware-facing and affect device reset/abort semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_init.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_ioc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_ioc.h

MPT MPI IOC management, discovery event, and firmware image ABI header.

Key responsibilities:
- Defines IOC init request/reply frames, WhoInit values, init flags, message/header version masks, reply frame sizing, high address fields, and host page buffer SGE.
- Defines IOC facts and port facts request/reply structures with firmware version, product ID, queue depths, chain depth, ports, devices/buses, capabilities, exceptions, and protocol flags.
- Defines port enable, event notification, and event acknowledge messages.
- Defines event IDs and event payloads for IOC state, SCSI/SAS device status changes, queue full, FC link/loop/logout, integrated RAID changes, SAS PHY link status, discovery errors, expander status changes, persistent table full, and log entries.
- Defines firmware download/upload messages, transaction context SGEs, firmware image headers, product/family ID masks, and extended image headers.

Dependencies:
- Uses SGE unions and common IOC status constants from `mpi.h`.
- Event payloads overlap semantically with RAID/config/SAS page definitions in sibling MPT headers.

Notable risks:
- Event payloads are variable and keyed by event ID; consumers must validate event length before casting.
- Firmware image/header constants are update-path ABI and mistakes can brick or misidentify adapter images.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_ioc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_raid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_raid.h

MPT integrated RAID action and physical-disk passthrough message header.

Key responsibilities:
- Defines RAID action request/reply frames for volume and physical disk management.
- Defines action values for status, create/delete/enable/disable/quiesce volumes, changing settings, online/offline/fail/replace physical disks, and activate/inactivate volume.
- Defines action data flags for synchronization and physical-disk retention/deletion behavior.
- Defines RAID action status values and a volume progress indicator structure.
- Defines SCSI I/O RAID passthrough request/reply frames targeting a physical disk number.

Dependencies:
- Uses `sge_simple_union_t` and `sge_io_union_t` from `mpi.h`.
- Mirrors SCSI I/O control/status patterns from `mpi_init.h`.

Notable risks:
- RAID actions can be destructive; driver control paths must validate action, volume/disk identifiers, and action data.
- Passthrough requests bypass logical volume abstraction and require strict sense/SGL handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_raid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msacct.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msacct.h

Microstate accounting constants for LWPs and CPUs.

Key responsibilities:
- Defines LWP microstates for user, system, trap, user/kernel page faults, user lock wait, sleep, CPU wait, and stopped states.
- Defines `NMSTATES` as the number of LWP microstates, with a comment warning it must not exceed the `siginfo` size constraint.
- Defines CPU microstates for user, system, idle, and disabled.
- Defines `NCMSTATES` as 3 because disabled CPUs are not accounted as a normal CPU accounting state.

Dependencies:
- Referenced by accounting, `/proc`, scheduling, and CPU state reporting code.

Notable risks:
- Numeric state values are ABI/signaling data; reordering or expanding them affects accounting consumers.
- `NMSTATES` has an explicit structural size constraint through `struct siginfo`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msacct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg.h

Public System V message queue ABI header.

Key responsibilities:
- Defines message queue permission bits, wait-mode bits, and `MSG_NOERROR`.
- Defines `msgqnum_t`, `msglen_t`, and public `struct msqid_ds` with permissions, queue head/tail pointers, byte/message counts, byte limit, last sender/receiver PIDs, timestamps, and reserved fields.
- Provides LP64/ILP32 timestamp padding for ABI compatibility.
- Defines user message buffer templates, using `_mtype/_mtext` under X/Open namespace rules.
- Defines `msgsnap()` buffer header and per-message header structures.
- Declares userland message queue APIs: `msgctl`, `msgget`, `msgids`, `msgsnap`, `msgrcv`, and `msgsnd`.

Dependencies:
- Includes `sys/ipc.h`.

Notable risks:
- This is public ABI; struct layout, padding, and namespace-sensitive field names must remain stable.
- Kernel code uses a different internal message buffer name to avoid collisions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg_impl.h

Kernel and compatibility implementation definitions for System V message queues.

Key responsibilities:
- Defines `msgsys()` subcommand numbers for get/control/receive/send/ids/snapshot.
- Defines wakeup records and selection callback chains used to decide which blocked sender/receiver to wake.
- Defines internal `struct msg` entries stored on queue lists, including type, size, message address, flags, and copyout reference count.
- Defines internal per-queue `kmsqid_t` state: permissions, message list, byte/count limits, PIDs/timestamps, sender/receiver wait counts, lowest type, wake selection lists, condition variables, and wait-list buckets.
- Defines condition-variable sharding constants for message receive wakeups.
- Defines ILP32 views of message buffers, snapshot headers, and `msqid_ds` for 32-bit syscall compatibility on LP64 kernels.

Dependencies:
- Includes `sys/ipc_impl.h`; kernel/kmem users include `sys/msg.h`, `sys/t_lock.h`, and `sys/list.h`.

Notable risks:
- Queue wakeup logic depends on multiple wait lists and per-message copyout flags; races can produce missed wakeups or use-after-free if invariants are broken.
- 32-bit compatibility structures must track the public ABI exactly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msio.h

Mouse ioctl ABI header.

Key responsibilities:
- Defines `Ms_parms` for mouse jitter threshold, speed law, and speed limit.
- Defines `Ms_screen_resolution` for screen height and width.
- Defines mouse ioctl command base and commands to get/set parameters, query button count, and set screen resolution.

Dependencies:
- Standalone public header guarded for C++.

Notable risks:
- Ioctl numeric values share the `'m' << 8` base with tape comments noting overlap; consumers rely on stable command numbers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msreg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msreg.h

Software mouse event/register layout header.

Key responsibilities:
- Defines `struct mouseinfo` samples with signed x/y/wheel deltas, button bitmask, and 32-bit timeval timestamp.
- Defines hardware button bit positions for left/middle/right.
- Defines `struct mousebuf` circular buffer layout for mouse samples.
- Defines `struct ms_softc` state for the mouse buffer, event generation, read format, VUID address, and previous button state.
- Defines event-generation state constants for x/y movement, ten buttons, and wheel.
- Defines obsolete kernel `MSIOGETBUF` ioctl for exposing the mouse buffer pointer.

Dependencies:
- Includes `sys/types.h` and `sys/types32.h`; VUID constants are expected from surrounding input headers.

Notable risks:
- Some structures expose historical buffer layouts and 32-bit timestamps.
- The obsolete kernel ioctl exposes buffer internals and should remain compatibility-only.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msreg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mtio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mtio.h

Magnetic tape ioctl ABI and device minor-layout header.

Key responsibilities:
- Defines tape operation request structures `mtop` and 64-bit-count `mtlop`, plus 32-bit syscall variants.
- Defines tape operations such as write EOF, spacing, rewind/offline, retension, erase, EOM, record-size get/set, load, tell/seek, and media lock/unlock.
- Defines tape status structure `mtget` and 32-bit variant with type, device/error registers, residual, file/block position, flags, and blocking factor.
- Defines tape drive configuration structure `mtdrivetype`, density/speed arrays, retry and timeout settings.
- Defines persistent/recent SCSI error entry structures, request wrappers, and 32-bit variants.
- Defines tape status flags, a large set of legacy and generic tape type IDs, tape info table entry type, ioctl command numbers, media insert/eject state enum, default tape path, and minor-device encoding macros.

Dependencies:
- Includes `sys/types.h`; error entry references SCSI ARQ status types defined elsewhere.

Notable risks:
- This is old public device ABI with many legacy constants; changing command numbers or minor-bit macros breaks tools and drivers.
- User pointers in drive type and error-entry requests require safe copyin/copyout handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mtio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot.h

Multiboot v1 boot protocol layout header for illumos kernel boot.

Key responsibilities:
- Defines Multiboot header magic, flags, checksums for 32-bit and 64-bit kernels, and bootloader magic.
- Defines the Multiboot image header fields required within the first 8 KiB of the loaded image.
- Defines ELF section table, module, memory map, drive info, and drive mode structures.
- Defines `multiboot_info_t` with flag bits for memory, boot device, command line, modules, symbols, memory map, drive info, config table, boot loader name, APM, and VBE/video data.
- Adds illumos-specific `sol_netinfo` for diskless/network boot metadata.

Dependencies:
- Non-assembly users include `sys/types.h` and `sys/types32.h`.

Notable risks:
- All pointer fields are 32-bit physical/loader addresses; 64-bit kernel code must translate carefully.
- Memory map walking follows Multiboot’s variable-sized records, not a normal fixed array.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2.h

Multiboot 2 protocol constants and packed structure definitions.

Key responsibilities:
- Defines Multiboot 2 search/alignment constants, header and bootloader magic, module/info alignment, tag IDs, header tag IDs, architecture IDs, optional tag flag, load preferences, and console flags.
- Defines packed header and header-tag structures for information requests, load addresses, entry address, console flags, framebuffer, module alignment, and relocatable kernels.
- Defines memory map entries and memory type constants.
- Defines generic tag and info-header structures plus typed tags for command line, bootloader name, modules, basic memory, boot device, memory map, VBE, framebuffer, ELF sections, APM, EFI32/EFI64, SMBIOS, ACPI, network, EFI memory map, EFI image handles, and load base address.
- Represents variable-length data with flexible arrays in string, module command line, memory maps, ELF sections, SMBIOS, ACPI, and network tags.

Dependencies:
- Non-assembly users include `sys/stdint.h`; structures are explicitly `#pragma pack(1)`.

Notable risks:
- Packed wire/bootloader ABI; natural alignment assumptions are unsafe.
- Header comments warn the spec documentation was inaccurate when written and GRUB 2 behavior is the practical reference.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2_impl.h

dboot helper interface for consuming Multiboot 2 information.

Key responsibilities:
- Declares helpers to find tags, get command line, count modules, retrieve module start/end/cmdline values, and get memory map tags.
- Declares basic memory info retrieval.
- Declares indexed accessors for Multiboot memory map and EFI memory map entry length, base, and type.
- Declares helpers to count memory map entries and compute the highest referenced address.

Dependencies:
- Includes `sys/multiboot2.h`; uses `boolean_t`, `uint32_t`, `uint64_t`, and `paddr_t` from surrounding boot/kernel types.

Notable risks:
- Accessors must handle packed, variable-sized tags and bounds correctly during early boot.
- These functions operate before normal kernel services are fully available.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/multiboot2_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mutex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mutex.h

Public kernel mutex interface header.

Key responsibilities:
- Defines mutex types: adaptive, spin, driver, and default.
- Defines opaque `kmutex_t` layout sized differently for LP64 and ILP32.
- Under `_KERNEL`, defines cache-line padded mutex type for false-sharing-sensitive users.
- Defines `MUTEX_HELD` and `MUTEX_NOT_HELD` assertion helpers.
- Declares mutex lifecycle, enter/tryenter/exit, ownership, owner lookup, backoff tuning variables, delay hooks, synchronization, and default lock-delay helpers.

Dependencies:
- Includes `sys/types.h` outside assembly.

Notable risks:
- `kmutex_t` is intentionally opaque but ABI-sized; changing its storage breaks kernel consumers.
- Spin mutex initialization depends on correct interrupt block cookie use.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nbmlock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nbmlock.h

Non-blocking mandatory-locking support interface.

Key responsibilities:
- Defines operation classes for mandatory lock/share conflict checks: read, write, rename, remove, and read-write mmap/exclusive checks.
- Declares critical-region primitives for vnode mandatory-lock-sensitive operations.
- Declares helpers to test whether checking is needed and to check generic, share, lock, and Solaris mandatory-lock conflicts.
- Declares `nbl_svmand()` for vnode/credential-based mandatory-lock setup or query.

Dependencies:
- Includes vnode, rwlock, and credential headers.

Notable risks:
- Correct caller use is operation-specific: `NBL_READWRITE` is for exclusive-lock or read-write mmap conflict checks, not ordinary I/O.
- These helpers protect filesystem operations from mandatory locking races; missing critical sections can violate locking semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nbmlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndi_impldefs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndi_impldefs.h

Internal Nexus Driver Interface implementation definitions.

Key responsibilities:
- Defines `struct ndi_event_hdl`, the internal event callback-management handle with owning devinfo, handle/event mutexes, callback-list mutex, interrupt block cookie, priority-level counters, event-cookie list, and next-handle link.
- Declares property encoding/decoding and common update/lookup/remove helpers for bytes, ints, int64, strings, and string arrays.
- Declares internal node configuration and unconfiguration routines.
- Retains obsolete device-tree change block/allow interfaces for driver compatibility.
- Declares framework-only helpers for auto-assigned node IDs, node class, node attributes, explicit node ID setting, and driver.conf child creation.

Dependencies:
- Includes core DDI/devinfo, properties, mutex, page, autoconf, and implementation headers.

Notable risks:
- This is internal DDI framework surface; consumers should not treat it as stable public driver ABI.
- Event handle locking is split between event definitions and callback lists, so call paths must use the correct mutex.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndi_impldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndifm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndifm.h

NDI fault-management cache and error-dispatch interface.

Key responsibilities:
- Defines DMA and access handle cache type constants and default cache sizes.
- Declares default cache-size globals.
- Aliases DDI fault-management cache structures for NDI use.
- Defines per-handle `ndi_err_t` status with ENA, status, expected-error flag, ontrap pointer, FM cache entry link, and compare function.
- Under `_KERNEL`, declares FM cache insert/remove/error helpers, per-entry and all-entry error processing, FM handler dispatch, and access/DMA handle error setters.

Dependencies:
- Includes `sys/ddifm.h` and `sys/ddifm_impl.h`.

Notable risks:
- Error attribution depends on matching handles to FM cache entries correctly.
- Cache lifecycle must coordinate with device teardown and fault handler dispatch.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndifm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211.h

Main illumos net80211 kernel support header for 802.11 MAC drivers.

Key responsibilities:
- Defines device capability flags for crypto, IBSS/AP/monitor modes, power management, retry, slot/preamble, WPA, WME, WDS, background scan, fragmentation, and HT software/driver support.
- Defines runtime flags, extended flags, channel flags, channel test macros, node flags, fixed-rate constants, WME constants, radiotap flags, auth modes, state machine states, rate sets, HT rate sets, channel records, and device statistics.
- Defines node table state with scan/inactivity tracking, key-index map, node list, and hash buckets.
- Defines `ieee80211_node` station/BSS state including addresses, rates, channel, beacon data, challenge, keys, captured WPA/WME/HT IEs, HT aggregation state, inactivity, tx rate, and list/hash links.
- Defines WME parameter/state structures.
- Defines central `ieee80211com` state for a driver instance: MAC handle, hardware capabilities, channels/rates, desired network settings, TIM, watchdog, crypto state, event queue, state flags, BSS, scan/station tables, WME, HT counters, and driver/common callbacks.
- Declares attach/detach, media/ioctl/door registration, input/encap, beacon, scan, station join/leave, node management, crypto, stats, channel/rate helpers, watchdog, header sizing, property, allocation, and lookup APIs.

Dependencies:
- Includes MAC provider headers, Ethernet, net80211 protocol/crypto/HT/AMRR headers, and WPA event definitions.

Notable risks:
- Driver callbacks are a mixed mandatory/optional/overridable interface; missing mandatory hooks or incorrect override order can break state transitions.
- Node reference counts are atomic but table/list operations still require the proper node-table locks.
- The `ieee80211com` layout is shared across common code and drivers, so field semantics are tightly coupled.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_amrr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_amrr.h

Adaptive Multi Rate Retry rate-control interface for net80211.

Key responsibilities:
- Defines global AMRR thresholds for minimum and maximum success counts.
- Defines per-algorithm settings in `struct ieee80211_amrr`.
- Defines per-node AMRR state with success count, recovery flag, success threshold, transmit count, and retry count.
- Declares node initialization and rate-choice functions.

Dependencies:
- Forward-declares `struct ieee80211_node`; used by 802.11 drivers/common code that track tx/retry statistics.

Notable risks:
- Rate adaptation quality depends on drivers maintaining accurate transmit and retry counters in `ieee80211_amrr_node`.
- Threshold tuning affects throughput and stability under changing radio conditions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_amrr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_crypto.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_crypto.h

802.11 crypto constants, key structures, and cipher plugin interface.

Key responsibilities:
- Defines WPA/optional IE size limits and MLME operation constants.
- Defines cipher IDs for WEP, TKIP, AES-OCB, AES-CCM, CKIP, and none.
- Defines key buffer/MIC sizes, key flags, default key flag, WEP IV/key-id/CRC constants, extended-IV constants, and maximum key count.
- Defines hardware key index type and no-key sentinel.
- Under `_KERNEL`, defines cipher operation table for attach/detach, key validation, encap/decap, MIC add/check.
- Defines `ieee80211_key` with key material, flags, hardware indexes, rx/tx sequence counters, cipher pointer, and private cipher state.
- Defines per-interface crypto state with network keys, default transmit key, hardware key capacity, and hardware key allocation/delete/set/update callbacks.
- Provides macros for key update, device key operations, cipher attach/detach, and MIC helpers.
- Declares crypto attach/detach, cipher register/unregister, and key reset functions.

Dependencies:
- Includes `sys/net80211_proto.h`; kernel builds also use STREAMS message blocks and MAC headers.

Notable risks:
- Cipher numeric ordering is documented as significant and must not be reordered.
- Key sequence counters and software/hardware crypto flags are security-sensitive.
- Hardware key callback failure handling must avoid installing partially configured keys.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_ht.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_ht.h

802.11n high-throughput support interface.

Key responsibilities:
- Defines aggregation block-ack window maximum and aging threshold for overlapping non-HT BSS detection.
- Defines receive message flags for A-MPDU and hardware WEP processing.
- Defines HT sequence type.
- Defines transmit A-MPDU state with flags, access category, dialog token, queued bytes/frames, sequence window, attempts, last request time, and timer.
- Defines receive A-MPDU reorder state with queued bytes/frames, sequence window, oldest age, frame count, and reorder buffer.
- Declares HT attach/detach/announce, supported HT rate lookup, HT rate setup, A-MSDU decapsulation, A-MPDU reorder/BAR receive, node init/cleanup/join/leave, channel adjustment, HT info updates, action handling, aggregation request/stop, BAR/action send, IE construction, and beacon HT update functions.

Dependencies:
- Forward-declares net80211 common, node, channel, and beacon offset structures; uses STREAMS `mblk_t` and timeout IDs from kernel context.

Notable risks:
- A-MPDU reorder logic depends on sequence arithmetic and bounded reorder buffers.
- Driver and common-code aggregation callbacks must agree on lifecycle transitions for ADDBA/DELBA.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_ht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_proto.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_proto.h

802.11 wire protocol definitions for net80211.

Key responsibilities:
- Defines address helpers, ACK size, physical modes, PHY types, operating modes, and protection modes.
- Defines packed frame structures for data, QoS data, 4-address frames, LLC/SNAP, management notification, RTS/CTS/ACK/PS-Poll/CF-End/BAR control frames, TIM IE, WPA IE, WME parameter/info/TSPEC elements, 802.11n action frames, HT capability IE, and HT information IE.
- Defines frame-control type/subtype/direction bits, sequence/fragment masks, sequence arithmetic macros, QoS masks, WME AC/TID mapping, management action constants, block-ack masks, and HT capability/parameter/info masks.
- Defines management information element lengths, capability flags, element IDs, OUIs, authentication algorithms/sequences, reason codes, status codes, WEP constants, MTU/min/max frame lengths, association ID limits, RTS/fragment thresholds, rate-fix flags, and beacon offset bookkeeping.
- Uses packed layout around all wire structures.

Dependencies:
- Consumed by `net80211.h`, `net80211_crypto.h`, and 802.11 frame parsing/building code.

Notable risks:
- Packed wire structures and bit masks must match IEEE 802.11 frame layout exactly.
- Some constants are duplicated with crypto headers; changes must stay synchronized.
- Variable-length IE structures require careful length validation before access.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netconfig.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netconfig.h

Network selection/configuration database ABI header for `/etc/netconfig`.

Key responsibilities:
- Defines `NETCONFIG` path and `NETPATH` environment variable name.
- Defines `struct netconfig` entries with network ID, semantics, flags, protocol family, protocol, device, lookup-library list, and reserved fields.
- Defines iteration handle `NCONF_HANDLE`.
- Defines transport semantics values for connectionless, connection-oriented, orderly release, raw, and private RDMA.
- Defines flags for visible and broadcast networks.
- Defines protocol family strings, including loopback, inet, inet6, many legacy families, and private RDMA.
- Defines protocol strings for tcp, udp, icmp, and RDMA provider names.
- Declares netconfig/netpath iteration, lookup, free, and error-reporting APIs.

Dependencies:
- Standalone public C/C++ header.

Notable risks:
- RDMA semantics and family values are explicitly private Solaris kRPC interfaces despite being present in a public-looking header.
- Reserved fields are noted as borrowed by services such as lockd, so ABI consumers may depend on them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/neti.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/neti.h

Kernel netinfo and network hooks framework interface.

Key responsibilities:
- Defines netinfo version, hook family names for IPv4, IPv6, ARP, and VIONA, and hook event names for physical in/out, forwarding, loopback in/out, NIC events, and observation.
- Defines hardware checksum capability bits and helper macros querying partial checksum status.
- Defines physical/logical interface IDs, network ID, interface address selector enum, injection mode enum, packet injection request, and `net_handle_t`.
- Defines protocol provider callback table for interface name, MTU, PMTU, logical interface addresses/zones/flags, physical/logical walks, packet injection, route lookup, and checksum validation.
- Defines internal protocol, injection, instance, instance-wrapper, and per-netstack data structures with lists, refcounts, hooks, netstack IDs, zones, condition variables, and condemnation flags.
- Provides IPIF ID mapping macros.
- Declares internal initialization and netid/netstack/zone mapping helpers.
- Declares public hook event/family/hook registration, packet injection allocation/free/inject, net instance registration/notification, kstat creation/deletion, protocol register/lookup/walk/release/unregister/notification, and interface/query wrappers.

Dependencies:
- Includes inet socket types, integer types, queue/list macros, hook implementation, and netstack headers; avoids including `sys/stream.h` by forward-declaring `struct msgb`.

Notable risks:
- This is an extensible kernel plugin interface with refcounted and condemned objects; teardown must coordinate with hook callbacks.
- Packet injection path crosses protocol stacks and zones, so netid/zone mapping and address validation are critical.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/neti.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netlb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netlb.h

Generic network driver loopback-test ioctl ABI header.

Key responsibilities:
- Defines loopback ioctl base and commands to get loopback-info size, get loopback-info table, get current mode, and set current mode.
- Documents the intended user flow for discovering available loopback modes, selecting/restoring modes, and running tests.
- Defines loopback info size type.
- Defines generic loopback mode types: normal, external, and internal.
- Defines `lb_property_t` entries with type, string key, and numeric value.

Dependencies:
- Uses `uint32_t` from surrounding system types.

Notable risks:
- Drivers expose mode keys/values through this ABI, so userland test tools depend on stable interpretation.
- Mode changes affect hardware test behavior and must be restored after diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netlb.h -->