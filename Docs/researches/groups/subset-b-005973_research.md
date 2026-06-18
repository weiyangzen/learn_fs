<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/xe_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/xe_drm.h

## Purpose
Defines the Linux UAPI contract for Intel Xe DRM userspace clients: device discovery, GEM allocation and mmap offsets, VM lifecycle, VM binding, execution queues, GPU submission, user fence waits, observation/performance streams, madvise memory attributes, PXP state, EU stall sampling, and DRM RAS enum names. It is an ABI header, so field order, reserved fields, extensibility chains, and ioctl numbers are compatibility-critical.

## Important APIs, Types, And Functions
The exported ioctls are `DRM_IOCTL_XE_DEVICE_QUERY`, `DRM_IOCTL_XE_GEM_CREATE`, `DRM_IOCTL_XE_GEM_MMAP_OFFSET`, `DRM_IOCTL_XE_VM_CREATE`, `DRM_IOCTL_XE_VM_DESTROY`, `DRM_IOCTL_XE_VM_BIND`, `DRM_IOCTL_XE_EXEC_QUEUE_CREATE`, `DRM_IOCTL_XE_EXEC_QUEUE_DESTROY`, `DRM_IOCTL_XE_EXEC_QUEUE_GET_PROPERTY`, `DRM_IOCTL_XE_EXEC`, `DRM_IOCTL_XE_WAIT_USER_FENCE`, `DRM_IOCTL_XE_OBSERVATION`, `DRM_IOCTL_XE_MADVISE`, `DRM_IOCTL_XE_VM_QUERY_MEM_RANGE_ATTRS`, `DRM_IOCTL_XE_EXEC_QUEUE_SET_PROPERTY`, and `DRM_IOCTL_XE_VM_GET_PROPERTY`. Core structs include `drm_xe_device_query`, query reply structs for engines/memory/GT/topology/firmware/OA/PXP/EU stalls, `drm_xe_gem_create`, `drm_xe_vm_create`, `drm_xe_vm_bind_op`, `drm_xe_vm_bind`, `xe_vm_fault`, `drm_xe_exec_queue_create`, `drm_xe_sync`, `drm_xe_exec`, `drm_xe_wait_user_fence`, `drm_xe_observation_param`, `drm_xe_madvise`, and memory range attribute query structs. `drm_xe_user_extension` and `drm_xe_ext_set_property` are the shared extension-chain mechanism.

## Control Flow
Typical userspace flow queries device capabilities, creates GEM buffers and a VM, binds BOs or userptr ranges into the VM, creates an execution queue for selected engine class/instance data, submits batch buffers through `DRM_IOCTL_XE_EXEC`, and waits with sync objects or user fences. Observation streams are opened/configured through `DRM_IOCTL_XE_OBSERVATION` and then controlled with stream-fd ioctls. VM bind supports arrays of bind operations, async sync signaling, prefetch, unmap, userptr mapping, dumpable/PXP checks, CPU address mirroring, decompression, and madvise-autoreset behavior.

## State And Persistence
Kernel state is held in DRM file-private objects: GEM handles, VM ids, exec queue ids, bound VMAs, sync object relationships, observation stream fds, and per-VM fault reporting. The header exposes persistent ABI object handles, not implementation storage. Memory placement and attributes can change through migration, madvise, fault handling, purgeable state, and preferred-location policy. Reserved fields and zero-required extension tails preserve forward compatibility.

## Dependencies And Integration Points
Depends on generic DRM UAPI definitions from `drm.h`. It integrates with Mesa/compute runtimes, libdrm-style userspace, dma-buf/PRIME, syncobj timelines, mmap, GPU scheduler and GuC submission, platform memory regions, PXP protected-content management, perf/OA tooling, and DRM RAS netlink naming. Hardware-specific topology, GT, OA, and firmware details are intentionally queried instead of hard-coded by userspace.

## Risks And Edge Cases
Main risks are ABI drift, nonzero reserved fields, broken 32/64-bit pointer handling, stale two-step query sizing, invalid memory placement masks, VM bind races, userptr lifetime bugs, overcommit/fault-mode differences, long-running VM synchronization restrictions, PXP invalidation, purgeable BO access after DONTNEED, and observation stream overflow/lost reports. Integer sizes, alignment, pointer fields stored in `__u64`, and compact ioctl numbering are sensitive.

## Test Signals
Useful signals include UAPI compile checks, libdrm/Mesa ioctl smoke tests, two-pass query resize tests, GEM create/mmap/bind/exec/wait round trips, VM fault delivery tests, syncobj and user-fence ordering tests, invalid reserved-field rejection tests, memory migration and purgeable-state tests, OA/EU stall read/poll/error-path tests, PXP invalidation handling, and ABI layout comparison across 32-bit and 64-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/xe_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/bnxt.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/bnxt.h

## Purpose
Defines Broadcom BNXT-specific data carried by the generic `fwctl` firmware-control UAPI. It identifies supported BNXT command classes and the device-data shape returned by `FWCTL_INFO`.

## Important APIs, Types, And Functions
`enum fwctl_bnxt_commands` advertises inline, query, and send command categories. `struct fwctl_info_bnxt` contains `uctx_caps`, a firmware/user-context capability bitmap interpreted by the BNXT fwctl driver.

## Control Flow
Userspace first issues `FWCTL_INFO` through the generic fwctl fd, verifies `FWCTL_DEVICE_TYPE_BNXT`, reads `fwctl_info_bnxt`, then formats BNXT-specific RPC payloads for `FWCTL_RPC` according to the advertised capabilities.

## State And Persistence
The header itself defines no persistent state. Kernel state lives in the fwctl file context and BNXT firmware context; `uctx_caps` is a snapshot of allowed operations for that fd.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and the generic `fwctl.h` contract. It integrates with BNXT device firmware, fwctl security scopes, and vendor tooling that understands BNXT command payloads.

## Risks And Edge Cases
Risks are capability misinterpretation, use of commands outside the fd's granted scope, and ABI ambiguity if future bit definitions are added without keeping old zero/default behavior.

## Test Signals
Tests should validate `FWCTL_INFO` device type/data length, correct `uctx_caps` reporting, rejected unsupported command classes, and RPC error propagation for invalid or out-of-scope BNXT payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/bnxt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/cxl.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/cxl.h

## Purpose
Defines CXL-specific fwctl RPC payloads for mailbox feature commands. It maps generic `FWCTL_RPC` buffers to CXL mailbox opcode, flags, input payload, and output return-value formats.

## Important APIs, Types, And Functions
`struct fwctl_rpc_cxl` contains a grouped header with `opcode`, `flags`, `op_size`, and reserved zero field, followed by a union of CXL mailbox feature input structs. `struct fwctl_rpc_cxl_out` reports output `size`, device `retval`, and either structured supported-feature data or a flexible byte payload.

## Control Flow
Userspace discovers `FWCTL_DEVICE_TYPE_CXL`, builds a `fwctl_rpc_cxl` request with a supported mailbox opcode, passes it as the `in` buffer to `FWCTL_RPC`, and receives `fwctl_rpc_cxl_out` in the `out` buffer. Kernel delivery errors are represented by ioctl errno; CXL mailbox completion status is carried in `retval`.

## State And Persistence
No state is stored in the header. Persistent effects depend on mailbox opcode, especially Set Feature commands that can modify device feature configuration.

## Dependencies And Integration Points
Depends on `<linux/types.h>`, `<linux/stddef.h>`, and `<cxl/features.h>`. It integrates with the CXL mailbox subsystem, CXL feature descriptors, fwctl scope validation, and CXL management utilities.

## Risks And Edge Cases
Reserved fields must be zero. `op_size` and output `size` must match payload expectations. Feature payload versions, flexible array sizing, and distinguishing ioctl failure from device `retval` are key ABI risks.

## Test Signals
Test with Get Supported Features, Get Feature, and Set Feature payloads; invalid opcode/size rejection; reserved-field validation; short output-buffer handling; and correct propagation of mailbox return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/cxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/fwctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/fwctl.h

## Purpose
Provides the generic fwctl userspace ABI for controlled firmware RPC access. It defines the ioctl numbering, common extensible struct convention, device type discovery, security scopes, and generic RPC envelope.

## Important APIs, Types, And Functions
`FWCTL_INFO` uses `struct fwctl_info` to return `out_device_type` and optional device-specific data. `FWCTL_RPC` uses `struct fwctl_rpc` with scope, input length/pointer, and output length/pointer. `enum fwctl_device_type` identifies MLX5, CXL, BNXT, and PDS payload formats. `enum fwctl_rpc_scope` distinguishes configuration, read-only debug, debug write, and full debug write access.

## Control Flow
Userspace opens a fwctl device, calls `FWCTL_INFO` to determine the vendor payload ABI, allocates any returned device-data buffer, then sends device-specific RPC buffers through `FWCTL_RPC`. The kernel checks struct sizes, rejects nonzero unknown extension bytes, validates scope/permissions, delivers the RPC to firmware, and returns kernel delivery errors separately from device-encoded response status.

## State And Persistence
The ABI is fd-oriented. Per-fd kernel state can include security scope, firmware user context, hot-unplug orphaning, and vendor binding. Firmware configuration RPCs may persist in device firmware depending on command semantics; debug-write scopes may taint the kernel.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and `<linux/ioctl.h>`. Vendor-specific headers provide the device-data and RPC payload formats. Integration points include CAP_SYS_RAW_IO, lockdown policy, driver hotplug, firmware command queues, and user management tools.

## Risks And Edge Cases
ABI growth depends on zeroing unknown struct tails. Errno meanings are part of the contract: `ENOTTY`, `E2BIG`, `EOPNOTSUPP`, `EINVAL`, `ENOMEM`, and `ENODEV` carry distinct diagnostics. Security risk is high because firmware RPCs can expose configuration and debug control.

## Test Signals
Test old/new struct sizes, nonzero unknown-tail rejection, all scope permission paths, hot-unplug `ENODEV`, invalid pointer/length handling, vendor device-type discovery, and separation between ioctl errno and device response status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/fwctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/mlx5.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/mlx5.h

## Purpose
Defines MLX5-specific fwctl discovery data. MLX5 uses firmware user contexts, and this header exposes the UID and capability set bound to a fwctl fd.

## Important APIs, Types, And Functions
`struct fwctl_info_mlx5` contains `uid` and `uctx_caps`. RPC command buffers are expected to follow MLX5 firmware command layouts from the hardware programming reference, with the kernel forcing the fd-bound UID into command headers.

## Control Flow
Userspace calls `FWCTL_INFO`, verifies `FWCTL_DEVICE_TYPE_MLX5`, reads the UID/capability set, and sends MLX5 firmware command buffers via `FWCTL_RPC`. The kernel binds each fd to a user context and mediates commands according to fwctl security scope.

## State And Persistence
The important state is the firmware user context bound to the fd. Firmware-side changes can persist according to MLX5 command semantics; the header only exposes discovery fields.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and generic fwctl. Integrates with MLX5 firmware command handling, user-context capability assignment, NIC/device management tools, and fwctl lockdown/CAP policy.

## Risks And Edge Cases
Incorrectly trusting userspace-supplied UID would violate isolation; the kernel must overwrite/enforce it. Capability drift between firmware and userspace tooling can lead to unsupported command attempts.

## Test Signals
Verify `FWCTL_INFO` UID/caps, command header UID enforcement, unsupported capability rejection, scope enforcement, and firmware error encoding in output buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/mlx5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/pds.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/pds.h

## Purpose
Defines AMD/Pensando PDS-specific fwctl information and RPC envelope. It exposes capability bits for query/send support and a structured payload-pointer request/response format.

## Important APIs, Types, And Functions
`struct fwctl_info_pds` reports `uctx_caps`. `enum pds_fwctl_capabilities` defines query and send capability indexes. `struct fwctl_rpc_pds` has nested `in` and `out` structs with operation, endpoint, length, payload pointer, return value, and reserved fields.

## Control Flow
Userspace discovers `FWCTL_DEVICE_TYPE_PDS`, checks `uctx_caps`, fills `fwctl_rpc_pds.in` with operation, endpoint, and payload buffer, and passes the struct through generic `FWCTL_RPC`; the driver writes result metadata and output payload through `out`.

## State And Persistence
State is held in the fwctl fd and PDS firmware. RPC payloads may query or mutate firmware/device state depending on operation and capability.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and generic fwctl. Integrates with PDS firmware endpoints, capability-gated command dispatch, and vendor management tooling.

## Risks And Edge Cases
Reserved fields must remain zero. `len`/payload pointer mismatches, endpoint misuse, and conflating `out.retval` with ioctl errno are likely bugs. Capability bits are indexes, so tooling must treat them as bitmap positions.

## Test Signals
Test query/send capability reporting, rejected reserved fields, bad pointer/length handling, endpoint validation, and output `retval`/payload updates for successful firmware delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/pds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/a.out.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/a.out.h

## Purpose
Defines legacy GNU/Linux a.out executable, object, symbol, and relocation ABI helpers. It preserves constants and layout macros for old loaders, tools, and compatibility consumers.

## Important APIs, Types, And Functions
Exports machine type constants, magic values `OMAGIC`, `NMAGIC`, `ZMAGIC`, `QMAGIC`, `CMAGIC`, macros for `N_MAGIC`, machine type, flags, section offsets, text/data/bss addresses, symbol table constants, `struct nlist`, and `struct relocation_info`.

## Control Flow
Consumers inspect `struct exec.a_info`, validate magic with `N_BADMAG`, calculate file offsets for text/data/relocation/symbol/string sections, then load or link according to magic-specific alignment rules.

## State And Persistence
The persistent state is the on-disk a.out file format: header fields, symbol table records, relocation records, and string tables. Runtime state is derived by loaders/linkers.

## Dependencies And Integration Points
Includes architecture-specific `<asm/a.out.h>` unless overridden and uses page/segment sizing from architecture or libc. Integrates with obsolete binary loaders, binutils-like tools, and core-file/symbol consumers.

## Risks And Edge Cases
Architecture overrides, page-size assumptions, old Sun/m68k/SPARC machine constants, bitfield layout in relocations, and `SEGMENT_SIZE` depending on userspace `getpagesize()` are compatibility hazards. This format should not be extended casually.

## Test Signals
Layout tests for `struct nlist` and relocation records, offset macro tests for each magic value, cross-architecture compile checks, and loader tests against known a.out fixtures are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/a.out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acct.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/acct.h

## Purpose
Defines BSD-style process accounting record formats written by the kernel and consumed by accounting tools.

## Important APIs, Types, And Functions
Exports compact time/value types `comp_t` and `comp2_t`, record layouts `struct acct` and `struct acct_v3`, command length `ACCT_COMM`, accounting flags such as `AFORK`, `ASU`, `ACORE`, `AXSIG`, and byte-order/version constants.

## Control Flow
When process accounting is enabled, the kernel writes one record at task/process exit. Userspace accounting tools read records sequentially and decode flags, uid/gid, tty, start time, elapsed/user/system time, I/O, faults, swaps, exit code, and command name.

## State And Persistence
Records persist in the configured accounting file. The fields encode a point-in-time exit summary, not live process state. `struct acct` preserves older 16-bit uid/gid compatibility while `acct_v3` adds pid/ppid and full uid/gid fields.

## Dependencies And Integration Points
Depends on Linux integer types plus architecture `HZ`/byte order. Integrates with kernel accounting code, accton-style tools, and accounting log parsers.

## Risks And Edge Cases
Time range is limited by 32-bit start time, compact floating encodings lose precision, endianness must be honored, m68k padding differs under kernel build conditions, and userspace sees `acct_v3.ac_etime` as float while the kernel uses an integer representation.

## Test Signals
Validate binary record size/layout, endian byte-order flag, compact time decoding, v2/v3 parser compatibility, command truncation, and accounting records for normal exit, signal exit, core dump, and privileged execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acrn.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/acrn.h

## Purpose
Defines the ioctl ABI for `/dev/acrn_hsm`, the ACRN Hypervisor Service Module interface used by service-VM userspace to create/control VMs, handle I/O requests, assign devices, manage memory, inject interrupts, and wire eventfds/irqfds.

## Important APIs, Types, And Functions
Important structures include I/O request variants `acrn_mmio_request`, `acrn_pio_request`, `acrn_pci_request`, aligned `acrn_io_request`, `acrn_io_request_buffer`, VM creation and register structs, memory maps, passthrough device/IRQ structs, virtual device structs, power-management state structs, `acrn_ioeventfd`, and `acrn_irqfd`. Ioctls include create/destroy/start/pause/reset VM, set vCPU regs, inject MSI, monitor interrupts, notify request finish, create/attach/destroy ioreq clients, set/unset memseg, assign/deassign PCI/MMIO devices, create/destroy vdevs, PM state query, ioeventfd, and irqfd.

## Control Flow
Userspace creates a VM, maps an I/O request buffer, starts vCPUs, scans request slots for `PENDING`, marks them `PROCESSING`, emulates PIO/MMIO/PCI config operations, marks requests `COMPLETE`, and notifies the hypervisor. Separate ioctls configure memory, passthrough IRQ routing, virtual devices, and eventfd/irqfd delivery.

## State And Persistence
State is per VM and per HSM client: VM id, vCPU register state, shared ioreq buffer, memory segments, device assignments, interrupt routing, and eventfd registrations. The I/O request lifecycle explicitly cycles `FREE -> PENDING -> PROCESSING -> COMPLETE -> FREE`.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and ioctl definitions. Integrates with the ACRN hypervisor, service VM device model, eventfd, PCI/MMIO passthrough, ACPI power state data, and interrupt injection.

## Risks And Edge Cases
The 256-byte alignment of `acrn_io_request`, strict state ordering, atomic/barrier requirements between hypervisor and HSM, reserved fields, guest physical address trust, passthrough IRQ correctness, and eventfd deassignment flags are high-risk ABI points.

## Test Signals
Test VM lifecycle ioctls, ioreq state machine under concurrency, PIO/MMIO/PCI emulation completion, memory map set/unset, passthrough assignment/deassignment, irqfd/ioeventfd signal delivery, bad reserved-field rejection, and 32/64-bit layout compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acrn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/adb.h

## Purpose
Defines Apple Desktop Bus command and packet constants used by old Macintosh ADB controller/userspace interfaces.

## Important APIs, Types, And Functions
Macros build ADB command bytes: `ADB_BUSRESET`, `ADB_FLUSH`, `ADB_WRITEREG`, and `ADB_READREG`. It defines default device ids, return codes, packet kinds for ADB/CUDA/PMU/etc., and `ADB_QUERY_GETDEVINFO`.

## Control Flow
Consumers encode command bytes with device id/register fields, submit them to the ADB controller interface, and interpret returned packet or query data according to packet type and return status.

## State And Persistence
The header has no persistent storage; device addressing and handler ids are bus/controller state. Bus reset and flush affect live device/controller state.

## Dependencies And Integration Points
Integrates with legacy ADB, CUDA, PMU, timer, power, and Mac IIC packet providers in old Apple hardware support.

## Risks And Edge Cases
Command byte bit packing is easy to misuse, device ids are defaults rather than guaranteed live addresses, and controller-specific packet emulation may not support all packet classes.

## Test Signals
Compile tests plus hardware/emulator tests for reset, read/write register, flush, timeout handling, and get-device-info query responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adfs_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/adfs_fs.h

## Purpose
Defines the Acorn Disc Filing System disk record layout and constants needed to identify and parse an ADFS volume descriptor.

## Important APIs, Types, And Functions
`struct adfs_discrecord` is a packed, 4-byte-aligned 60-byte disk record containing geometry, root location, disk size/id/name/type, share size, zone count, format version, and root size. Constants define the on-disk record address and size.

## Control Flow
ADFS code reads the disk record at `ADFS_DISCRECORD`/`ADFS_DR_OFFSET`, interprets little-endian fields, derives filesystem geometry and root metadata, then mounts or reports the volume.

## State And Persistence
All state is persistent on disk. The structure mirrors the disk format and must not gain padding beyond the declared packed layout.

## Dependencies And Integration Points
Depends on Linux fixed-width types and magic definitions. Integrates with the ADFS filesystem driver, mount tooling, and disk image parsers.

## Risks And Edge Cases
Bitfields, little-endian values, high disk-size fields, and fixed 60-byte layout can break cross-compiler or cross-endian parsing. Corrupt disk records can produce invalid geometry.

## Test Signals
Mount/read tests against known ADFS images, structure size checks, endian decoding tests, and malformed geometry rejection are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/affs_hardblocks.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/affs_hardblocks.h

## Purpose
Defines Amiga Rigid Disk Block and partition block layouts used by AFFS-related partition/disk parsing.

## Important APIs, Types, And Functions
`struct RigidDiskBlock` describes RDB metadata, geometry, linked-list block pointers, and vendor/product strings. `struct PartitionBlock` describes partition block metadata and environment arrays. `IDNAME_RIGIDDISK`, `IDNAME_PARTITION`, and `RDB_ALLOCATION_LIMIT` are exported constants.

## Control Flow
Disk scanning code looks for the big-endian `RDSK` identifier, validates checksum/summed longs, follows partition and filesystem-header block lists, and decodes partition environment values.

## State And Persistence
The structs are persistent on-disk big-endian records. Kernel/userspace code uses them as ABI descriptions of Amiga disk metadata.

## Dependencies And Integration Points
Depends on Linux integer/endian types. Integrates with AFFS, partition scanners, Amiga disk image tools, and block-device probing.

## Risks And Edge Cases
Big-endian fields on little-endian hosts, untrusted linked block lists, checksum validation, and fixed vendor string lengths are the main hazards.

## Test Signals
Use known RDB disk images, verify identifier/checksum handling, partition list traversal bounds, endian conversion, and rejection of malformed list pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/affs_hardblocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/agpgart.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/agpgart.h

## Purpose
Defines the legacy `/dev/agpgart` ioctl ABI for AGP aperture management and graphics memory binding.

## Important APIs, Types, And Functions
Ioctls include `AGPIOC_INFO`, `AGPIOC_ACQUIRE`, `AGPIOC_RELEASE`, `AGPIOC_SETUP`, `AGPIOC_RESERVE`, `AGPIOC_PROTECT`, `AGPIOC_ALLOCATE`, `AGPIOC_DEALLOCATE`, `AGPIOC_BIND`, `AGPIOC_UNBIND`, and `AGPIOC_CHIPSET_FLUSH`. Userspace structs include `agp_info`, `agp_setup`, `agp_segment`, `agp_region`, `agp_allocate`, `agp_bind`, and `agp_unbind`.

## Control Flow
Userspace opens `/dev/agpgart`, acquires exclusive access, queries bridge/aperture state, sets mode, allocates pages, binds them at aperture page offsets, optionally reserves/protects regions, flushes chipset state, then unbinds/deallocates/releases.

## State And Persistence
State is kernel AGP bridge state: acquired owner, aperture setup, allocated page keys, bound GATT entries, and used page counts. It is live hardware/kernel state, not persistent across reboot.

## Dependencies And Integration Points
Depends on `<linux/types.h>` for userspace and ioctl encodings. Integrates with old DRI/DRM stacks, AGP bridge drivers, graphics memory managers, and chipset cache/TLB flush paths.

## Risks And Edge Cases
Legacy `unsigned long`/kernel-size types affect 32/64-bit ABI. Exclusive acquire/release ordering, stale allocation keys, page count overflow, and chipset-specific physical address fields are fragile.

## Test Signals
ABI layout compile tests, acquire/release ordering tests, allocation/bind/unbind/deallocate round trips, invalid key/page offset rejection, and chipset flush behavior are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/agpgart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aio_abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aio_abi.h

## Purpose
Defines the Linux native asynchronous I/O ABI structures shared by `io_submit`, `io_getevents`, and related system calls.

## Important APIs, Types, And Functions
`aio_context_t` is the userspace context handle. `enum IOCB_CMD_*` identifies pread, pwrite, fsync, fdsync, poll, noop, preadv, and pwritev operations. `IOCB_FLAG_RESFD` and `IOCB_FLAG_IOPRIO` control eventfd and ioprio usage. `struct io_event` reports completion data/object/result fields. `struct iocb` describes one submitted operation and is exactly 64 bytes.

## Control Flow
Userspace creates an AIO context, fills one or more `iocb` records, submits pointers to the kernel, and later reads `io_event` completions. The kernel stores an internal request key and returns results through the event queue and optional eventfd.

## State And Persistence
State is per AIO context: queued requests, completion events, eventfd notifications, and kernel-side request keys. It is transient and tied to process/file lifetime.

## Dependencies And Integration Points
Depends on Linux types, fs `RWF_*` flags, and architecture byte order. Integrates with filesystem/block I/O, eventfd, polling, and libc/libaio wrappers.

## Risks And Edge Cases
The byte-order-dependent placement of `aio_key` and `aio_rw_flags`, 64-bit pointer/offset fields, unsupported opcode values, eventfd lifetime, and priority flag interpretation are ABI-sensitive.

## Test Signals
Structure size/layout tests, pread/pwrite completion tests, eventfd signaling, vectored I/O, poll/noop behavior, endian compile checks, and invalid opcode/flag rejection provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aio_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/am437x-vpfe.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/am437x-vpfe.h

## Purpose
Defines private V4L2 configuration ABI for the TI AM437x VPFE CCDC raw capture block.

## Important APIs, Types, And Functions
Exports enums for CCDC data size, black-clamp sample length/line count, and A-law gamma width. Structures include `vpfe_ccdc_a_law`, `vpfe_ccdc_black_clamp`, `vpfe_ccdc_black_compensation`, and `vpfe_ccdc_config_params_raw`. `VIDIOC_AM437X_CCDC_CFG` is a private `_IOW` V4L2 ioctl.

## Control Flow
Capture applications configure raw-mode CCDC parameters through the private ioctl, then use normal V4L2 buffer/streaming operations for capture. Optional A-law, black clamp, and black compensation settings are interpreted by the driver.

## State And Persistence
Settings are live device configuration for the VPFE hardware and persist only until changed, stream stopped, or device reset.

## Dependencies And Integration Points
Depends on `<linux/videodev2.h>`. Integrates with V4L2 device nodes, TI VPFE/CCDC driver internals, sensor pipelines, and raw Bayer capture applications.

## Risks And Edge Cases
The ioctl is explicitly experimental. Enum ranges, unsigned/char field limits, disabled black-clamp interpretation, and hardware register constraints must be validated by the driver.

## Test Signals
V4L2 compliance plus raw capture tests with each data width, A-law enable/disable, clamp enabled/disabled, invalid enum rejection, and image black-level verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/am437x-vpfe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/amt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/amt.h

## Purpose
Defines netlink attributes for configuring Automatic Multicast Tunneling virtual interfaces.

## Important APIs, Types, And Functions
`enum ifla_amt_mode` distinguishes gateway and relay mode. `IFLA_AMT_*` attributes describe mode, relay/gateway ports, underlying link, local/remote/discovery IP addresses, and maximum tunnel count.

## Control Flow
Userspace creates or modifies an AMT link through rtnetlink, supplying these attributes. Gateway mode discovers/uses a relay and encapsulates IGMP/MLD; relay mode accepts gateway traffic and decapsulates multicast control/data in the opposite direction.

## State And Persistence
State is per netdevice: mode, ports, link index, IPs, discovery target, and tunnel limit. It persists while the netdevice exists and can be re-created by network managers.

## Dependencies And Integration Points
Integrates with rtnetlink `IFLA_INFO_DATA`, UDP encapsulation, multicast routing/control protocols, and network configuration tools such as iproute2.

## Risks And Edge Cases
Mode-specific attributes can be invalid in the other mode, port/IP defaults must be clear, and tunnel-limit exhaustion or discovery failures affect data-plane behavior.

## Test Signals
Rtnetlink create/change/dump tests, gateway/relay mode validation, invalid attribute rejection, multicast packet encapsulation/decapsulation tests, and iproute2 compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/amt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/android/binder.h

## Purpose
Defines the Android Binder character-device IPC ABI: object wire formats, read/write ioctl payloads, transaction data, protocol commands returned by the driver, and commands sent by userspace.

## Important APIs, Types, And Functions
Core types include `binder_size_t`, `binder_uintptr_t`, object headers, `flat_binder_object`, `binder_fd_object`, `binder_buffer_object`, `binder_fd_array_object`, `binder_write_read`, `binder_version`, freeze/debug/error structs, and `binder_transaction_data` variants. Ioctls include `BINDER_WRITE_READ`, context-manager setup, thread exit/version/debug-node queries, freeze operations, oneway spam detection, and extended error retrieval. Protocol enums define `BR_*` driver returns and `BC_*` userspace commands.

## Control Flow
Userspace writes `BC_*` commands and reads `BR_*` responses using `BINDER_WRITE_READ`. Transactions carry target handles or local object pointers, cookies, code, flags, sender identity, buffers, and offsets to embedded Binder objects. The driver rewrites object references, installs or transfers file descriptors, manages reference counts, asks processes to spawn loopers, and reports death/freeze notifications.

## State And Persistence
Binder state is per process and per binder device: nodes, handles, refs, buffers, thread looper counts, context manager, death/freeze notifications, frozen status, and queued transactions. State is runtime IPC state and vanishes with process/device teardown.

## Dependencies And Integration Points
Depends on Linux ioctl/types and Android userspace Binder libraries. Integrates with binderfs, SELinux security contexts, process freezer, file descriptor passing, Android service manager, and native handle marshaling.

## Risks And Edge Cases
32-bit vs 64-bit pointer sizing, offset-array validation, nested buffer parent fixups, fd-array bounds, reference-count protocol ordering, EINTR retry behavior, ECONNREFUSED teardown semantics, frozen target responses, and untrusted transaction buffers are high-risk.

## Test Signals
Binder selftests, libbinder IPC round trips, 32/64-bit compat tests, fd and fd-array transfer tests, death/freeze notification tests, oneway spam detection, extended-error checks, malformed offset/buffer rejection, and SELinux secctx transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/android/binder_netlink.h

## Purpose
Defines the generated generic-netlink family used by Binder to report errors/events to listeners.

## Important APIs, Types, And Functions
Exports family name/version, report attributes for error, context, source/target pid/tid, reply flag, transaction flags, code, and data size. `BINDER_CMD_REPORT` is the command and `BINDER_MCGRP_REPORT` is the multicast group.

## Control Flow
The Binder kernel code emits a `BINDER_CMD_REPORT` generic-netlink message to the report multicast group. Userspace subscribes to the family/group and parses the fixed attributes.

## State And Persistence
No persistent state is defined here. Events are transient multicast netlink records; listeners must handle loss or late subscription.

## Dependencies And Integration Points
Generated from `Documentation/netlink/specs/binder.yaml` and integrates with YNL tooling, Binder driver event paths, and diagnostic/monitoring daemons.

## Risks And Edge Cases
Generated headers should not be hand-edited. Attribute availability may vary by event; consumers must not assume every optional field is present. Multicast delivery is best-effort.

## Test Signals
YNL spec regeneration checks, netlink family discovery, subscription tests, emitted report parsing, and unknown-attribute tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binderfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/android/binderfs.h

## Purpose
Defines the binderfs control ioctl for dynamically creating Binder device nodes inside a binderfs mount.

## Important APIs, Types, And Functions
`BINDERFS_MAX_NAME` bounds device names. `struct binderfs_device` carries requested device name and returned major/minor numbers. `BINDER_CTL_ADD` is the `_IOWR` ioctl used on the binder-control node.

## Control Flow
Userspace mounts binderfs, opens the control device, fills a `binderfs_device` name, calls `BINDER_CTL_ADD`, and receives the allocated device major/minor for the new binder node.

## State And Persistence
Created binder devices persist in the binderfs mount namespace until removed/unmounted. Major/minor values are kernel allocation state.

## Dependencies And Integration Points
Depends on Binder UAPI, Linux types, and ioctl definitions. Integrates with Android containerization, per-namespace Binder device provisioning, and service managers.

## Risks And Edge Cases
Name length and termination, duplicate names, permission checks, mount namespace isolation, and major/minor exhaustion should be validated.

## Test Signals
Mount binderfs, add devices with valid/invalid names, check returned device numbers, duplicate creation behavior, and Binder operation on the created nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binderfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/apm_bios.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/apm_bios.h

## Purpose
Defines the legacy Advanced Power Management BIOS userspace/kernel interface, including BIOS info, power states, events, error codes, device ids, capability flags, and standby/suspend ioctls.

## Important APIs, Types, And Functions
Exports `apm_event_t`, `apm_eventinfo_t`, `struct apm_bios_info`, `APM_STATE_*`, event constants such as standby/suspend/resume/low-battery, error constants, device id masks, battery count, capability flags, `APM_IOC_STANDBY`, and `APM_IOC_SUSPEND`.

## Control Flow
Userspace queries or receives APM events through legacy APM device support and can request system standby or suspend through ioctls. Kernel/BIOS code maps requests to firmware calls and reports events/status.

## State And Persistence
Power state is system/device firmware state. BIOS segment information describes real-mode/16-bit/32-bit APM entry points and is static after boot.

## Dependencies And Integration Points
Depends on Linux types and ioctl. Integrates with old x86 BIOS APM firmware, power-management daemons, and legacy suspend/resume paths.

## Risks And Edge Cases
Modern systems generally use ACPI; APM firmware may be absent or buggy. Device id masks, OEM states, and resume event ordering are platform-specific.

## Test Signals
Legacy hardware/emulator standby/suspend tests, event delivery tests, absent-firmware error handling, and capability flag parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/apm_bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arcfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/arcfb.h

## Purpose
Defines two framebuffer ioctls used by the ARCFB driver for event wait and secondary control retrieval.

## Important APIs, Types, And Functions
`FBIO_WAITEVENT` is an `_IO` ioctl on framebuffer magic `F`. `FBIO_GETCONTROL2` is an `_IOR` ioctl returning a `size_t` control value.

## Control Flow
Userspace opens the framebuffer device, waits for a device event with `FBIO_WAITEVENT`, and reads auxiliary control state through `FBIO_GETCONTROL2`.

## State And Persistence
The header defines no storage. State is transient framebuffer/device event and control state.

## Dependencies And Integration Points
Integrates with Linux framebuffer ioctls and ARCFB-specific userspace tools.

## Risks And Edge Cases
`size_t` in an ioctl payload can be compat-sensitive across 32/64-bit userspace. Blocking wait semantics and signal interruption need userspace handling.

## Test Signals
Compat layout checks, ioctl availability tests, event wakeup behavior, and invalid fd/device rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arcfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arm_sdei.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/arm_sdei.h

## Purpose
Defines Arm Software Delegated Exception Interface function ids, version decoding helpers, return values, event flags, status bits, and info constants.

## Important APIs, Types, And Functions
Macros derive SDEI 1.0 SMC/HVC function ids from `SDEI_1_0_FN_BASE`. Version helpers extract major/minor/vendor fields. Return constants include success, not supported, invalid parameters, denied, pending, and out of resource. Event constants cover register routing mode, running/enabled/registered status, completion status, event type, priority, and routing info.

## Control Flow
Kernel or low-level users issue SDEI calls by function id to register, enable, disable, complete, unregister, route, bind interrupts, and reset events. Results are decoded with the return constants and version macros.

## State And Persistence
SDEI event registration, enablement, routing, and PE mask state live in firmware/EL3 interface state until reset/unregister. The header only provides numeric ABI constants.

## Dependencies And Integration Points
Integrates with Arm firmware, SMC/HVC calling conventions, interrupt routing, and kernel SDEI support.

## Risks And Edge Cases
Function id width, signed negative returns, event priority/routing semantics, and firmware version differences are the main risks.

## Test Signals
Firmware feature probing, version decode tests, register/enable/complete/unregister cycles, invalid parameter handling, and interrupt bind/release tests on SDEI-capable platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arm_sdei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-lpc-ctrl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-lpc-ctrl.h

## Purpose
Defines ioctls for configuring ASPEED BMC LPC host windows into BMC flash or memory resources.

## Important APIs, Types, And Functions
`ASPEED_LPC_CTRL_WINDOW_FLASH` and `ASPEED_LPC_CTRL_WINDOW_MEMORY` identify window types. `struct aspeed_lpc_ctrl_mapping` carries window type/id, reserved flags, host LPC address, BMC offset, and size. Ioctls are `ASPEED_LPC_CTRL_IOCTL_GET_SIZE` and `ASPEED_LPC_CTRL_IOCTL_MAP`.

## Control Flow
Userspace queries a window's size or requests a mapping. The driver validates type/id, alignment, offset/size, then programs LPC bridge registers so the host can access the selected BMC resource.

## State And Persistence
Mapping state is live BMC/host LPC window configuration. It can persist until reprogrammed or reset, depending on hardware/driver lifecycle.

## Dependencies And Integration Points
Depends on Linux ioctl/types. Integrates with ASPEED BMC LPC hardware, host firmware access paths, flash/RAM exposure policy, and BMC management tools.

## Risks And Edge Cases
Address/size must be power-of-two aligned, minimum size is 64 KiB, flags must be zero, and exposing BMC flash/RAM to the host is security-sensitive.

## Test Signals
GET_SIZE/MAP ioctl tests, alignment rejection, window type/id validation, host-visible access tests, and permission/security policy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-lpc-ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-p2a-ctrl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-p2a-ctrl.h

## Purpose
Defines ioctls for ASPEED P2A host access windows into BMC physical memory, including read-only/read-write policy and memory config readback.

## Important APIs, Types, And Functions
`ASPEED_P2A_CTRL_READ_ONLY` and `ASPEED_P2A_CTRL_READWRITE` are window flags. `struct aspeed_p2a_ctrl_mapping` carries physical address, length, and flags. Ioctls are `ASPEED_P2A_CTRL_IOCTL_SET_WINDOW` and `ASPEED_P2A_CTRL_IOCTL_GET_MEMORY_CONFIG`.

## Control Flow
Userspace sets a host-readable or host-writable BMC memory window, or queries the configured memory region used for mmap. Once a region is mapped, hardware semantics can unlock broader read access.

## State And Persistence
State is live P2A hardware window configuration. It controls host access to BMC memory until changed or reset.

## Dependencies And Integration Points
Depends on ioctl/types. Integrates with ASPEED P2A hardware, BMC security configuration, host debug/management flows, and mmap-capable driver paths.

## Risks And Edge Cases
The documented caveat that any mapped region unlocks all regions for reading is a major security risk. Address/length validation, write enable, and permission checks are critical.

## Test Signals
SET_WINDOW/GET_MEMORY_CONFIG ioctl tests, read-only vs read-write host access tests, invalid range rejection, and security policy checks around memory exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-p2a-ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-video.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-video.h

## Purpose
Defines ASPEED video capture input identifiers and private V4L2 controls for high-quality JPEG mode and quality.

## Important APIs, Types, And Functions
`enum aspeed_video_input` distinguishes VGA and graphics input. `V4L2_CID_ASPEED_HQ_MODE` and `V4L2_CID_ASPEED_HQ_JPEG_QUALITY` are controls under `V4L2_CID_USER_ASPEED_BASE`.

## Control Flow
Userspace configures ASPEED video capture through V4L2, selects input, adjusts HQ mode/quality controls, and streams frames through standard V4L2 APIs.

## State And Persistence
Control values are live device settings for the ASPEED video engine and persist only while configured by the driver/device.

## Dependencies And Integration Points
Depends on `<linux/v4l2-controls.h>`. Integrates with V4L2 control enumeration, BMC remote console capture, and ASPEED video hardware.

## Risks And Edge Cases
Control range/defaults are driver-defined; unsupported input/control combinations and JPEG quality extremes should be handled.

## Test Signals
V4L2 control query/set/get tests, capture on VGA/GFX inputs, JPEG quality visual/size validation, and invalid control value rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atalk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atalk.h

## Purpose
Defines AppleTalk socket address, network range, and protocol constants for Linux AppleTalk networking compatibility.

## Important APIs, Types, And Functions
Exports AppleTalk port/address constants, DDP size/hop limits, `SIOCATALKDIFADDR`, `struct atalk_addr`, `struct sockaddr_at`, and `struct atalk_netrange`.

## Control Flow
Userspace uses `sockaddr_at` with AppleTalk sockets and private ioctls to configure addresses. Kernel networking code uses network/node/port fields to bind, route, and send DDP traffic.

## State And Persistence
Runtime state includes interface AppleTalk addresses and network ranges. Persistence is external, through network configuration.

## Dependencies And Integration Points
Depends on Linux socket/types and byte order. Integrates with netatalk compatibility, AppleTalk protocol stack, and socket APIs.

## Risks And Edge Cases
The ABI is legacy; broadcast/any values, localtalk port constraints, and big-endian network fields must be handled correctly.

## Test Signals
Socket bind/connect tests, ioctl address configuration, endian checks for network fields, broadcast/any address behavior, and interoperability with netatalk tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm.h

## Purpose
Defines the general Linux ATM socket ABI: cell constants, AAL protocol ids, socket-option encoding, traffic/QoS parameters, PVC/SVC addresses, address-use helpers, and ATM ioctl wrapper structs.

## Important APIs, Types, And Functions
Important exports include ATM cell/PDU limits, AAL constants, `SO_ATMQOS`, `SO_ATMSAP`, `SO_ATMPVC`, `struct atm_trafprm`, `struct atm_qos`, `struct sockaddr_atmpvc`, `struct sockaddr_atmsvc`, `atmsvc_addr_in_use`, `atmpvc_addr_in_use`, `struct atmif_sioc`, and `atm_backend_t`.

## Control Flow
ATM applications create ATM sockets, set QoS/SAP options, bind or connect PVC/SVC addresses, and use ATM-specific ioctls for interface/device/backend configuration. Helpers identify whether PVC/SVC addresses are populated.

## State And Persistence
Socket state includes QoS, SAP, PVC/SVC address, AAL, and multipoint/backend choices. Interface and backend state is managed by related ATM ioctls and daemons.

## Dependencies And Integration Points
Depends on ATM API alignment, SAP and ioctl headers, Linux types, and compiler user-pointer annotations. Integrates with ATM socket families, signaling daemon, CLIP/LANE/MPOA/PPPoATM/BR2684 backends, and legacy ATM drivers.

## Risks And Edge Cases
Socket option bit encoding reserves limited level bits, ABI alignment differs on sparc/ia64, VPI/VCI magic values include negative sentinels, and traffic parameter bitfields must match userspace expectations.

## Test Signals
ATM socket option get/set tests, PVC/SVC bind/connect tests, QoS encoding validation, address helper behavior, and ABI alignment tests on affected architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_eni.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_eni.h

## Purpose
Defines ENI ATM driver-specific utility ioctls and buffer multiplier structure.

## Important APIs, Types, And Functions
`struct eni_multipliers` carries transmit and receive buffer multipliers in percent. `ENI_MEMDUMP` requests a memory map dump and `ENI_SETMULT` sets buffer multipliers using `atmif_sioc`.

## Control Flow
Driver-specific utilities issue private SAR ioctls on an ATM interface, passing an `atmif_sioc` that points to ENI-specific data when needed.

## State And Persistence
State is live ENI driver buffer configuration and diagnostic output. It is not persistent across driver reload/reset unless tooling reapplies it.

## Dependencies And Integration Points
Depends on `atmioc.h` and `atmif_sioc` from `atm.h`. Integrates with ENI SAR driver internals and ATM diagnostics.

## Risks And Edge Cases
Multipliers must be greater than 100 per comment; invalid user pointers and driver-private ioctl collisions are risks.

## Test Signals
Private ioctl availability, multiplier validation, memory dump path smoke tests, and malformed `atmif_sioc` rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_eni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_he.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_he.h

## Purpose
Defines FORE/HE ATM driver-specific register access ioctl structures and register type constants.

## Important APIs, Types, And Functions
`HE_GET_REG` is a private SAR ioctl. `struct he_ioctl_reg` carries register address, value, and type. Register types include PCI, RCM, TCM, and mailbox.

## Control Flow
Diagnostic utilities pass an `atmif_sioc` to `HE_GET_REG`; the driver interprets the pointed data as `he_ioctl_reg`, reads the requested register class/address, and returns the value.

## State And Persistence
No persistent state is defined. Register reads observe live hardware state.

## Dependencies And Integration Points
Depends on ATM ioctl numbering and `atmif_sioc`. Integrates with HE ATM hardware diagnostics.

## Risks And Edge Cases
Raw register access can expose hardware details; invalid register type/address and user buffer sizing must be checked.

## Test Signals
Known register read tests, invalid type/address rejection, and compat pointer handling through `atmif_sioc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_he.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_idt77105.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_idt77105.h

## Purpose
Defines IDT77105 ATM PHY driver-specific statistics structure and ioctls.

## Important APIs, Types, And Functions
`struct idt77105_stats` reports symbol errors, transmitted cells, received cells, and receive HEC errors. `IDT77105_GETSTAT` reads stats; `IDT77105_GETSTATZ` reads and zeros stats.

## Control Flow
Utilities issue PHY-private ioctls via `atmif_sioc`; the driver copies current counters to userspace and optionally resets them for the zeroing variant.

## State And Persistence
Counters are live driver/hardware statistics. `GETSTATZ` mutates them by clearing after read.

## Dependencies And Integration Points
Depends on Linux types, ATM ioctl ranges, and ATM device definitions. Integrates with IDT77105 PHY diagnostics.

## Risks And Edge Cases
Read-and-zero races, counter wrap, and invalid userspace buffer pointers are the main risks.

## Test Signals
Stats read tests, zeroing behavior, counter increment under traffic/errors, and malformed ioctl buffer rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_idt77105.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_nicstar.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_nicstar.h

## Purpose
Defines NICSTAR ATM driver-specific pool-statistics and buffer-level ioctls.

## Important APIs, Types, And Functions
Ioctls include `NS_GETPSTAT`, `NS_SETBUFLEV`, and `NS_ADJBUFLEV`. `buf_nr` contains min/init/max levels. `pool_levels` identifies buffer type, count, and levels. Buffer types include small, large, huge, and iovec.

## Control Flow
Utilities query pool stats, set level markers, or request automatic adjustment through SAR-private ioctls. `atmif_sioc` carries pointers to NICSTAR-specific data.

## State And Persistence
State is live NICSTAR receive/transmit pool configuration and counters; it is reset on driver/hardware reset.

## Dependencies And Integration Points
Depends on ATM API alignment and ioctl ranges. Integrates with NICSTAR driver diagnostics and buffer management.

## Risks And Edge Cases
The header notes external `sys/types.h` may be needed for some users. Invalid pool type/levels, count interpretation, and compat layout are risks.

## Test Signals
Pool stat reads, buffer level set/adjust tests, invalid type rejection, and stress under buffer pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_nicstar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_tcp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_tcp.h

## Purpose
Defines the ATMTCP pseudo-ATM driver protocol and ioctls for tunneling ATM cells/control over a TCP-like daemon interface.

## Important APIs, Types, And Functions
`struct atmtcp_hdr` carries network-order VPI, VCI, and length. `ATMTCP_HDR_MAGIC` marks control messages. `struct atmtcp_control` carries open/close control, kernel VCC pointer, suggested PVC address, QoS, and result. Ioctls include `SIOCSIFATMTCP`, `ATMTCP_CREATE`, and `ATMTCP_REMOVE`.

## Control Flow
Kernel and daemon exchange data cells or control messages. Open/close messages carry VCC, address, QoS, and result fields according to direction; create/remove ioctls manage persistent ATMTCP interfaces.

## State And Persistence
State includes persistent ATMTCP interface instances and active VCC mappings between kernel and daemon. `atm_kptr_t` carries opaque kernel pointers.

## Dependencies And Integration Points
Depends on ATM API, ATM addresses/QoS, ioctl ranges, and Linux types. Integrates with ATM daemon/userland emulation.

## Risks And Edge Cases
Header fields are network byte order while control fields are host order. Opaque pointer handling, open/close field direction, and persistent interface cleanup are fragile.

## Test Signals
Create/remove interface tests, open/close control exchange, endian validation for VPI/VCI/length, invalid result handling, and VCC cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_zatm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_zatm.h

## Purpose
Defines ZATM driver-specific free-buffer-pool ioctls and statistics/configuration structures.

## Important APIs, Types, And Functions
Ioctls include `ZATM_GETPOOL`, `ZATM_GETPOOLZ`, and `ZATM_SETPOOL`. `struct zatm_pool_info` contains ref counts, low/high watermarks, queue counters, alignment offsets, and timer repetition controls. `struct zatm_pool_req` selects a pool and carries info. Pool constants cover OAM, AAL0, AAL5 base, and last pool.

## Control Flow
Utilities query, read-and-zero, or update pool parameters via SAR-private ioctls. The driver copies pool info through an `atmif_sioc` pointer.

## State And Persistence
State is live ZATM buffer-pool configuration/counters. `GETPOOLZ` mutates counters by zeroing after read.

## Dependencies And Integration Points
Depends on ATM API alignment and ioctl ranges. Integrates with ZATM SAR driver buffer management.

## Risks And Edge Cases
Pool number bounds, read-and-zero races, and invalid watermarks/offsets can destabilize driver memory handling.

## Test Signals
Get/set pool round trips, zeroing counter behavior, invalid pool rejection, and traffic stress under configured low/high watermarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_zatm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmapi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmapi.h

## Purpose
Provides common ATM UAPI compatibility helpers for architecture-specific alignment and opaque kernel pointer representation.

## Important APIs, Types, And Functions
`__ATM_API_ALIGN` expands to 8-byte alignment on sparc/ia64 and empty elsewhere. `atm_kptr_t` is an opaque 8-byte aligned struct used to pass kernel pointer tokens without exposing pointer type details.

## Control Flow
Other ATM headers use these definitions in structs exchanged with userspace. Userspace treats `atm_kptr_t` as an opaque token and passes it back unchanged.

## State And Persistence
No state is stored here. `atm_kptr_t` can represent live kernel VCC/session state in related protocols.

## Dependencies And Integration Points
Included by general ATM, signaling, LANE, MPOA, ATMTCP, and driver-private headers. It bridges ABI layout across architectures.

## Risks And Edge Cases
Alignment differences can break binary compatibility if omitted. The opaque pointer convention requires all-zero fields for NULL and no userspace dereference.

## Test Signals
Cross-architecture struct layout checks, NULL token handling, and round-trip tests in protocols using `atm_kptr_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmarp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmarp.h

## Purpose
Defines ATMARP protocol constants and the kernel-to-daemon control message ABI for Classical IP over ATM address resolution.

## Important APIs, Types, And Functions
Exports retry/queue constants, ioctls `ATMARPD_CTRL`, `ATMARP_MKIP`, `ATMARP_SETENTRY`, and `ATMARP_ENCAP`, `enum atmarp_ctrl_type`, and `struct atmarp_ctrl`.

## Control Flow
An ATMARP daemon registers a control socket, receives need/up/down/change events, resolves IP-to-ATM mappings, attaches sockets to IP, sets ARP entries, and configures encapsulation.

## State And Persistence
State includes runtime ARP cache entries, unresolved packet queues, daemon control socket registration, and encapsulation settings. Persistence is external to the kernel ABI.

## Dependencies And Integration Points
Depends on Linux types, ATM API alignment, and ATM ioctl ranges. Integrates with Classical IP over ATM and ATMARP daemon tooling.

## Risks And Edge Cases
Unresolved queue limits, retry timing, daemon absence, network byte order IP fields, and stale hidden entries are operational risks.

## Test Signals
Daemon registration, need/up/down/change message delivery, ARP entry set/hide, encapsulation changes, retry timeout behavior, and queue overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmarp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmbr2684.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmbr2684.h

## Purpose
Defines the RFC 1483/2684 ATM bridging/routing backend ABI for creating virtual network interfaces and attaching ATM VCs.

## Important APIs, Types, And Functions
Exports media, routed, FCS, encapsulation, and payload constants. `struct atm_newif_br2684` creates backend interfaces. `struct br2684_if_spec` selects an interface by number/name. `struct atm_backend_br2684` attaches a VC with FCS/encapsulation/padding options. `struct br2684_filter_set` and `BR2684_SETFILT` manage an experimental IP filter.

## Control Flow
Userspace creates a BR2684 backend netdevice with `ATM_NEWBACKENDIF`, then uses `ATM_SETBACKEND` on an ATM VC to attach it to an interface. Optional filter ioctls constrain routed IP traffic.

## State And Persistence
State includes created netdevices, VC-to-interface attachments, encapsulation/payload/FCS settings, and optional filters. It lasts until interface/VC teardown.

## Dependencies And Integration Points
Depends on ATM core types and `IFNAMSIZ`. Integrates with Ethernet-like netdevices over ATM, PPP/CLIP alternatives, and legacy DSL/ATM tools.

## Risks And Edge Cases
Many constants are marked unsupported, interface lookup by name/number can race with netdevice lifecycle, and experimental filters may not compose with netfilter.

## Test Signals
Interface creation, VC attach/detach, LLC vs VC-mux encapsulation, routed vs bridged payload, filter set/disable, and invalid media/FCS options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmbr2684.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmclip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmclip.h

## Purpose
Defines Classical IP over ATM constants and ioctl to create CLIP network interfaces.

## Important APIs, Types, And Functions
Exports RFC1483 LLC header length, RFC1626 default MTU, CLIP idle/check timers, and `SIOCMKCLIP` for creating an IP-over-ATM interface.

## Control Flow
Userspace creates a CLIP interface with `SIOCMKCLIP`, then ATMARP and CLIP code resolve addresses and attach VCs for IP traffic.

## State And Persistence
State includes created CLIP netdevices, idle timers, and ATMARP-managed VC mappings. It is runtime network configuration.

## Dependencies And Integration Points
Depends on socket ioctl and ATM ioctl ranges. Integrates with ATMARP, ATM PVC/SVC sockets, and IP networking over ATM.

## Risks And Edge Cases
Idle timer defaults, daemon availability, MTU expectations, and ioctl collisions in the CLIP range are compatibility concerns.

## Test Signals
CLIP interface creation, MTU defaults, idle expiry, ATMARP resolution integration, and invalid ioctl context rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmclip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmdev.h

## Purpose
Defines ATM device-driver control ABI: interface statistics, link rates, address/ESI management, loopback controls, backend selection, and VC state/change constants.

## Important APIs, Types, And Functions
Exports PCR constants, `atm_aal_stats`, `atm_dev_stats`, many `ATM_*` ioctls for interface names/type/ESI/address/CIRANGE/stat/loopback/backend/party operations, backend ids, loopback bit masks, `atm_iobuf`, `atm_cirange`, single-copy flags, modify-QoS flags, and VC state text maps.

## Control Flow
Management tools issue ATM interface ioctls through `atmif_sioc` or `atm_iobuf` to discover devices, configure addressing/ranges/ESI, read stats, set loopback, select backends, and manage point-to-multipoint parties.

## State And Persistence
State includes interface addresses, ESI, connection identifier range, loopback mode, stats, backend bindings, and VC flags. It is runtime driver/network state.

## Dependencies And Integration Points
Depends on ATM API/core/ioctl headers. Integrates with ATM drivers, CLIP/LANE/MPOA/PPP/BR2684 backends, signaling daemons, and diagnostic tools.

## Risks And Edge Cases
Read-and-zero stats, `void __user *` buffer lengths, loopback local/remote combination constraints, backend id coordination, and legacy ioctl number ranges are sensitive.

## Test Signals
Interface discovery, address add/del/reset, ESI set/force, stats get/get-zero, loopback set/query, backend attach, party add/drop, and malformed buffer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmioc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmioc.h

## Purpose
Defines the ioctl number allocation ranges for ATM PHY, SAR, interface, backend, CLIP, LANE, MPOA, and special-purpose operations.

## Important APIs, Types, And Functions
Exports range bases and ends such as `ATMIOC_PHYCOM`, `ATMIOC_PHYTYP`, `ATMIOC_PHYPRV`, `ATMIOC_SARCOM`, `ATMIOC_SARPRV`, `ATMIOC_ITF`, `ATMIOC_BACKEND`, `ATMIOC_LANE`, `ATMIOC_MPOA`, `ATMIOC_CLIP`, and `ATMIOC_SPECIAL`.

## Control Flow
Other ATM headers compose `_IO*('a', range + offset, type)` ioctl numbers from these ranges to avoid collisions between common, type-specific, and private controls.

## State And Persistence
No state. This is a numeric namespace contract.

## Dependencies And Integration Points
Includes `<asm/ioctl.h>` so consumers get `_IO`, `_IOR`, `_IOW`, and `_IOWR`. It is included by almost every ATM UAPI header.

## Risks And Edge Cases
Overlapping private offsets can break driver utilities. The documented range boundaries are part of ABI compatibility and should not be renumbered.

## Test Signals
Compile-time uniqueness checks for known ATM ioctls and regression tests that ioctl numbers remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmlec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmlec.h

## Purpose
Defines the ATM LAN Emulation Client daemon interface for LANE control/data/multicast sockets and messages.

## Important APIs, Types, And Functions
Ioctls `ATMLEC_CTRL`, `ATMLEC_DATA`, and `ATMLEC_MCAST` register socket roles. `atmlec_msg_type` enumerates MAC/ATM mapping, topology, flush, ARP, config, LEC id, and bridge decisions. `atmlec_config_msg`, `atmlec_msg`, and `atmlec_ioc` carry LANE parameters and addresses.

## Control Flow
The LEC daemon registers control/data sockets, exchanges `atmlec_msg` records with the kernel to resolve MAC-to-ATM mappings, react to topology/flush events, and configure LANE parameters. Data and multicast VCCs are attached through `atmlec_ioc`.

## State And Persistence
State includes LEC interfaces, ATM/MAC cache entries, LANE config, LEC id, proxy state, TLV data, and attached VCCs. It is runtime networking state.

## Dependencies And Integration Points
Depends on ATM core/API, Ethernet address definitions, and ATM ioctl ranges. Integrates with LANE daemons such as zeppelin and ATM network interfaces.

## Risks And Edge Cases
Fixed max LEC interfaces, variable TLVs after messages, LANE1/2 differences, cache flush ordering, and proxy mapping correctness are risks.

## Test Signals
Daemon registration, config message exchange, MAC/ATM mapping updates/deletes, topology change/flush handling, multicast/data VCC setup, and TLV length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmlec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmmpc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmmpc.h

## Purpose
Defines the ATM MPOA Client daemon ABI for shortcut setup, ingress/egress cache control, MPOA parameter exchange, and control/data socket roles.

## Important APIs, Types, And Functions
`ATMMPC_CTRL` and `ATMMPC_DATA` register sockets. `atmmpc_ioc` selects MPC ingress/egress attachment. `in_ctrl_info`, `eg_ctrl_info`, `mpc_parameters`, `k_message`, and `llc_snap_hdr` carry MPOA protocol data. Numerous `SND_*`, `MPOA_*`, and configuration constants define daemon/kernel message types and defaults.

## Control Flow
The daemon receives kernel trigger messages, sends MPOA resolution requests/replies, opens ingress shortcuts, purges caches, reacts to MPS death, and updates MPC parameters. Kernel and daemon exchange `k_message` records over control sockets.

## State And Persistence
State includes ingress/egress MPOA caches, shortcut VCCs, control ATM addresses, retry/holding timers, parameters, and socket role attachments. It is runtime network state.

## Dependencies And Integration Points
Depends on ATM API/core/types and ATM ioctl ranges. Integrates with MPOA daemons, NHRP/MPOA signaling, and ATM QoS.

## Risks And Edge Cases
Message type coordination, fixed 256-byte DLL header, network-byte-order IP fields, cache id/tag lifetime, timer defaults, and daemon reload/exit handling are fragile.

## Test Signals
Control/data socket registration, ingress/egress cache update/purge, shortcut open flow, parameter reload, MPS death handling, and malformed message rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmmpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmppp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmppp.h

## Purpose
Defines the PPP over ATM backend selection payload and encapsulation constants for RFC2364 support.

## Important APIs, Types, And Functions
Encapsulation constants are autodetect, VC-mux, and LLC. `struct atm_backend_ppp` is passed to `ATM_SETBACKEND` with `backend_num` set to `ATM_BACKEND_PPP` and `encaps` set to one of the exported values.

## Control Flow
Userspace opens/configures an ATM VC, then sets the PPP backend using `ATM_SETBACKEND`. PPP frames are then carried over the selected ATM encapsulation.

## State And Persistence
State is the VC backend binding and encapsulation mode. It persists for the lifetime of the VC.

## Dependencies And Integration Points
Depends on `atm.h`. Integrates with PPP, pppd plugins, ATM VCs, and RFC2364 networking.

## Risks And Edge Cases
Autodetect may fail with ambiguous traffic, encapsulation must match peer configuration, and backend selection must happen at the correct VC lifecycle point.

## Test Signals
PPP session establishment over VC and LLC modes, autodetect behavior, invalid encapsulation rejection, and backend teardown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmppp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmsap.h

## Purpose
Defines ATM Service Access Point addressing fields for BLLI/BHLI negotiation in ATM signaling.

## Important APIs, Types, And Functions
Exports layer-2, layer-3, high-layer, mode, terminal, and multiplexing constants. `struct atm_blli` describes low-layer protocol info, `struct atm_bhli` high-layer info, `struct atm_sap` groups one BHLI plus up to three BLLIs, and `blli_in_use` tests whether a BLLI is populated.

## Control Flow
Userspace or signaling daemons populate SAP fields before SVC setup/listen. The kernel and atmsigd include these fields in signaling messages and matching logic.

## State And Persistence
SAP data is per socket/call signaling state and persists for the call/listen lifetime.

## Dependencies And Integration Points
Depends on ATM API alignment. Integrates with `atm.h`, `atmsvc.h`, atmsigd, and ATM UNI signaling.

## Risks And Edge Cases
Optional fields encoded as zero, max BLLI count, protocol-specific union interpretation, and HLI length bounds must be respected.

## Test Signals
SVC setup/listen with varied SAPs, BLLI/BHLI matching tests, omitted optional fields, maximum HLI/BLLI counts, and ABI alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsvc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmsvc.h

## Purpose
Defines the ATM signaling daemon control socket ABI used between kernel SVC code and `atmsigd`.

## Important APIs, Types, And Functions
`ATMSIGD_CTRL` registers the signaling daemon control socket. `enum atmsvc_msg_type` defines bind/connect/accept/reject/listen/okay/error/indicate/close/modify/identify/terminate/addparty/dropparty messages. `struct atmsvc_msg` carries VCC tokens, reply code, PVC/SVC addresses, QoS, SAP, and session id. `SELECT_TOP_PCR` chooses a PCR value from traffic parameters.

## Control Flow
Kernel SVC code sends requests/indications to atmsigd; the daemon resolves signaling, returns okay/error/close or call-control messages, and includes QoS/SAP/address state. Point-to-multipoint operations use add/drop party messages.

## State And Persistence
State includes active/listening VCC tokens, signaling sessions, call addresses, QoS/SAP negotiations, and pending replies. It is runtime call-control state.

## Dependencies And Integration Points
Depends on ATM API/core/ioctl headers. Integrates with atmsigd, ATM UNI signaling, SVC sockets, and QoS policy.

## Risks And Edge Cases
Opaque VCC token lifetime, positive vs negative reply semantics, daemon crash/termination, p2mp session handling, and PCR selection policy must match kernel and daemon.

## Test Signals
Daemon registration, bind/connect/listen/accept/reject/close flows, add/drop party, modify QoS, daemon termination recovery, and malformed message handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/audit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/audit.h

## Purpose
Defines the Linux audit netlink ABI: message type ranges, audit rule constants, filter/action fields, status and feature structures, architecture identifiers, multicast groups, and variable-length rule records.

## Important APIs, Types, And Functions
Exports command messages `AUDIT_GET`, `AUDIT_SET`, rule add/delete/list commands, TTY and feature commands, large event type ranges for syscall/path/LSM/crypto/integrity/anomaly records, filter constants, field ids, operators, status masks, feature bitmaps, `AUDIT_ARCH_*` values, `audit_status`, `audit_features`, `audit_tty_status`, and `audit_rule_data`.

## Control Flow
Audit userspace uses netlink to get/set audit status, configure auditd pid/rate/backlog/failure policy, add/list/delete syscall rules, configure TTY auditing, and query/set feature locks. The kernel emits audit records in the numeric event ranges to auditd or multicast read-only listeners.

## State And Persistence
Kernel audit state includes enabled/failure mode, auditd pid, rate/backlog counters, feature locks, TTY settings, syscall/filter rule lists, watches, and lost-message counters. Persistence is external through auditd rules/config reloaded at boot.

## Dependencies And Integration Points
Depends on Linux types and ELF machine ids. Integrates with netlink, auditd/libaudit, LSMs, seccomp, io_uring, BPF, integrity/IMA/EVM, netfilter, fanotify, and filesystem watches.

## Risks And Edge Cases
Numeric message ranges are ABI; renumbering is forbidden. Rule arrays have fixed maxima, `buf[]` carries variable string fields, architecture ids encode bitness/endian/convention, and feature locks can make settings immutable. Backlog/rate failure policy can drop logs or panic the system.

## Test Signals
Netlink get/set status tests, rule add/list/delete with integer and string fields, syscall arch filtering, TTY auditing, feature lock behavior, multicast read-log listener tests, lost/backlog counters, and malformed rule buffer rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_dev-ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auto_dev-ioctl.h

## Purpose
Defines the modern autofs control-device ioctl ABI used to manage autofs mount points through `/dev/autofs`.

## Important APIs, Types, And Functions
`struct autofs_dev_ioctl` is the common extensible payload with version, size, `ioctlfd`, command union, and optional path tail. Argument structs cover protocol version, openmount, ready/fail tokens, pipe fd, timeout, requester, expire, askumount, and mountpoint query. Ioctls include version/proto queries, open/close mount, ready/fail, setpipefd/catatonic, timeout, requester, expire, askumount, and ismountpoint.

## Control Flow
Userspace initializes the struct with `init_autofs_dev_ioctl`, optionally appends a path, opens or targets a mount fd, and issues command-specific ioctls. Kernel autofs uses tokens to complete pending mount/expire requests and returns mount/requester/status data through the union.

## State And Persistence
State is per autofs mount and control fd: protocol version, pipe fd, pending wait tokens, timeout, requester uid/gid, expiration candidates, and mountpoint identity. It is runtime mount state.

## Dependencies And Integration Points
Depends on `auto_fs.h` and string helpers. Integrates with automount daemons, VFS mount handling, pipes, and path-based control operations.

## Risks And Edge Cases
The `size` must include appended path data, version/size negotiation matters, token mismatch can leave waiters blocked, and `ioctlfd` defaults to -1. Path validation and mount namespace context are critical.

## Test Signals
Initialize/version tests, openmount/closemount, ready/fail token completion, setpipefd/catatonic behavior, timeout get/set, requester query, expire/askumount, ismountpoint, and malformed size/path rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_dev-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs.h

## Purpose
Defines the classic autofs pipe packet and ioctl ABI for protocol versions 3 through 5.

## Important APIs, Types, And Functions
Exports protocol version/subversion constants, `autofs_wqt_t`, packet header/missing/expire structs, legacy ioctls `AUTOFS_IOC_READY`, `FAIL`, `CATATONIC`, `PROTOVER`, `SETTIMEOUT`, `EXPIRE`, v4/v5 expire/missing packet types, mount type helpers, notification enum, v5 packet unions, and `AUTOFS_IOC_EXPIRE_MULTI`, `PROTOSUBVER`, `ASKUMOUNT`.

## Control Flow
Kernel autofs sends missing/expire packets to the daemon through a pipe. The daemon mounts or expires paths, then completes wait tokens with ready/fail ioctls. Additional ioctls negotiate protocol versions, timeout, multi-expire, and umount readiness.

## State And Persistence
State is per autofs mount: protocol version, wait queue tokens, pending path packets, mount type, timeout, and daemon pipe/catatonic status. It is runtime VFS/daemon coordination state.

## Dependencies And Integration Points
Depends on Linux types/limits and userspace ioctl definitions. Integrates with automount daemons, VFS path lookup, direct/indirect/offset mount types, and the newer control device ABI.

## Risks And Edge Cases
`autofs_wqt_t` size is architecture-sensitive to preserve compat ABI. Path name length is fixed at `NAME_MAX+1`. Token completion ordering, daemon death/catatonic mode, and direct vs indirect packet interpretation are common hazards.

## Test Signals
Protocol negotiation, missing and expire packet delivery, ready/fail completion, timeout setting, multi-expire behavior, direct/indirect/offset trigger tests, compat type-size checks, and daemon crash recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs4.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs4.h

## Purpose
Compatibility wrapper for autofs version 4 userspace includes. It re-exports the definitions from `linux/auto_fs.h`.

## Important APIs, Types, And Functions
No new ABI is defined. Including this header provides the `auto_fs.h` protocol constants, packet structs, helper functions, and ioctls.

## Control Flow
Consumers that historically included `auto_fs4.h` compile against the unified autofs ABI without changing source.

## State And Persistence
No separate state. Runtime state is the autofs state described by `auto_fs.h`.

## Dependencies And Integration Points
Depends directly on `<linux/auto_fs.h>`. Integrates with older automount source code expecting the v4 header name.

## Risks And Edge Cases
The main risk is assuming it only contains v4 definitions; it actually exposes the unified current autofs ABI.

## Test Signals
Compile compatibility tests for old autofs userspace includes and confirmation that expected v4/v5 symbols are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auxvec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auxvec.h

## Purpose
Defines generic Linux ELF auxiliary vector entry ids placed on a new program's initial stack.

## Important APIs, Types, And Functions
Exports `AT_*` constants for program headers, page size, interpreter base, entry point, uid/gid/euid/egid, platform strings, hardware capability words, clock tick, secure mode, random bytes, rseq feature size/alignment, executable filename, and minimum signal stack size. It includes architecture-specific auxvec additions first.

## Control Flow
During exec, the kernel builds an auxiliary vector of type/value pairs. The dynamic loader and libc read entries to locate ELF headers, determine platform/hwcap optimizations, seed randomness, enable secure mode behavior, and configure rseq/signal-stack expectations.

## State And Persistence
Auxv data is per exec image and remains readable through process startup mechanisms such as `getauxval()` or `/proc/self/auxv`. It is not persistent beyond the process.

## Dependencies And Integration Points
Depends on `<asm/auxvec.h>` for architecture-specific entries. Integrates with ELF loaders, libc, CPU feature dispatch, security mode handling, rseq, and procfs auxv exposure.

## Risks And Edge Cases
Architecture-specific entries can overlap if not coordinated, secure-mode handling is security-sensitive, `AT_RANDOM` points to process memory, and hardware capability interpretation is arch-specific.

## Test Signals
Exec/getauxval tests, `/proc/self/auxv` parsing, dynamic-loader startup tests, secure-exec behavior, hwcap dispatch checks, and rseq auxv value validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auxvec.h -->
