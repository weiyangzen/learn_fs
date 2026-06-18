# subset-b-005891 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_fpga.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_fpga.h

## Purpose
This header defines Mellanox mlx5 FPGA firmware interface layouts. It is a pure command/event ABI description: every `*_bits` structure is a bit-accurate mailbox, capability, or event record consumed by mlx5 command-building code via the generated `MLX5_GET`/`MLX5_SET` style accessors used throughout the driver. It has no executable control flow of its own.

## Important APIs, Types, And Data
- `struct mlx5_ifc_fpga_shell_caps_bits` and `struct mlx5_ifc_fpga_cap_bits` describe FPGA identity, firmware/image metadata, register access modes, DDR/control-register apertures, sandbox capabilities, and shell QP support.
- `MLX5_FPGA_CTRL_OPERATION_*` plus `struct mlx5_ifc_fpga_ctrl_bits` define control operations for image load, FPGA reset, flash selection, sandbox bypass, and sandbox reset.
- `struct mlx5_ifc_fpga_access_reg_bits` describes variable-size register access with `size`, 64-bit `address`, and flexible trailing byte data. `MLX5_FPGA_ACCESS_REG_SIZE_MAX` caps payloads at 64 bytes.
- `enum mlx5_ifc_fpga_qp_state`, `enum mlx5_ifc_fpga_qp_type`, and `enum mlx5_ifc_fpga_qp_service_type` define the FPGA QP state/type subset.
- `struct mlx5_ifc_fpga_qpc_bits` is the FPGA QP context. It carries state, QP type, traffic class, VLAN/PKey, PSNs, remote QPN, retry/RNR counters, remote/local MACs, and 16-byte IP addresses.
- Create, modify, query, counter-query, and destroy command input/output structures wrap `fpga_qpc` and expose `fpga_qpn`, `field_select`, `clear`, status, and syndrome fields.
- `struct mlx5_ifc_fpga_error_event_bits` and `struct mlx5_ifc_fpga_qp_error_event_bits` define asynchronous event payloads, including syndrome and failing FPGA QPN.

## Control Flow
Consumers query `mlx5_ifc_fpga_cap_bits` first to decide whether control/register/QP operations are legal, then build command mailboxes using the command-specific input structures. QP lifecycle follows create to query/modify to counter-query to destroy. Error handling is event-driven: the device reports one of the FPGA or FPGA-QP syndromes and upper layers map those values into driver log or recovery behavior.

## State And Persistence
State lives in device firmware, not in this header. Persistent or long-lived values include selected flash image, loaded image metadata, FPGA control state, sandbox bypass state, FPGA QP contexts, and QP counters. Kernel memory only holds encoded command buffers and decoded event/counter data.

## Dependencies And Integration Points
The file depends on common mlx5 IFC conventions: `u8 field[bits]` arrays, generated access macros, opcode values from other mlx5 command headers, and `mlx5_core_dev` command execution in the mlx5 core/FPGA code. The FPGA QP context overlaps semantically with RDMA/ethernet queue concepts but is a separate firmware ABI.

## Risks
The structures are bit-position sensitive; changing reserved field lengths or field order breaks firmware compatibility. Flexible register data must be bounded by `MLX5_FPGA_ACCESS_REG_SIZE_MAX`. QP fields combine network byte-order hardware values, PSNs, MACs, and IP arrays, so callers must populate them with the expected endianness and address family layout. Field-select masks for modify commands must match firmware-supported writable fields or modifications can silently fail with syndromes.

## Test Signals
Build coverage should compile mlx5 FPGA command users with these layouts. Runtime signals include successful FPGA capability queries, successful register access at boundary sizes 0 and 64, create/query/modify/destroy QP round trips, counter clear behavior, and injection or observation of each FPGA error event syndrome. ABI regression tests should check expected structure sizes and offsets when generated IFC tooling is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_fpga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_vdpa.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_vdpa.h

## Purpose
This header defines mlx5 firmware interface objects for vDPA/virtio-net queue offload. It is an ABI layer for creating, modifying, querying, destroying, and counting virtio queue objects through mlx5 general object commands.

## Important APIs, Types, And Data
- Queue event mode enums select no MSI-X, QP-backed events, or MSI-X events.
- Queue type enums distinguish split and packed virtio rings. Capability bits expose split/packed support via `BIT()`.
- `struct mlx5_ifc_virtio_q_bits` is the low-level virtio queue context: queue type/index/size, event mode, feature toggles, event QPN or MSI-X vector, emulation id, descriptor/used/available addresses, queue mkey, tunnel descriptor limit, error type, three UMEM windows, counter set, PD, and descriptor-group mkey.
- `struct mlx5_ifc_virtio_net_q_object_bits` wraps queue state, modify field mask, VHCA id, feature bits, dirty bitmap logging fields, TIS/QPN target, hardware available/used indexes, and the nested queue context.
- `mlx5_ifc_create/query/modify/destroy_virtio_net_q_*` structs use mlx5 general object command headers.
- `MLX5_VIRTQ_MODIFY_MASK_*` enumerates writable fields for queue modify operations.
- `MLX5_VIRTIO_NET_Q_OBJECT_STATE_*` defines INIT, RDY, SUSPEND, and ERR object states; `MLX5_VIRTIO_NET_Q_OBJECT_NONE` is a sentinel for no object.
- `struct mlx5_ifc_virtio_q_counters_bits` and related create/destroy/query command structures expose descriptor and error counters.

## Control Flow
A vDPA driver allocates an mlx5 general object for each virtio-net queue, initializes queue memory addresses and keys, transitions the object state to ready, optionally updates indexes/features/dirty logging through modify masks, queries state or counters, and destroys the object during queue teardown. Dirty bitmap fields support live migration flows where logging is enabled, queried or dumped elsewhere, and later disabled.

## State And Persistence
Persistent state is firmware-resident per queue object: queue state, ring addresses, mkeys, queue indexes, dirty bitmap parameters, and counters. Host state consists of command buffers and software handles to the firmware object ids. Counters persist until destroyed or reset by firmware semantics outside this header.

## Dependencies And Integration Points
The header relies on `mlx5_ifc_general_obj_in_cmd_hdr_bits` and `mlx5_ifc_general_obj_out_cmd_hdr_bits` from the broader mlx5 IFC definitions. It integrates with the mlx5 vDPA driver, virtio/vhost memory registration, protection domains, UMEM/mkey setup, MSI-X or QP event wiring, and live migration dirty logging.

## Risks
Firmware compatibility is highly sensitive to bit offsets. Split versus packed queue support must be checked before programming `virtio_q_type`. Ring addresses, queue size, and mkeys must correspond to valid DMA/IOMMU mappings; stale mappings can corrupt guest memory. Modify operations must set the right `modify_field_select` bit or firmware may ignore changed fields. Dirty bitmap size/address/mkey mismatches risk incorrect live migration data.

## Test Signals
Useful signals include create/modify/query/destroy cycles for split and packed queues, transitions through INIT/RDY/SUSPEND/ERR paths, event delivery in MSI-X and QP modes, dirty bitmap enable/disable during migration tests, counter increments for received/completed descriptors, and negative tests for unsupported queue type or invalid mkey/address combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_vdpa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/mpfs.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/mpfs.h

## Purpose
This header declares the mlx5 MPFS MAC filtering hook used by other mlx5 components to add or remove MAC addresses from firmware-managed multi-physical-function steering/filtering state. It also provides no-op stubs when `CONFIG_MLX5_MPFS` is disabled.

## Important APIs, Types, And Data
- `struct mlx5_core_dev` is forward-declared to avoid including the full driver header.
- `mlx5_mpfs_add_mac(struct mlx5_core_dev *dev, u8 *mac)` registers a MAC address for the device when MPFS is enabled.
- `mlx5_mpfs_del_mac(struct mlx5_core_dev *dev, u8 *mac)` removes the registered MAC address.
- Disabled-config inline stubs return 0, making callers independent of the build option.

## Control Flow
Callers invoke add during netdev/vport setup and delete during teardown or address change. Under `CONFIG_MLX5_MPFS`, implementation code performs actual firmware or steering table updates. Without MPFS, calls succeed without side effects.

## State And Persistence
When enabled, MPFS state is expected to live in the mlx5 device/firmware or driver-private steering tables. The header itself stores nothing. Disabled builds persist no MPFS state and treat every add/delete as successful.

## Dependencies And Integration Points
The API integrates with mlx5 core device lifecycle and Ethernet address management. It depends on the Kconfig symbol `CONFIG_MLX5_MPFS` and `u8` from kernel integer typedefs.

## Risks
The no-op fallback can hide missing filtering behavior in configurations that expected hardware MPFS enforcement. Callers must ensure MAC pointers reference at least `ETH_ALEN` bytes and have stable contents for the duration of the call. Enabled implementations must handle duplicate adds and deletes of absent MACs consistently.

## Test Signals
Compile both enabled and disabled MPFS configurations. Runtime tests should verify MAC filter programming on enabled hardware, duplicate add/delete behavior, teardown cleanup, and that disabled builds do not fail callers that treat MPFS as optional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/mpfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/port.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/port.h

## Purpose
This header exposes mlx5 port capability, link mode, module EEPROM, autonegotiation, MTU, and InfiniBand port query interfaces. It is a declaration and constants layer used by mlx5 Ethernet, IB/RDMA, and management code.

## Important APIs, Types, And Data
- `enum mlx5_beacon_duration` defines off and infinite beacon duration values.
- `enum mlx5_module_id` identifies common transceiver module types such as SFP, QSFP, QSFP+, QSFP28, and DSFP.
- `enum mlx5_an_status` describes autonegotiation status values.
- I2C and EEPROM constants define low/high module I2C addresses and page sizes.
- `enum mlx5e_link_mode` and `enum mlx5e_ext_link_mode` map firmware link-mode bits to Ethernet media/rate names from 100M through 1600G classes.
- `enum mlx5e_connector_type` identifies physical connector categories.
- `enum mlx5_ptys_width` defines lane width masks.
- `MLX5E_PROT_MASK()` and `MLX5_GET_ETH_PROTO()` help construct mode masks and select standard versus extended PTYS fields.
- Exported functions query or modify port capabilities, PTYS, IB operational width/protocol, max/oper MTU, and VL hardware capability.

## Control Flow
Drivers query PTYS and module metadata to build ethtool link mode displays, validate requested speed/lane changes, and read active negotiated state. Port capability modification is explicit through `mlx5_set_port_caps()`. MTU and IB operational attributes are queried as needed by netdev and RDMA setup paths.

## State And Persistence
Port state is maintained by device firmware and physical link hardware: advertised/operational modes, module identity, MTU, VL capability, and autoneg status. The header maintains no state but defines the enum values that must match firmware registers.

## Dependencies And Integration Points
It includes `linux/mlx5/driver.h` for `struct mlx5_core_dev` and mlx5 access helpers. It integrates with mlx5e ethtool, devlink/port management, RDMA port queries, module EEPROM reads, and firmware PTYS register access.

## Risks
Link mode enum numeric values must match firmware bit positions. Adding modes requires updates in display/mapping tables outside this file. `MLX5_GET_ETH_PROTO()` must be called with the correct `ext` selector and register layout. Multi-plane or multi-port callers must pass correct `local_port` and `plane_index` to avoid reporting or configuring the wrong port.

## Test Signals
Compile-time users should cover all enum values in mapping tables. Runtime signals include ethtool advertised/supported mode output, module EEPROM reads at both I2C pages, successful MTU queries, IB operational width/protocol queries, and link-mode negotiation tests on standard and extended PTYS-capable devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/qp.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/qp.h

## Purpose
This header centralizes mlx5 queue pair and work queue element definitions. It provides QP state/type constants, send WQE segment layouts, address vector structures, memory registration/protection-signature descriptors, data-segment formats, debug hooks, and small helpers used by mlx5 core, RDMA, Ethernet, storage offload, and packet-processing paths.

## Important APIs, Types, And Data
- QP constants include terminate scatter-list lkey, signature WQE size, DIF/protection masks, block signature flags, WQE block sizes, DS units, max WQE size, receive/send doorbell indexes, and inline/check flags.
- `enum mlx5_qp_optpar` defines modify-QP optional parameter bits such as alternate path, RRE/RAE/RWE, PKey, QKey, RNR timeout/retry, primary path, retry count, LAG affinity, SRQ/CQ bindings, DC fields, and counter set id.
- `enum mlx5_qp_state` defines reset/init/RTR/RTS/SQ error/SQD/error/draining/suspended states.
- QP service types include RC, UC, UD, XRC, MLX, DCI/DCT, special QP0/QP1, raw transport, sniffer, UMR, PTP, and max sentinel.
- WQE layout structs include FMR, control, Ethernet, XRC, masked atomic, datagram, remote address, atomic, data, UMR control, PSV get/set/check, signature, inline, block signature format, MTT/KLM/KSM, stride blocks, flow update, and header modify argument update segments.
- `struct mlx5_base_av`, `struct mlx5_av`, and `struct mlx5_ib_ah` represent address vectors and RDMA address handles.
- `struct mlx5_core_qp` embeds `mlx5_core_rsc_common` first for resource tracking, an event callback, QPN, debug handle, process id, and UID.
- `struct mlx5_core_dct` wraps a core QP and drained completion.
- `mlx5_debug_qp_add()` and `mlx5_debug_qp_remove()` register debug visibility.
- `mlx5_qp_type_str()` and `mlx5_qp_state_str()` convert transport/state values to strings.
- `mlx5_get_qp_default_ts()` selects default versus free-running timestamp format based on RoCE or general SQ timestamp capabilities.

## Control Flow
The header defines data consumed by WQE builders and QP state-machine code. Callers assemble control and payload segments in hardware order, ring doorbells elsewhere, and receive completion/error events through device queues. QP lifecycle logic outside this header uses state and optional-parameter enums to drive modify commands. Inline helpers only perform local switch-based string conversion or capability checks for timestamp format.

## State And Persistence
Hardware QP state, WQEs, PSNs, counters, and memory-key references are stored in device queues and firmware contexts. `struct mlx5_core_qp` stores software identity and callback state for a tracked QP resource. WQE segment contents are transient descriptors in send queues. Debug registration can persist while the QP exists.

## Dependencies And Integration Points
The header includes `linux/mlx5/device.h` and `linux/mlx5/driver.h`, uses RDMA core types such as `struct ib_ah`, and depends on endian fixed-width types. It integrates with mlx5 command code, RDMA verbs providers, Ethernet SQ builders, storage integrity offloads, UMR/mkey management, MACsec/IPsec metadata, and resource tracking/debugfs.

## Risks
All WQE layouts are hardware ABI and endian sensitive. Incorrect DS counts, inline lengths, masks, or segment ordering can produce device syndromes or memory corruption. `mlx5_ib_ah` assumes `struct ib_ah` embedding for `container_of`. `mlx5_get_qp_default_ts()` depends on accurate capability reporting and RoCE state. Large comments around signature/DIF constants indicate cross-feature coupling with storage integrity and UMR WQE sizing.

## Test Signals
Build tests should cover RDMA and Ethernet configurations. Runtime signals include QP create/modify transitions across states, WQE posting for send, RDMA read/write, atomic, UMR, inline, and checksum offload paths; debug QP registration visibility; timestamp format behavior with and without RoCE; and fault injection for malformed WQEs or invalid QP state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/rsc_dump.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/rsc_dump.h

## Purpose
This header declares the mlx5 resource dump interface. It lets callers describe a firmware resource or resource range and iteratively retrieve dump segments into pages for diagnostics.

## Important APIs, Types, And Data
- `enum mlx5_sgmt_type` lists supported dump segment/resource types: hardware CQ/SQ/RQ contexts, full SRQ/CQ/EQ/QP contexts, send/receive/SRQ/CQ/EQ buffers, SX/RX slices, RDB, PRM query QP/CQ/MKEY, menu, terminate, and a count sentinel.
- `struct mlx5_rsc_key` identifies the resource to dump: segment type, two indexes, two object counts, and expected size.
- `struct mlx5_rsc_dump_cmd` is opaque to callers.
- `mlx5_rsc_dump_cmd_create()` allocates/prepares a dump command for a device and key.
- `mlx5_rsc_dump_next()` streams the next chunk into a caller-supplied `struct page` and returns its size.
- `mlx5_rsc_dump_cmd_destroy()` tears down command state.

## Control Flow
Diagnostic code creates a dump command from a key, repeatedly calls `mlx5_rsc_dump_next()` until firmware indicates completion or error, then destroys the command. The menu and terminate segment types allow discovery and stream termination semantics.

## State And Persistence
The opaque command object holds iteration state for an in-progress dump. Dumped resource data is a snapshot or firmware stream; this header does not persist it beyond pages supplied by callers. Firmware resources being dumped continue to live independently.

## Dependencies And Integration Points
It includes `linux/mlx5/driver.h` for device definitions and uses `struct page` for output buffers. It integrates with mlx5 diagnostics, devlink health reporters, debugfs, or crash-analysis paths that need firmware-visible resource state.

## Risks
Callers must destroy commands on all error paths. Segment indexes/counts/sizes must match firmware expectations or the dump may fail or return misleading data. Output pages must be valid and sized for the reported segment payload. Dumping live resources can race with resource teardown unless the implementation pins or validates objects.

## Test Signals
Tests should create and destroy commands for menu queries and representative QP/CQ/MKEY resources, iterate until completion, validate nonzero sizes, exercise invalid keys, and run dumps while resources are being created and destroyed to check cleanup and race handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/rsc_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/transobj.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/transobj.h

## Purpose
This header declares mlx5 transport object management APIs. It covers allocation of transport domains, creation/query/modification/destruction of receive queues, send queues, TIRs, TISs, RQTs, and hairpin queue pairs.

## Important APIs, Types, And Data
- `mlx5_core_alloc_transport_domain()` and `mlx5_core_dealloc_transport_domain()` manage transport domain numbers.
- RQ APIs: `mlx5_core_create_rq()`, `mlx5_core_modify_rq()`, `mlx5_core_destroy_rq()`, `mlx5_core_query_rq()`.
- SQ APIs: `mlx5_core_create_sq()`, `mlx5_core_modify_sq()`, `mlx5_core_destroy_sq()`, `mlx5_core_query_sq()`, `mlx5_core_query_sq_state()`.
- TIR/TIS APIs create, modify where supported, and destroy transport interface receive/send objects.
- RQT APIs create, modify, and destroy receive queue tables.
- `struct mlx5_hairpin_params` captures log data size, log packet count, queue counter, and channel count.
- `struct mlx5_hairpin` stores function and peer mlx5 devices, channel count, RQN/SQN arrays, and a `peer_gone` flag.
- Hairpin APIs create, destroy, and clear dead peer state.

## Control Flow
Networking code allocates transport domains, creates queues and indirection objects, wires RQTs into TIRs or TIS/SQ paths, modifies objects as configuration changes, queries state for validation/debug, and destroys objects in reverse order. Hairpin creation builds paired SQ/RQ objects across a function device and peer device for direct packet redirection; peer-death handling marks or clears state to prevent unsafe access.

## State And Persistence
Firmware owns object state identified by RQN, SQN, TIRN, TISN, RQTN, and TDN values. The hairpin structure persists driver-side arrays of queue numbers and peer identity until destroyed. No state is stored in this header.

## Dependencies And Integration Points
It includes `linux/mlx5/driver.h` and integrates with mlx5e channels, representors, eswitch/offload flows, RSS/RQT setup, queue counters, and multi-device hairpin forwarding. Command buffers are raw `u32 *in/out`, so callers depend on mlx5 IFC layout headers for object contexts.

## Risks
Object lifecycle ordering matters: destroying an object still referenced by a TIR/TIS/RQT or flow table can break traffic. Raw command buffers increase the risk of malformed input lengths or missing required fields. Hairpin creation spans two devices, so peer teardown races and partial creation failures must be handled carefully. `peer_gone` state must be honored by destroy/cleanup code.

## Test Signals
Runtime tests should cover create/query/modify/destroy for RQ, SQ, TIR, TIS, and RQT objects, SQ state queries, transport domain leak checks, RSS table updates, hairpin traffic forwarding, peer removal during active hairpin use, and rollback from injected command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/transobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/vport.h -->
# sources/distributed-fs/ceph-client/include/linux/mlx5/vport.h

## Purpose
This header exposes mlx5 virtual port management APIs for PF/VF/ECPF/uplink contexts. It covers vport state, MAC/GUID/MTU/min-inline settings, speeds, RoCE enablement, lists and promiscuity, VLANs, counters, HCA vport attributes, multiport affiliation, local loopback, and other-function capabilities.

## Important APIs, Types, And Data
- `MLX5_VPORT_MANAGER(mdev)` tests whether a device is an Ethernet PF with vport group manager capability.
- Vport ids identify PF (`0`), first VF (`1`), ECPF (`0xfffe`), and uplink (`0xffff`).
- Inline mode constants describe L2, vport-context, and not-required modes.
- Query/modify functions cover vport admin state, max TX speed, MAC address, min inline, MTU, system image GUID, SD group, node GUID, QKey violation counter, GID/PKey/HCA contexts, MAC lists, promiscuity, VLAN lists, down stats, vport counters, HCA vport context, local loopback, multiport affiliation, system image GUID, other function caps, and VHCA id.
- RoCE helpers enable or disable RoCE on the NIC vport.

## Control Flow
PF management and eswitch code first checks manager capability, then queries target vport state and capabilities, applies configuration through modify calls, and reads counters or stats for monitoring. VF and other-vport operations pass `other_vport`/`vf_num`/`vport` selectors. Multiport affiliation links a master device with a port device and later unaffiliates during teardown.

## State And Persistence
Vport configuration is firmware-resident and can affect link behavior, packet steering, RDMA identity, and VF presentation. Driver state tracks the relevant `mlx5_core_dev` and target vport ids, while the header only declares interfaces and constants.

## Dependencies And Integration Points
The file includes `linux/mlx5/driver.h` and `linux/mlx5/device.h` for device, capability, list type, and HCA context definitions. It integrates with SR-IOV, eswitch, representors, netdev address/MTU setup, RDMA GID/PKey handling, devlink, and multiport devices.

## Risks
Most APIs operate on firmware state for a selected vport; incorrect `other_vport`, VF number, or uplink/PF id can change the wrong function. Capability checks are required before manager-only operations. MAC/VLAN list sizes must match firmware limits. RoCE and GUID changes can affect RDMA users. Multiport affiliation must handle device removal and rollback.

## Test Signals
Tests should cover PF manager detection, PF/VF/uplink vport state queries, MAC/MTU/min-inline update and readback, max TX speed changes, MAC list and promiscuity programming, VLAN list updates, RoCE enable/disable, GID/PKey queries, vport counter reads, local loopback toggles, VHCA id lookup, and multiport affiliate/unaffiliate teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/vport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm.h -->
# sources/distributed-fs/ceph-client/include/linux/mm.h

## Purpose
This is the central public Linux memory-management header in this source tree. It declares core MM initialization, VMA flags and operations, page/folio helpers, page fault structures, GUP and pinning APIs, mmap/munmap/protection interfaces, page-table allocation and locking helpers, page-cache and truncate APIs, memory hotplug/vmemmap helpers, memory failure handling, page poisoning/debug-pagealloc hooks, and several local extensions around typed `vma_flags_t`, mmap action preparation, page snapshots, and anonymous PTE mapping without page faults.

## Important APIs, Types, And Data
- Initialization and accounting: `arch_mm_preinit()`, `mm_core_init_early()`, `mm_core_init()`, `init_mm_internals()`, `_totalram_pages`, `totalram_pages*()`, `high_memory`, reserve sysctls, and max map count constants.
- Address and page utilities: `PAGE_ALIGN`, `PAGE_ALIGN_DOWN`, `PAGE_ALIGNED`, `page_to_virt`, `lm_alias`, `mm_zero_struct_page()`, `folio_page_idx()`, `lru_to_folio()`, `page_range_contiguous()`.
- VMA flag model: typed `vma_flag_t` enum entries, legacy `VM_*` masks, typed `VMA_*` combinations, `VM_SPECIAL`, `VMA_REMAP_FLAGS`, `VM_COPY_ON_FORK`, stack/default data flags, atomic-update allow mask, and sticky merge flags.
- Fault handling: `FAULT_FLAG_DEFAULT`, `FAULT_FLAG_TRACE`, `fault_flag_allow_retry_first()`, `struct vm_fault`, `release_fault_lock()`, `assert_fault_locked()`, `handle_mm_fault()`, `fixup_user_fault()`, and `vm_fault_to_errno()`.
- `struct vm_operations_struct` defines VMA callbacks: open/close/mapped/may_split/mremap/mprotect/fault/huge_fault/map_pages/pagesize/page_mkwrite/pfn_mkwrite/access/name/NUMA policy/find_normal_page/userfaultfd operations.
- VMA lifecycle and flags: `vm_area_alloc()`, `vm_area_dup()`, `vm_area_free()`, `vma_init()`, `vm_flags_init/reset/set/clear/mod`, typed `vma_flags_*` builders/tests/set/clear/diff/same helpers, VMA and `vm_area_desc` flag wrappers, anonymous/heap/stack/accessibility helpers, and Maple Tree iterators.
- Folio/page reference and mapping helpers: compound/folio order, mapcount/mapped checks, `folio_get/put`, `release_pages()`, GUP pin bias, DMA-pinned checks, COW-for-DMA checks, node/zone/KASAN tag helpers, PFN/PTE/PMD/PUD constructors, folio size/count iteration helpers, expected refcount, page address helpers, and pfmemalloc markers.
- Unmapping and page cache: `zap_details`, `ZAP_FLAG_*`, `vm_normal_*`, `zap_vma_range()`, `copy_page_range()`, `follow_pfnmap_*`, truncate/pagecache functions, `unmap_mapping_*()`, filemap fault helpers, dirty helpers, and page dirty APIs.
- User memory access and pinning: `access_process_vm()`, `access_remote_vm()`, `get_user_pages*()`, `pin_user_pages*()`, `memfd_pin_folios()`, `unpin_user_page*()`, `folio_add_pin(s)`, and `get_user_page_vma_remote()`.
- Protection and mmap: `change_protection()`, `mprotect_fixup()`, RSS counters, page-table alloc/free/lock helpers, `find_vma*()`, `do_mmap()`, `do_munmap()`, `vm_mmap()`, `vm_munmap()`, `do_madvise()`, `expand_stack*()`, `vm_unmapped_area()`, stack guard helpers, and `vma_set_page_prot()`.
- Local mmap action helpers: `mmap_action_remap*()`, `mmap_action_ioremap*()`, `mmap_action_simple_ioremap()`, `mmap_action_map_kernel_pages*()`, `mmap_action_prepare()`, and `mmap_action_complete()` use `struct vm_area_desc` and `struct mmap_action`.
- Insertion/remap helpers: `remap_pfn_range()`, `vm_insert_page(s)`, `vm_map_pages*()`, `vmf_insert_*()`, `io_remap_pfn_range()`, `vmf_error()`, and `vmf_fs_error()`.
- Debug/hardening/hotplug: page poisoning, init-on-alloc/free static keys, debug pagealloc/guard pages, gate area hooks, sparse/vmemmap population, altmap helpers, vmemmap optimization, memory failure enums and APIs, unaccepted memory APIs, mseal, shadow-stack status hooks, page pool DMA index masks, `struct page_snapshot`, `snapshot_page()`, and `map_anon_folio_pte_nopf()`.

## Control Flow
The header mostly wires subsystem boundaries. Typical paths include mmap setup through `do_mmap()`/`mmap_prepare` descriptors, VMA flag initialization, optional mmap action preparation/completion, page faults through `handle_mm_fault()` into `vm_operations_struct` callbacks, PTE/PMD installation through page-table allocation helpers, and teardown through zap/unmap/truncate functions. Folio lifetimes flow through reference acquisition, mapcount/accounting changes, GUP/pin tracking, dirty/writeback/truncate operations, and final `folio_put()` release. Page-table lifetimes flow through allocation, constructor/lock initialization, use through offset-map helpers, destructor, and free.

## State And Persistence
Key persistent state is held in `mm_struct`, `vm_area_struct`, Maple Tree VMA indexes, `struct page`/`struct folio`, page tables, page cache mappings, memcg/vmstat counters, and firmware or device mappings for PFNMAP/DAX/I/O cases. Atomic and percpu counters track total RAM, RSS, page-table bytes, and pin counts. VMA flags persist in both legacy `vm_flags_t` and typed `vma_flags_t` views through helpers. Page poisoning, init-on-alloc/free, debug-pagealloc, memory failure, and vmemmap state are globally configured through static keys or subsystem globals.

## Dependencies And Integration Points
The file includes a broad set of kernel MM, scheduler, page table, KASAN, memremap, resource, shrinker, mmap-lock, bitmap, IOMMU debug, and architecture headers. It is consumed by nearly every memory user: filesystem mmap handlers, device drivers, RDMA/GUP users, BPF remote memory access, MMU notifiers, memory hotplug, DAX, hugetlb/THP, NUMA balancing, userfaultfd, page allocator, page table code, and architecture fault handlers.

## Risks
This header is extremely ABI and concurrency sensitive. VMA flag conversions must keep typed and legacy masks aligned, especially while conversion is incomplete. Many helpers require mmap lock, VMA lock, page-table lock, folio lock, or write-protect sequence preconditions that are documented but not enforced by types. GUP pinning deliberately overloads refcounts for small folios, so false positives and overflow handling must be understood. Page-table locking varies by configuration and architecture. PFNMAP/I/O remap helpers can expose physical memory to userspace if flags, protections, or range checks are wrong. Memory-failure, hotplug, vmemmap, and page poisoning hooks are configuration dependent and can be no-ops in some builds.

## Test Signals
Signals include `allyesconfig`/`allmodconfig` compile coverage, sparse type checking for `vma_flag_t`, mmap/mprotect/munmap regression tests, page fault and userfaultfd tests, GUP/pin/unpin and DMA-pinned COW tests, THP/hugetlb/folio split and migration tests, page-table allocation accounting, KASAN tag tests, page poisoning/debug-pagealloc tests, vmemmap hotplug/DAX optimization tests, memory failure injection, stack expansion tests, RSS counter validation, and exercising local `mmap_action_*` flows with PFN remap, I/O remap, and kernel page mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_api.h -->
# sources/distributed-fs/ceph-client/include/linux/mm_api.h

## Purpose
This file is a one-line compatibility or API shim that includes `linux/mm.h`. It gives code a stable `mm_api.h` include name while re-exporting the full MM interface from `mm.h`.

## Important APIs, Types, And Data
The file declares no independent API, type, macro, or state. Its only content is `#include <linux/mm.h>`, so all visible symbols come from `mm.h` and its transitive includes.

## Control Flow
There is no runtime control flow. During preprocessing, including `mm_api.h` is equivalent to including `linux/mm.h`.

## State And Persistence
No state is introduced or persisted by this header.

## Dependencies And Integration Points
Its sole dependency is `linux/mm.h`. It integrates with any code that wants to depend on an MM API facade instead of including the main MM header directly.

## Risks
Because it re-exports a very large header, compile-time dependencies and rebuild scope remain as broad as direct `mm.h` inclusion. Any future attempt to narrow the API must consider all existing users that rely on transitive `mm.h` declarations.

## Test Signals
Compile any translation unit that includes `linux/mm_api.h` without separately including `linux/mm.h`. Include-what-you-use or dependency scans can identify whether the shim is serving as a stable facade or merely duplicating direct includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_inline.h -->
# sources/distributed-fs/ceph-client/include/linux/mm_inline.h

## Purpose
This header contains hot-path inline memory-management helpers that are too small or performance-sensitive for out-of-line calls. It focuses on LRU list classification/accounting, multi-generational LRU integration, anonymous VMA names, pending TLB flush tracking, userfaultfd write-protect marker handling, recency checks, and contiguous page-array detection.

## Important APIs, Types, And Data
- `folio_is_file_lru()` classifies folios for file versus anonymous LRU accounting by testing `folio_test_swapbacked()`.
- `__update_lru_size()` and `update_lru_size()` update lruvec and zone LRU counters, with memcg updates under `CONFIG_MEMCG`.
- `__folio_clear_lru_flags()` clears LRU/active/unevictable flags during release.
- `folio_lru_list()` selects the correct LRU list from file/anon and active/unevictable folio flags.
- Under `CONFIG_LRU_GEN`, helpers expose feature static keys, sequence-to-generation/hist conversion, tier calculation, reference extraction, generation extraction, active generation checks, size updates, generation sequence selection, add/delete paths, and migration of reference bits.
- Non-`CONFIG_LRU_GEN` stubs return disabled/false and keep callers simple.
- `lruvec_add_folio()`, `lruvec_add_folio_tail()`, and `lruvec_del_folio()` update list membership and LRU counters, delegating to MGLRU when active.
- Anonymous VMA name helpers get/put/reuse/duplicate/free/compare `anon_vma_name` values under `CONFIG_ANON_VMA_NAME`; stubs make the feature optional.
- TLB flush helpers initialize, increment, decrement, and query `mm->tlb_flush_pending`, including nested flush detection.
- `copy_pte_marker()` and `pte_install_uffd_wp_if_needed()` preserve or install special PTE markers for userfaultfd write-protect and poisoned/guard metadata.
- `vma_has_recency()` filters VMAs that should contribute recency signals.
- `num_pages_contiguous()` returns how many entries in a page pointer array are contiguous as `struct page` entries and sparsemem sections.

## Control Flow
LRU add/delete callers classify a folio, try the MGLRU path, and fall back to classic list insertion/removal and counter updates. MGLRU add computes a sequence, encodes the generation in folio flags, updates generation and LRU counters, and inserts at head or tail depending on reclaim context. Delete clears generation bits, may restore `PG_active` for migration, updates counters, and unlinks. TLB flush tracking increments before PTE updates under PTL ordering assumptions and decrements after flush completion. UFFD marker installation occurs only when a PTE has already been cleared and the VMA/file-backed write-protect conditions match.

## State And Persistence
State lives in folio flags (`PG_lru`, `PG_active`, `PG_unevictable`, MGLRU bits, reference bits), `lruvec` lists/counters, memcg LRU counters, `mm_struct.tlb_flush_pending`, VMA anonymous names, and PTE marker entries. The header mutates these structures inline but owns no independent global state except referenced static keys declared elsewhere.

## Dependencies And Integration Points
It includes atomic, huge MM, MM type, swap, string, userfaultfd, and leafops headers. It integrates with reclaim, page cache release, memcg accounting, MGLRU, migration, userfaultfd, page-table zapping/copying, and sparsemem section handling.

## Risks
LRU helpers require `lruvec->lru_lock`; `__update_lru_size()` asserts it. Wrong LRU classification or missed counter updates corrupt reclaim accounting. MGLRU flag encoding must stay aligned with page flag definitions. TLB flush pending relies on page-table-lock ordering and architecture TLB invalidation ordering, so misuse outside the documented PTL scope is unsafe. `pte_install_uffd_wp_if_needed()` must only run on cleared PTEs under the page-table lock. `num_pages_contiguous()` reports struct-page contiguity, not guaranteed PFN contiguity in all sparsemem configs.

## Test Signals
Signals include LRU counter balance tests during folio add/delete/isolate/release, memcg LRU accounting checks, MGLRU enabled and disabled builds, folio migration preserving reference bits, reclaim rotations, userfaultfd write-protect fork/zap tests, TLB flush pending assertions under concurrent faults, anonymous VMA name refcount tests, and sparsemem page-array contiguity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_inline.h -->
