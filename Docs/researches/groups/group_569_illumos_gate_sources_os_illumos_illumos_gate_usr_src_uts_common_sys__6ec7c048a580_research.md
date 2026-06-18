# Group Research: group_569_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__6ec7c048a580

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/av1394/av1394_isoch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/av1394/av1394_isoch.h

## Purpose

`av1394_isoch.h` defines private isochronous transfer state for the IEEE 1394 AV target driver. It covers DMA buffer pools, receive and transmit IXL command chains, per-channel transfer state, mmap offset allocation, IEC 61883 autotransmit support, and CMP plug-control register state.

## Main Interfaces

The central type is `av1394_ic_t`, representing one isochronous channel with direction, state, packet/frame sizing, 1394 isoch handles, condition variable, deferred request flags, and embedded receive/transmit substate.

Receive state `av1394_ir_t` tracks data pools, IXL receive buffers, full/empty frame queues, overflow index, and read offsets. Transmit state `av1394_it_t` tracks IXL begin/data blocks, frame timestamp metadata, empty/full queues, underrun state, and write offsets.

The header declares lifecycle and I/O entry points for channel open/close/init/fini/start/stop, receive read/recv/overflow, transmit write/xmit/underrun, mmap address-space allocation, CMP init/fini/bus-reset/ioctl handlers, and top-level isoch attach/detach/open/close/read/write/ioctl/devmap operations.

## Data and Synchronization

DMA memory is modeled as `av1394_isoch_seg_t` arrays inside `av1394_isoch_pool_t`, with DDI umem and DMA cookies. Comments and `_NOTE` annotations mark much of the setup data as single-threaded after initialization. `av1394_isoch_t` is the per-instance state with an instance mutex, channel array, CMP registers, soft interrupt state, and autotransmit configuration. Lock ordering is explicitly `i_mutex` before `ic_mutex`.

## Research Notes

This file is a private contract between AV1394 isochronous implementation files. Storage relevance is indirect, through common illumos DMA, devmap, soft interrupt, and 1394 target-driver patterns rather than filesystem behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/av1394/av1394_isoch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam.h

## Purpose

`dcam.h` is the primary private header for the IEEE 1394 digital camera target driver. It defines device flags, per-buffer DMA metadata, ring-buffer state, and the driver soft-state structure used by attach, open, capture, ioctl, read, poll, interrupt, and bus-reset paths.

## Main Types

`buff_info_t` describes one frame buffer: video mode, sequence number, timestamp, kernel address, DMA/access handles, DMA cookie, memory length, and cookie count.

`ring_buff_t` describes a circular frame buffer with buffer count/size, buffer metadata array, read pointer state, status per reader, and write pointer position. The driver supports one read pointer through `MAX_NUM_READ_PTRS`.

`dcam_state_t` stores the device instance, 1394 attach/target/isochronous handles, mutexes, parameter capabilities, IXL chain pointer, ring buffer, sequence counter, flags, current video mode/frame rate/capacity, status, online/power/suspend state, and bus-reset callback id.

## Interfaces

The header declares standard module and driver entry points, character device operations, interrupt and bus-reset callbacks, ring-buffer management helpers, and frame receive start/stop helpers.

## Research Notes

This is the shared state definition for DCAM driver implementation files. The most important risks are DMA buffer lifetime, ring-buffer reader/write pointer synchronization, and flag transitions around capture, suspend, and bus reset.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_frame.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_frame.h

## Purpose

`dcam_frame.h` declares the frame-receive subsystem for the 1394 digital camera driver.

## Interfaces

The functions cover ioctl-triggered receive startup, receive subsystem initialization/finalization, start/stop control, and IXL completion callback handling:

- `dcam1394_ioctl_frame_rcv_start`
- `dcam_frame_rcv_init`
- `dcam_frame_rcv_fini`
- `dcam_frame_rcv_start`
- `dcam_frame_rcv_stop`
- `dcam_frame_is_done`

`dcam_frame_rcv_init()` accepts video mode, frame rate, and requested ring-buffer frame count, indicating this layer builds the capture buffers and IXL program for the selected mode.

## Research Notes

This header is intentionally narrow. Its integration point is `dcam_state_t` from `dcam.h`; the implementation is responsible for turning isochronous completions into readable ring-buffer frames and for safely stopping capture.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_frame.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_param.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_param.h

## Purpose

`dcam_param.h` declares parameter capability discovery and get/set operations for the 1394 digital camera driver.

## Main Interfaces

The header defines repeated capability bits for valid/present/get/set/control-set support, then exposes:

- `param_attr_init()` and `param_attr_set()` for building the parameter capability bitmap.
- ioctl-level `dcam1394_ioctl_param_get()` and `dcam1394_ioctl_param_set()`.
- generic `dcam1394_param_get()` and `dcam1394_param_set()`.
- generic feature CSR helpers `feature_get()` and `feature_set()`.

It also declares per-parameter handlers for power, video mode, frame rate, ring-buffer capacity and counters, frame size, status, and camera image controls such as brightness, exposure, sharpness, white balance, hue, saturation, gamma, shutter, gain, iris, focus, zoom, pan, and tilt.

## Research Notes

This is a function contract, not a data-heavy header. It maps user-visible DCAM parameter lists to camera register access and driver-local state. Correctness depends on matching capability bits to the actual register support exposed by the device.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_reg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_reg.h

## Purpose

`dcam_reg.h` defines DCAM 1394 register offsets, masks, and shifts used to read and write camera control/status registers.

## Register Map

The header covers:

- camera initialize register and assert value.
- inquiry registers for video modes, frame rates, basic function support, and feature element support.
- feature inquiry fields for readout, on/off, auto, manual, min value, and max value.
- current frame rate, video mode, video format, ISO channel, camera power, ISO enable, memory save, one-shot, and memory channel registers.
- feature CSR offsets for brightness, exposure, sharpness, white balance, hue, saturation, gamma, shutter, gain, iris, focus, zoom, pan, and tilt.
- feature CSR masks for presence, on/off, auto/manual mode, value fields, and white-balance U/V values.

## Interfaces

`dcam_reg_read()` and `dcam_reg_write()` are the exported helpers for register I/O using `dcam1394_reg_io_t`.

## Research Notes

This header is the low-level binding to the DCAM camera specification. Mistakes in masks/shifts would directly affect camera parameter reporting and control.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/cmd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/cmd.h

## Purpose

`cmd.h` defines the SCSA1394 command object used to carry illumos SCSI packets over SBP-2/IEEE 1394.

## Main Types

`scsa1394_cmd_seg_t` describes one data-buffer or page-table segment with length, device/bus addresses, and a 1394 address handle.

`scsa1394_cmd_t` embeds an `sbp2_task_t` and ends with an embedded `scsi_pkt`. It stores command state/flags, owning LUN, `buf`, SCSI packet, CDB/status/private lengths, inline CDB/status/private storage, timeout tracking, DMA state for the command ORB, data buffer DMA windows and segments, page-table DMA memory, and Symbios workaround bookkeeping for LBA/block breakup.

## Macros and Flags

The header provides conversion macros between packet, command, and SBP-2 task objects. Command states are init/start/status. Flags track extended CDB/private/status allocations, valid DMA resources, map-in state, read/write direction, and Symbios command breakup.

## Research Notes

This is a core storage-adjacent header: it bridges SCSA packet state to SBP-2 task state and owns the DMA metadata needed for FireWire storage transfers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/impl.h

## Purpose

`impl.h` is the main private implementation header for the SCSA1394 HBA driver, which exposes SBP-2 FireWire storage devices to the illumos SCSI framework.

## Main Structures

`scsa1394_thread_t` models a per-LUN worker thread with request bits for exit, task status, SBP-2 nudging, bus reset, disconnect, and reconnect.

`scsa1394_lun_t` stores per-LUN locks, SBP-2 LUN/session pointers, child devinfo, worker and soft interrupt state, device workaround flags, fake inquiry data, and per-LUN statistics.

`scsa1394_state_t` stores per-instance device state, 1394 handles, event callbacks, DMA attributes, SCSI HBA transport, SBP-2 target/config ROM, LUN array, command cache, taskq, workaround flags, geometry hints, and instance statistics.

## Helpers and Interfaces

The header defines address/transport/state conversion macros, local node/bus generation macros, SBP-2 address/ORB helpers, CDB LBA and transfer-length extraction macros for 6/10/12-byte and READ CD commands, CD-RW block-size validation, constants, and function prototypes for SBP-2 attach/login/logout/request/reset/flush plus HBA worker and device-state helpers.

## Research Notes

This header is a compact map of FireWire storage driver architecture: per-instance target state, per-LUN work serialization, SBP-2 command conversion, bus reset handling, and legacy device workarounds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/sbp2.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/sbp2.h

## Purpose

`sbp2.h` defines SCSI command and status encapsulation structures for SBP-2 transport.

## Main Types

`scsa1394_cmd_orb_t` is the SBP-2 command ORB format. It includes the next ORB pointer, two-word data descriptor, parameter field, data size, and a 12-byte SCSI CDB.

`scsa1394_status_t` is the SBP-2 status block with SBP status, ORB offset, SCSI status, sense bits, sense code/qualifier, information bytes, CDB-dependent data, FRU, sense-key-specific bytes, and vendor-dependent fields.

## Constants

The header defines masks and shifts for SCSI status format and status code, status block formats, sense valid/filemark/EOM/ILI/sense-key bits, and FRU/sense-key-dependent fields.

## Research Notes

This is the wire-format bridge between SBP-2 status transport and illumos SCSI sense/status handling. It is small but central to command completion correctness.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/sbp2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/Makefile -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/Makefile

## Purpose

This Makefile controls installation and header checking for the common illumos `sys` include tree. It is a manifest for exported kernel/user headers and many structured subdirectories.

## Main Content

The file includes `$(SRC)/uts/Makefile.uts`, sets installed header mode to `644`, and documents several private headers present in the kernel but not shipped. It defines machine-specific headers, generated headers (`priv_const.h`, `priv_names.h`, `usb/usbdevs.h`), and a large `CHKHDRS` list of common public/private checked headers.

It then defines subdirectory header groups for audio, AV, crypto, DCAM, i2c, InfiniBand/RDMA, Fibre Channel, filesystem internals, GPIO, NVMe, SCSI, SATA, USB, 1394, hotplug, RSM, Trusted Solaris, network drivers, and platform headers.

## Build Targets

`CHECKHDRS` maps each group to `.check` targets using `DOT_H_CHECK`. `.PARALLEL` enables parallel checking/installing. `install_h` installs root header targets after directory creation. `all_h` builds generated headers. The generated headers are produced with AWK scripts, and `clean`, `clobber`, and `check` provide maintenance targets.

## Research Notes

For research indexing, this file identifies which headers are considered part of the illumos header surface. It is metadata-heavy but important for understanding exported ABI/API boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acct.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acct.h

## Purpose

`acct.h` defines legacy process accounting record formats and accounting flags.

## Main Types

`comp_t` is a compact accounting “floating point” type with a 13-bit fraction and 3-bit exponent.

`struct acct` is the SVR4 accounting record with flags, exit status, uid/gid, controlling tty, start time, user/system/elapsed time, memory use, I/O counts, read/write block counts, and an 8-byte command name.

`struct o_acct` preserves the older SVR3 layout using old uid/gid/device types.

## Interfaces and Flags

Userland sees `acct(const char *)`. Kernel builds see `acct(char)`, `sysacct(char *)`, and `acct_fs_in_use(struct vnode *)`.

Flags include `AFORK`, `ASU`, `AEXPND`, and `ACCTF`.

## Research Notes

This is an ABI compatibility header for classic process accounting. Filesystem relevance appears in `acct_fs_in_use()`, which lets kernel code detect accounting files on vnodes/filesystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acctctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acctctl.h

## Purpose

`acctctl.h` defines the `acctctl()` extended accounting control interface and kernel state for per-zone exacct settings.

## User ABI

Mode bits select process, task, flow, or network accounting. Option bits select file get/set, resource get/set, and state get/set operations. Resource IDs enumerate recordable fields for each accounting class, including process IDs, users, projects, CPU/time, zones, memory, flow addresses/ports/protocols, and network traffic counters.

`ac_res_t` carries one resource ID and enabled/disabled state. Userland gets `acctctl(int cmd, void *buf, size_t bufsz)`.

## Kernel State

Kernel builds define `ac_info_t`, which contains a lock, accounting output vnode, file name, enabled state, and resource bitmask. `struct exacct_globals` groups per-zone task, process, flow, and network accounting state and links it into a global list. `exacct_zone_key` is the zone key for per-zone settings.

## Research Notes

This header is relevant to filesystem behavior because accounting destinations are vnodes, and the kernel tracks whether accounting files are already in use across zones.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acctctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl.h

## Purpose

`acl.h` defines illumos ACL public types, permission bits, inheritance flags, syscall commands, userland ACL library interfaces, and kernel ACL comparison/sort hooks.

## Main Types

`aclent_t` is the POSIX-draft style ACL entry with type, uid/gid id, and permission mode. `ace_t` is the NFSv4/Windows-style access control entry with who, access mask, flags, and type. Kernel builds also define `ace_object_t` with object GUID fields.

## Constants

The file defines legacy ACL entry types and default ACL variants, ACE permission bits, ACE inheritance and identity flags, ACE allow/deny/audit/alarm types, ACL-level flags, CIFS-only ACE object/callback types, grouped permission masks, NFSv4-supported flags, and acl/facl command numbers for `aclent_t` and ACE ACLs.

## Userland Interfaces

Userland declarations include ACL validation, mode conversion, sorting, text conversion, allocation/free, path/fd get/set, trivial ACL checks, strip, and modern `acl_t` conversion APIs. The raw `acl()` and `facl()` syscalls are declared for all builds.

## Research Notes

This is a core filesystem security ABI header. It binds vnode security attributes, NFSv4 ACLs, CIFS semantics, and legacy UFS-style ACL tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl_impl.h

## Purpose

`acl_impl.h` defines the internal generic ACL container used by the public ACL API.

## Main Types

`acl_type_t` distinguishes `ACLENT_T` legacy ACL entries from `ACE_T` ACE entries.

`struct acl_info` stores the ACL type, entry count, per-entry size, flags, and pointer to the ACL entry array.

## Flags

`ACL_IS_TRIVIAL` marks ACLs equivalent to ordinary mode bits. `ACL_IS_DIR` marks directory ACL context. The comment notes that public ACL flags such as auto-inherit, protected, and defaulted may also be stored in the same flags field.

## Research Notes

This header is the narrow bridge between public `acl_t` handles and concrete ACL entry arrays. It is filesystem-relevant because VFS ACL calls must carry both legacy and ACE-style ACLs through one container.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acl_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acpi_drv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acpi_drv.h

## Purpose

`acpi_drv.h` defines ioctl commands, data structures, kstat layouts, and minor-number helpers for the ACPI battery, AC adapter, lid, display, and hotkey driver.

## Main Interfaces

`enum acpi_drv_ioctl` covers battery bay, info/status, AC count, power status, battery warning get/set, lid status/update, brightness levels, and brightness setting.

`batt_bay_t` reports bay count and battery presence bitmap. `acpi_bif_t` mirrors ACPI battery information fields such as design capacity, last full capacity, voltage, warning/low thresholds, granularity, model, serial, type, and OEM info. `acpi_bst_t` reports battery state, rate, remaining capacity, and voltage. `acpi_drv_warn_t` stores warning thresholds.

## Kstats and Device Types

The header defines kstat names and `kstat_named` structures for power, warning, BIF, and BST data. `enum acpi_drv_type` distinguishes unknown, control-method battery, AC, lid, display, and hotkey devices. Kernel builds define minor encoding/decoding macros.

## Research Notes

Not filesystem-specific, but it is part of the platform driver ABI. It shows a common illumos pattern of matching ioctls, kstats, and encoded minors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acpi_drv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr.h

## Purpose

`aggr.h` defines the user/kernel ioctl ABI for illumos link aggregation configuration and reporting.

## Main ABI

Transmit load-balancing policy bits cover L2, L3, and L4 hashing. LACP mode is off/active/passive, and LACP timer is long/short. Port state is standby or attached. The file caps groups at 256 ports and aggregation keys at 999 due to DLPI/VLAN PPA constraints.

`aggr_lacp_state_t` is a byte-sized bitfield union for LACP actor/partner state, with bit ordering handled for host endianness.

## Ioctls

The ABI structures support create, delete, info, add/remove ports, and modify operations. Creation includes link id, key, ports, policy, MAC, LACP mode/timer, fixed-MAC flag, and force flag. Info separates group-level fields from per-port fields including MAC, state, and LACP state.

## Research Notes

This is networking, not filesystem, but it is an exported illumos driver ABI. Layout stability across ILP32/LP64 is explicitly required.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_impl.h

## Purpose

`aggr_impl.h` defines kernel-private data structures and functions for the link aggregation MAC driver.

## Main Structures

The file models pseudo receive and transmit groups/rings that present aggregated underlying NIC rings to MAC clients. `aggr_port_t` represents one member link with MAC client/handle state, link status, stats, LACP state, hardware group/ring references, promiscuous supplemental addresses, and TX ring mappings.

`aggr_grp_t` represents an aggregation group with link id, key, refs, port list, group MAC, flags, MAC registration, transmit port array and policy, stats, LACP aggregate state, checksum/LSO capabilities, queued LACP packet thread state, pseudo RX/TX groups, TX flow-control notification thread state, and port callback synchronization.

## Interfaces

The header declares initialization/finalization, ioctl init/fini, group create/delete/info/modify/port add/remove, port create/delete/start/stop/promisc/unicast/multicast/stat, receive/transmit callbacks, LACP mode and packet handling, VLAN/MAC classification helpers, and ring TX helpers.

## Research Notes

This header is concurrency-heavy. It uses atomic refcount macros, multiple mutex/CV domains, LACP deferred processing to avoid MAC perimeter deadlocks, and explicit group/port lock ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_lacp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_lacp.h

## Purpose

`aggr_lacp.h` defines kernel-private IEEE 802.3ad LACP protocol state, timers, packet formats, and statistics for link aggregation.

## State Machines

The header defines receive, periodic, mux, and churn state enums plus string-list macros for diagnostics. Timer constants include fast/slow periodic times, short/long timeout times, churn detection time, and aggregate wait time.

`Agg_t` stores per-aggregation actor/partner system information, keys, transmit/receive enable flags, collector delay, periodic timer mode, last-change time, and readiness. `aggr_lacp_port_t` stores actor and partner port identifiers, state bytes, per-port state machine variables, timers, timer-thread state, mutex/CV, and last event time.

## Packet Formats

`lacp_t` describes an LACPDU with actor, partner, collector, terminator, and reserved fields. `marker_pdu_t` describes marker protocol frames. `lag_id_t` represents the 802.3ad LAG identifier.

## Research Notes

This file is protocol-structure oriented. Correctness depends on byte/bit layout matching 802.3ad and timer-thread handling matching the aggregation driver’s port lifecycle.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr_lacp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio.h

## Purpose

`aio.h` defines common asynchronous I/O result types and legacy/Solaris AIO operation codes.

## Main Types

`aio_result_t` carries the return value and errno for an asynchronous operation. A 32-bit syscall variant, `aio_result32_t`, is provided under `_SYSCALL32`.

## Operation Codes

The header defines opcodes for read, write, wait, cancel, notify, init, start, list I/O, suspend, error, list wait, asynchronous read/write, fsync, waitn, and reserved implementation operations. Large-file 64-bit opcode aliases differ depending on LP64 versus ILP32 build mode.

`AIO_POLL_BIT` is the opcode filter for `AIO_INPROGRESS`.

## Research Notes

This is a small ABI header that feeds both POSIX AIO and older Solaris AIO compatibility layers. It is relevant to filesystem research because AIO requests ultimately drive vnode/device I/O paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_impl.h

## Purpose

`aio_impl.h` defines kernel-private asynchronous I/O request, list-I/O notification, and per-process AIO state.

## Main Structures

`aio_lio_t` is a list-I/O group head with request count, active reference count, free-list pointer, completion condition variable, signal queue pointer, and event-port notification data.

`aio_req_t` wraps the driver-visible `struct aio_req` with fd, flags, result pointer, cancel callback, queue/hash links, LIO group, embedded `uio`, `iovec`, `buf`, signal notification, user aiocb pointer union, and event-port data.

`aio_t` is per-process AIO state: pending/outstanding counts, flags, cleanup state, port queues, free lists, done/poll/notify/cleanup queues, mutexes/CVs, aiocb pointer table, waitn state, notification counts, port queue lock, and request hash table.

## Interfaces

The header declares `aphysio`, page-unlock, cleanup, zero-length completion, request free, queue concatenation, result copyout, port queue removal, enqueue/dequeue, and `aio_done()` for driver/PXFS use.

## Research Notes

This is the kernel AIO engine’s internal contract. The risky areas are queue membership flags, process-exit cleanup, port/signal notification ordering, and physical I/O buffer lifetime.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_req.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_req.h

## Purpose

`aio_req.h` exposes the small asynchronous I/O request structure visible to drivers.

## Main Interface

Kernel builds define:

`struct aio_req` with:
- `aio_uio`, the `uio` for the request.
- `aio_private`, opaque driver-private data.

The header also declares `aphysio()` for asynchronous physical I/O submission and `anocancel()` as a no-cancel callback for buffers.

## Research Notes

This is the narrow driver-facing AIO contract. It deliberately hides the larger `aio_req_t` implementation details from drivers while letting physical-device and filesystem code participate in asynchronous I/O.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_req.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aiocb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aiocb.h

## Purpose

`aiocb.h` defines the user-visible asynchronous I/O control block structures and list-I/O constants.

## Main Types

`aiocb_t` contains file descriptor, buffer pointer, byte count, offset, request priority, signal/event notification, list-I/O opcode, embedded `aio_result_t`, state flag, and padding.

Large-file and syscall compatibility variants include `aiocb64_t` for userland large-file builds, `aiocb64_32_t` for 32-bit callers in the kernel, and `aiocb32_t` under `_SYSCALL32`. Packing pragmas preserve 32-bit alignment where required.

## Constants

The header defines `AIO_CANCELED`, `AIO_ALLDONE`, and `AIO_NOTCANCELED`; `LIO_NOWAIT` and `LIO_WAIT`; and list operation codes `LIO_NOP`, `LIO_READ`, and `LIO_WRITE`. The read/write values intentionally match `FREAD` and `FWRITE` without including `sys/file.h`.

## Research Notes

This is a stable user ABI file. Offset and pointer-size compatibility are the main maintenance concerns.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aiocb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ascii.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ascii.h

## Purpose

`ascii.h` defines symbolic constants for ASCII control characters.

## Constants

The header maps names such as `A_NUL`, `A_SOH`, `A_STX`, `A_ETX`, `A_EOT`, `A_ENQ`, `A_ACK`, `A_BEL`, `A_BS`, `A_HT`, `A_NL`, `A_LF`, `A_VT`, `A_FF`, `A_NP`, `A_CR`, `A_ESC`, file/group/record/unit separators, and `A_DEL` to their byte values. It also defines `A_CSI` as `0x9b`.

## Research Notes

This is a utility constants header with no logic. It is included by terminal, console, serial, or parser code that prefers named control character constants over literals.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ascii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asy.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asy.h

## Purpose

`asy.h` defines hardware registers, bit fields, ring-buffer macros, flags, and state structures for the asynchronous serial UART driver.

## Hardware Definitions

The file defines bus type names, COM port I/O addresses, UART hardware type constants from 8250/16550 through 16950, and an `asy_reg_t` enum covering base UART registers plus 16750/16650/16950 extended and indexed registers.

It defines bit masks for interrupt enable, FIFO control and trigger levels, interrupt status, line control, modem control/status, line status, scratch-pad testing, 16650 enhanced feature access, and 16950 additional control/status/clock registers.

## Driver State

Ring macros manage a 64 Ki-entry receive ring with embedded error bits. `struct asycom` stores per-port hardware/common state, locks, interrupt handles, soft interrupt state, saved registers, console polling state, access handle, and 16950 settings.

`struct asyncline` stores STREAMS/TTY line state, output block, condition variables, flags, flow-control state, receive ring pointers, overrun bookkeeping, timers, suspend queue, and active operations count.

## Research Notes

This is a mature driver-private contract. Concurrency is split between high-level adaptive locks and high-priority interrupt locks; receive-ring error marking and suspend/resume soft interrupt serialization are key correctness areas.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asynch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asynch.h

## Purpose

`asynch.h` declares the older Solaris asynchronous I/O user interfaces.

## Interfaces

It defines `AIO_INPROGRESS` as the sentinel result value and declares:

- `aioread()`
- `aiowrite()`
- `aiocancel()`
- `aiowait()`

Large-file build logic remaps `aioread`/`aiowrite` to 64-bit variants under `_FILE_OFFSET_BITS=64`, and remaps 64-bit names back to native names on LP64 with `_LARGEFILE64_SOURCE`. Transitional `aioread64()` and `aiowrite64()` declarations are provided when applicable.

`MAXASYNCHIO` is set to 200 outstanding I/Os.

## Research Notes

This is a compatibility ABI header for pre-POSIX Solaris AIO. It shares `aio_result_t` with `aio.h` and remains relevant where old applications use `aioread`/`aiowrite`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asynch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/atomic.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/atomic.h

## Purpose

`atomic.h` declares illumos atomic operations and memory-barrier primitives.

## Atomic Operations

The header provides typed increment, decrement, add, OR, AND, compare-and-swap, and swap functions for 8/16/32-bit integers, `uchar_t`, `ushort_t`, `uint_t`, `ulong_t`, pointers, and 64-bit values where available. Most operations have both no-return and `_nv` variants, with comments warning that `_nv` can be more expensive and should be used only when the new value is needed atomically.

Exclusive bit set/clear helpers operate on `ulong_t` bit positions and report whether the bit was already in the requested state.

## Memory Barriers

`membar_enter`, `membar_exit`, `membar_producer`, and `membar_consumer` define lock acquisition/release and producer/consumer ordering semantics.

## Research Notes

This is a foundational concurrency ABI used throughout kernel code. Filesystem and storage code rely on these routines for refcounts, lock-free flags, queue state, and memory ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/atomic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/attr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/attr.h

## Purpose

`attr.h` defines illumos extended system attribute names, command-line option aliases, attribute IDs, and helper APIs.

## Main Content

String constants cover attributes such as creation time, hidden, system, readonly, archive, nounlink, immutable, appendonly, nodump, opaque, antivirus quarantine/modified/scanstamp, fsid, owner/group SID, reparse point, generation, offline, and sparse.

Option strings map many of those attributes to compact utility flags. `f_attr_t` enumerates the same attributes, ending in `F_ATTR_ALL`.

`xattr_view_t` identifies virtual system attribute directory views: readonly and readwrite. `xattr_entry_t` maps an attribute name to an option, xattr view, and nvlist data type.

## Kernel and User Helpers

Kernel builds define `xattr_fid_t` for virtual sysattr fid handling and declare `xattr_dir_vget()` and `xattr_sysattr_casechk()`. Common helpers map attributes to names, options, views, and data types.

## Research Notes

This is directly filesystem-relevant. It defines the names and metadata used by extended attributes and virtual system attribute directories.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/attr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio.h

## Purpose

`audio.h` defines legacy audio support identifiers, channel ioctl numbers, device type enumeration, and channel information structure.

## Main Content

The header sets STREAMS/module identity strings and audio direction/sleep flags. `AUDIO_INIT()` initializes a structure to all-bits-one by byte.

Audio support ioctls include channel number/type/count and device pointer queries for AD/APM/AS devices.

`enum audio_device_type` identifies cloned channel personalities such as audio, audioctl, wavetable, MIDI, time, and user-defined device types.

`audio_channel_t` reports the owning pid, cloned channel number, device type, size of the personality-specific info structure, and a pointer to that info.

## Research Notes

This is an older audio framework ABI. It is not filesystem-related, but it does show cloned-minor device and STREAMS-module conventions used by illumos drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/ac97.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/ac97.h

## Purpose

`audio/ac97.h` defines AC'97 codec register offsets, bit masks, known vendor/codec IDs, driver properties, and the kernel AC'97 framework API.

## Register Coverage

The header maps the AC'97 register set from reset and master/headphone/mono/tone/beep volumes through input gains, record source/gain, general purpose, 3D control, interrupt/paging, powerdown, extended audio, DAC/ADC rates, surround/center/LFE volume, S/PDIF, modem registers, vendor registers, page 01 codec registers, and vendor ID registers.

Masks cover channel gains, mute bits, sample rates, power state bits, extended audio capabilities, S/PDIF fields, modem status/control bits, and vendor ID decoding.

## Framework API

Kernel-only declarations define opaque `ac97_t` and `ac97_ctrl_t`, register read/write callbacks, control walk callbacks, old and new allocation/init paths, control probing/registration/unregistration, control lookup/read/write, reset, free, and channel-count helpers.

## Research Notes

This is a hardware-definition and helper-framework header. It is important for audio drivers using AC'97 codecs, especially because control registration must be adjusted only during single-threaded attach/detach phases.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/ac97.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_common.h

## Purpose

`audio/audio_common.h` defines common kernel audio framework types, data formats, minor-number encoding, control IDs, port labels, common values, walk results, control types, and control flags.

## Main Content

Opaque framework types include audio parameters, buffers, streams, engines, clients, devices, mixer/engine ops, and controls. `audio_ctrl_desc_t` describes one control with name, type, flags, min/max values, and optional enum labels.

The file defines audio data format bit masks for u-law, A-law, signed/unsigned integer PCM in multiple sizes/endian forms, packed 24-bit, AC3, opaque formats, convertible formats, and PCM conversion formats. Endian macros map native/opposite-endian names.

Minor-number macros encode instance and device type for mixer, dsp, devaudio, devaudioctl, sndstat, and driver-reserved minors.

## Controls

The header standardizes many control IDs and port names, plus boolean and level strings. Control types include boolean, enum, stereo, mono, and meter. Flags describe readability, writability, VU peak, dB units, polling, volume roles, playback/record, 3D, tone, monitor, digital, and multi-select enum behavior.

## Research Notes

This is the shared vocabulary for illumos kernel audio drivers and the audio framework.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_driver.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_driver.h

## Purpose

`audio/audio_driver.h` defines the kernel driver-facing interface to the illumos audio framework.

## Engine Interface

`audio_engine_ops_t` version 2 contains callbacks for engine open/close, start/stop, frame count, format, channel count, sample rate, DMA cache sync, hardware queue length, optional per-channel buffer layout, and optional play-ahead policy. Open returns actual fragment/buffer values through pointer hints.

## Device and Engine API

Drivers can initialize/finalize devops, allocate/free audio devices, set description/version/info strings, allocate/free engines, set/get engine-private data, add/remove engines, register/unregister devices, suspend/resume devices, and emit warnings. Debug byte/word/dword dump helpers are also declared.

Engine flags identify input/output capability and framework-managed open modes such as output/input, exclusive use, and nonblocking open.

## Controls

The header defines control read/write callback types and APIs to add/delete controls, add synthetic PCM soft volume, notify control updates, and read/write controls through driver callbacks.

## Research Notes

This is the primary integration contract for audio device drivers. Correct use requires stable engine callbacks and careful DMA buffer synchronization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_driver.h -->