# Group Research: group_611_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__f35479c7b3e6

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_impl.h

## Purpose
Defines the illumos MPAPI kernel/driver ioctl ABI used by multipathing code, especially `scsi_vhci`, to exchange plugin, device-product, logical-unit, path, initiator-port, target-port, target-port-group, and proprietary load-balance properties with MPAPI consumers.

## Main Interfaces
- Shared MPAPI property structures:
  - `mp_driver_prop_t`
  - `mp_vendor_prod_info_t`
  - `mp_dev_prod_prop_t`
  - `mp_logical_unit_prop_t`
  - `mp_init_port_prop_t`
  - `mp_target_port_prop_t`
  - `mp_tpg_prop_t`
  - `mp_path_prop_t`
  - `mp_proprietary_loadbalance_prop_t`
- Command input structures:
  - `mp_lu_tpg_pair_t`
  - `mp_set_tpg_state_req_t`
  - `mp_set_lu_lb_type_req_t`
- SCSI passthrough support:
  - `mp_uscsi_cmd_t` carries `scsi_address`, `uscsi_cmd`, buffers, pathinfo, and auto-request-sense state.
- Ioctl payload headers:
  - `mp_iocdata_t`
  - `mp_iocdata32_t` under `_KERNEL` and `_SYSCALL32`
- Constants for:
  - MP transfer direction (`MP_XFER_*`)
  - object types (`MP_OBJECT_TYPE_*`)
  - ioctl command and subcommands (`MP_CMD`, `MP_GET_*`, `MP_SET_*`, `MP_SEND_SCSI_CMD`)
  - load-balance types, name types, transport types, ALUA access states, path states, and MPAPI driver error values
  - object ID packing/extraction macros
  - sysevent class/subclass strings for plugin, LU, path, initiator, TPG, target-port, and product changes.

## Dependencies And Relationships
Includes `sys/sunmdi.h`, `sys/sunddi.h`, `sys/mdi_impldefs.h`, and `sys/debug.h`. The structures are consumed by MPAPI ioctl handling and by `mpapi_scsi_vhci.h`, which layers `scsi_vhci` object-list state on top of these public-ish property records.

## Research Notes
The file explicitly states that all structures except `mp_iocdata_t` are kept 64-bit aligned so the same layouts can serve 32-bit and 64-bit applications. The `CTASSERT` checks for `mp_driver_prop_t`, `mp_logical_unit_prop_t`, and `mp_proprietary_loadbalance_prop_t` enforce this ABI. Pointer-bearing proprietary buffers are deliberately represented as trailing `caddr_t` fields, with ILP32 padding when needed.

## Notable Risks
- This is ioctl ABI. Field order, padding, enum values, command numbers, and `CTASSERT` sizes must remain stable.
- `mp_iocdata32_t` compatibility depends on packing and 32-bit pointer/size translation matching the native ioctl contract.
- ID helper macros encode major number and instance into a 64-bit object ID; changing the packing would invalidate stale-ID detection and object lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_scsi_vhci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_scsi_vhci.h

## Purpose
Defines private `scsi_vhci` MPAPI bookkeeping structures: object IDs, generic item/list containers, and per-object cached data used to expose initiator ports, logical units, paths, target port groups, and target ports through the MPAPI ioctl layer.

## Main Interfaces
- Object ID representation:
  - `mp_oid_t` splits a 64-bit ID into timestamp, object type, and sequence ID with endian-aware bitfield ordering.
  - `mpoid_t` exposes the same ID as either raw `uint64_t` or decoded `mp_oid_t`.
- Generic list/item containers:
  - `mpapi_item_t` stores an OID, object-private data pointer, and mutex.
  - `mpapi_item_list_t` links items.
  - `mpapi_list_header_t` tracks head and tail.
- Cached object data:
  - `mpapi_initiator_data_t`
  - `mpapi_lu_data_t`
  - `mpapi_path_data_t`
  - `mpapi_tpg_data_t`
  - `mpapi_tport_data_t`
- Global MPAPI private state:
  - `mpapi_priv_t` stores a timestamp for stale-OID detection, per-object-type sequence counters, and one object-list header per `MP_OBJECT_TYPE_*`.

## Dependencies And Relationships
Includes `sys/scsi/adapters/mpapi_impl.h`, so all cached property structs are the ABI records from `mpapi_impl.h`. The comments refer to MDI pathinfo state, destroyed paths, standby/online path validity, and `scsi_vhci` virtual LU/path objects.

## Research Notes
`MPAPI_SCSI_MAXPCLASSLEN` fixes the path-class buffer at 25 bytes. Path and TPG data both cache a path class string, validity, and property snapshots. `mpapi_path_data_t` has separate `valid` and `hide` flags: `hide` is used when a path was destroyed or should have been destroyed, and forces invalid visibility.

## Notable Risks
- `mp_oid_t` uses C bitfields and therefore requires `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`; endian handling is part of the object-ID ABI.
- List and item structures carry mutex-protected mutable state, so object removal and stale-OID detection must stay synchronized with MDI path lifecycle changes.
- The sequence counter array is indexed by MP object type; object-type constants from `mpapi_impl.h` must stay within `MP_MAX_OBJECT_TYPE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_scsi_vhci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2.h

## Purpose
Defines Broadcom/LSI/Avago Fusion-MPT MPI v2.x core firmware ABI structures and constants for illumos SCSI/SAS/NVMe-capable adapter drivers. It covers MPI versioning, IOC state and register layout, request/reply descriptors, message function IDs, common IOC status codes, common request/reply headers, LUN masks, and MPI/IEEE scatter-gather element formats.

## Main Interfaces
- MPI version and header constants:
  - MPI 2.0, 2.5, and 2.6 version macros
  - `MPI2_HEADER_VERSION_UNIT` value `0x2E`
  - `MPI2_HEADER_VERSION`
- IOC state and system-interface register ABI:
  - `MPI2_SYSTEM_INTERFACE_REGS`
  - doorbell, write-sequence, host diagnostic, diagnostic read/write, interrupt, reply-free, reply-post, host-context-buffer, scratchpad, request-post, and atomic request-post offsets and masks
  - hard reset timing constants
- Request descriptors:
  - `MPI2_DEFAULT_REQUEST_DESCRIPTOR`
  - `MPI2_HIGH_PRIORITY_REQUEST_DESCRIPTOR`
  - `MPI2_SCSI_IO_REQUEST_DESCRIPTOR`
  - `MPI2_SCSI_TARGET_REQUEST_DESCRIPTOR`
  - `MPI2_RAID_ACCEL_REQUEST_DESCRIPTOR`
  - MPI 2.5 fast-path and MPI 2.6 PCIe-encapsulated aliases
  - `MPI2_REQUEST_DESCRIPTOR_UNION`
  - `MPI26_ATOMIC_REQUEST_DESCRIPTOR`
- Reply descriptors:
  - `MPI2_DEFAULT_REPLY_DESCRIPTOR`
  - `MPI2_ADDRESS_REPLY_DESCRIPTOR`
  - `MPI2_SCSI_IO_SUCCESS_REPLY_DESCRIPTOR`
  - `MPI2_TARGETASSIST_SUCCESS_REPLY_DESCRIPTOR`
  - `MPI2_TARGET_COMMAND_BUFFER_REPLY_DESCRIPTOR`
  - `MPI2_RAID_ACCELERATOR_SUCCESS_REPLY_DESCRIPTOR`
  - MPI 2.5 fast-path and MPI 2.6 PCIe-encapsulated aliases
  - `MPI2_REPLY_DESCRIPTORS_UNION`
- Message function codes for SCSI I/O, task management, IOC init/facts, config, port facts/enable, events, firmware download/upload, RAID, toolbox, enclosure processor, SMP/SATA passthrough, diagnostic operations, target command buffers, host discovery, power management, host messages, NVMe encapsulation, product-specific functions, doorbell reset, and handshake.
- Common IOC status and log-info constants for general errors, config, SCSI, EEDP, target mode, SAS SMP, diagnostic release, RAID accelerator, and log-info availability.
- Common message structures:
  - `MPI2_REQUEST_HEADER`
  - `MPI2_DEFAULT_REPLY`
  - `MPI2_VERSION_STRUCT`
  - `MPI2_VERSION_UNION`
  - shared LUN addressing masks
- MPI scatter/gather structures and helpers:
  - simple 32/64-bit SGEs
  - chain 32/64-bit SGEs
  - transaction context SGEs for 32/64/96/128-bit contexts
  - MPI SGE unions
  - SGE flags, length, chain offset, and read-modify-write helper macros
- IEEE scatter/gather structures and helpers:
  - IEEE simple 32/64-bit SGEs
  - IEEE chain SGEs for MPI 2.0 and MPI 2.5+
  - IEEE SGE unions
  - IEEE element type, next-segment-format, address-space flags, and helper macros
- Combined MPI/IEEE SGE unions and `SGLFlags` values for address space and SGL type selection.

## Dependencies And Relationships
This header assumes base MPI integer and pointer typedefs such as `U8`, `U16`, `U32`, `U64`, and `MPI2_POINTER` are available from surrounding MPI headers. It is the common low-level dependency for MPI v2 adapter message headers that define SCSI, IOC, config, RAID, SAS, and other function-specific payloads.

## Research Notes
The header identifies itself as `mpi2.h` version `02.00.46`, with history through September 2, 2016. Names prefixed `MPI25`/`Mpi25` are for MPI v2.5 products, while `MPI26` additions cover MPI v2.6 features such as scratchpad registers, atomic request descriptor posting, PCIe/NVMe encapsulation, and selected IEEE SGE next-segment formats.

## Notable Risks
- This is a firmware hardware ABI. Register offsets, descriptor sizes, flags, function IDs, and status codes must match adapter firmware exactly.
- Several SGE macros are explicitly read-modify-write operations; callers must avoid accumulating stale flags or lengths into reused descriptors.
- MPI 2.0, 2.5, and 2.6 structures coexist in one header. Driver code must choose the correct descriptor, SGE format, and feature bits for the controller generation.
- `MPI2_SYSTEM_INTERFACE_REGS` is declared `volatile`, reflecting MMIO semantics; consumers must preserve ordering and avoid treating it as ordinary memory.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2.h -->