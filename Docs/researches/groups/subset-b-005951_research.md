# Research: subset-b-005951

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/ds.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/ds.h

Purpose: defines the 16-bit PCMCIA client-driver interface. It gives PCMCIA card drivers their bus driver wrapper, per-function device object, CIS/configuration helpers, resource request APIs, and configuration flag constants. It explicitly excludes 32-bit CardBus devices, which are handled through PCI.

Important APIs and types: `struct pcmcia_driver` wraps probe/remove/suspend/resume callbacks, a module owner, static ID table, dynamic IDs, and the embedded `device_driver`; `pcmcia_register_driver()`, `pcmcia_unregister_driver()`, and `module_pcmcia_driver()` are the registration surface. `struct pcmcia_device` binds a card function to its `pcmcia_socket`, device/function numbers, driver-visible resources, IRQ, Vpp, config registers, CIS IDs/product strings, DMA mask, embedded `struct device`, and driver-private data. CIS helpers include `pcmcia_get_tuple()`, `pcmcia_loop_tuple()`, `pcmcia_parse_tuple()`, `pcmcia_loop_config()`, and `pcmcia_get_mac_from_cis()`. Runtime configuration helpers include config-byte access, `pcmcia_request_io()`, `pcmcia_request_irq()`, `pcmcia_enable_device()`, memory window request/map/release, Vpp/I/O-width fixups, reset, present check, and `pcmcia_disable_device()`.

Control flow: a module registers `struct pcmcia_driver`; the PCMCIA core matches against static or dynamic IDs, creates a `pcmcia_device`, invokes `probe()`, then the driver scans CIS tuples and configurations, requests I/O/IRQ/window resources, and calls `pcmcia_enable_device()`. On card removal, suspend, or driver unload, the core drives remove/suspend/resume and the driver releases state through `pcmcia_disable_device()`.

State and persistence: the header models in-memory bus/device state only. Persistent card identity comes from CIS/manufacturer/card/product fields read from hardware; requested resources are tracked in `resource[]`, bitfields such as `_irq`, `_io`, `_win`, `_locked`, and config flags/registers. Driver-private state lives in `priv` and `open`.

Dependencies and integration points: depends on device core, module/device ID tables, interrupt handlers, atomic/list/mutex infrastructure, PCMCIA socket services from `pcmcia/ss.h`, and CIS tuple types. It integrates PCMCIA client drivers with the Linux driver model, resource allocation, IRQ setup, networking MAC discovery, and socket-level card services.

Risks and test signals: risks include failing to free tuple buffers, enabling a device without matching requested resources, stale card-present state during hot removal, IRQ/resource leaks on probe failure, incorrect multifunction `func`/`device_no` handling, and config flag drift with socket services. Test signals include PCMCIA driver bind/unbind, dynamic ID matching, CIS tuple parsing, valid/invalid config loops, hot removal while open, suspend/resume, IRQ request failure unwinds, and memory-window mapping on sockets with multiple windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/ds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/soc_common.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/soc_common.h

Purpose: declares the shared SoC PCMCIA socket adapter layer used by platform-specific low-level drivers. It embeds a generic `pcmcia_socket` and adds GPIO, regulator, clock, resource, timing, polling, and CPU-frequency state needed by non-PCI SoC controllers.

Important APIs and types: `struct pcmcia_state` captures card-detect, ready, battery/status, write-protect, and voltage-sense bits returned by low-level hardware. `struct soc_pcmcia_regulator` tracks regulator object and on/off state. `struct soc_pcmcia_socket` owns the generic socket, socket index, clock, low-level ops pointer, cached socket status/config state, I/O/memory/attribute timing arrays, resource ranges, six status GPIO/IRQ slots (`SOC_STAT_CD`, `BVD1`, `BVD2`, `RDY`, `VS1`, `VS2`), reset/bus-enable GPIOs, Vcc/Vpp regulators, optional CPUFreq notifier, poll timer, list node, and private driver data. `struct pcmcia_low_level` is the hardware callback table for init/shutdown, state sampling, socket configuration, interrupt enable/disable, timing calculation/programming/reporting, and optional frequency-change handling.

Control flow: platform code provides `pcmcia_low_level`, initializes each `soc_pcmcia_socket`, and lets common SoC code translate GPIO/state changes into generic PCMCIA socket events. Hardware init configures resources, clocks, GPIOs, IRQ/polling, and regulators; `configure_socket()` applies Vcc/Vpp/reset/output state; suspend disables status IRQs and the bus; resume or reinitialization restores status handling and timing.

State and persistence: state is per-socket kernel runtime state. Regulator `on` flags, cached `cs_state`, speed arrays, status bits, IRQ state, and resources persist only for the device lifetime and across suspend/resume while the driver remains loaded. No card data is persisted.

Dependencies and integration points: depends on `pcmcia/ss.h`, clocks, regulators, GPIO descriptors, timers, resources, optional CPUFreq notifiers, and module ownership. It bridges SoC-specific board code with generic PCMCIA socket registration and event parsing.

Risks and test signals: risks include GPIO polarity/index mistakes, regulator state desynchronization, timing not updated after CPU frequency changes, poll timer races during shutdown, and mismatched resource windows. Test by probing/removing SoC sockets, card insert/remove events via GPIO IRQ and polling, Vcc/Vpp transitions, suspend/resume, CPUFreq transition timing, and status-bit mapping for memory and I/O cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/soc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/ss.h -->
# sources/distributed-fs/ceph-client/include/pcmcia/ss.h

Purpose: defines the PCMCIA/CardBus socket-service interface between socket controller drivers and the PCMCIA core. It specifies socket status flags, capabilities, mapping descriptors, socket operations, the central `pcmcia_socket` state object, resource policy hooks, and registration/events APIs.

Important APIs and types: status flags such as `SS_DETECT`, `SS_READY`, `SS_POWERON`, `SS_CARDBUS`, and voltage/card-type bits describe current card state. `socket_state_t` holds flags, card-status-change mask, Vcc/Vpp, and I/O IRQ. `pccard_io_map`, `pccard_mem_map`, and `io_window_t` describe I/O and memory windows, with `MAX_IO_WIN` and `MAX_WIN` limiting per-socket maps. `struct pccard_operations` provides controller callbacks for init, suspend, get_status, set_socket, set_io_map, and set_mem_map. `struct pcmcia_socket` stores current/suspended socket state, CIS cache/fake CIS, I/O and memory windows, socket and resource lists, capabilities, bridge data, ops/resource ops, optional CardBus hooks, state thread fields, locking, 16-bit PCMCIA child device list/presence/IRQ, embedded device, and resume status. Public APIs are `pcmcia_parse_events()`, `pcmcia_register_socket()`, and `pcmcia_unregister_socket()`.

Control flow: a socket driver fills `pcmcia_socket`, chooses static or non-static resource ops, registers it, and calls `pcmcia_parse_events()` from its interrupt path when card-status changes occur. The core serializes socket setup with `skt_mutex` and `ops_mutex`, manages a socket thread for events/sysfs events, allocates resources only after `resource_setup_done`, and unregisters after child devices and socket references are released.

State and persistence: all state is runtime kernel state tied to the physical socket. It includes cached CIS data, fake CIS overrides, current maps, card presence, resource allocation state, state-thread events, and child device lists. Hardware power and mapping state is reflected through callback-applied `socket_state_t`, but no persistent storage is owned here.

Dependencies and integration points: integrates device model, task/completion infrastructure, mutex/spinlocks, optional PCI/CardBus, resource allocator implementations (`pccard_static_ops`, `pccard_nonstatic_ops`), PCMCIA client devices, sysfs events, and controller IRQ handlers.

Risks and test signals: risks include lock-order violations between socket and ops locks, event loss under `thread_lock`, wrong static/non-static resource selection, CIS cache lifetime bugs, CardBus-only builds accidentally pulling nonstatic resource code, and unregister races with socket thread or child devices. Test socket registration/unregistration, interrupt-driven insertion/removal, sysfs-triggered events, suspend/resume with card present, resource allocation before/after setup, CardBus config, and fake-CIS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/pcmcia/ss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ras/ras_event.h -->
# sources/distributed-fs/ceph-client/include/ras/ras_event.h

Purpose: declares RAS tracepoints for memory-controller errors, ACPI CPER extended memory errors, ARM processor errors, non-standard CPER sections, and PCIe AER errors. It is a trace-event schema header included by tracepoint users and by `trace/define_trace.h`.

Important APIs and types: `TRACE_EVENT(extlog_mem_event)` is ACPI extlog-gated and records sequence, CPER memory error type/severity, physical address/mask, FRU GUID/text, and packed compact memory-error data. `TRACE_EVENT(mc_event)` records EDAC-style memory-controller error type, labels, count, hierarchy location, address/grain/syndrome, and driver detail. `TRACE_EVENT(arm_event)` records CPER ARM processor fields, raw processor/context/OEM buffers, severity, and CPU. `TRACE_EVENT(non_standard_event)` records section GUID, FRU, severity, raw payload length, and bytes. `TRACE_EVENT(aer_event)` is `CONFIG_PCIEAER` gated and records device, status bits, severity, optional TLP header, and bus type with correctable/uncorrectable flag decoding tables.

Control flow: RAS, EDAC, ACPI/APEI, ARM CPER, and PCIe AER handlers call generated tracepoint functions when hardware reports corrected or uncorrected events. Each `TP_fast_assign` copies validated fields and raw buffers into the ring buffer, and `TP_printk` formats them for tracefs/perf/ftrace consumers.

State and persistence: the header owns no persistent state. Event data is transient trace-buffer data; CPER validation bits decide whether fields are stored or replaced with sentinel values. Trace buffers and userspace collection determine retention.

Dependencies and integration points: depends on Linux tracepoint macros, EDAC helpers, CPER structures/formatters, PCI/AER constants, GUID handling, ktime-related trace support, and `trace/define_trace.h`. It is the common observability contract across hardware error subsystems.

Risks and test signals: risks include copying raw dynamic arrays with unvalidated lengths, stale CPER validation-bit handling, formatting mismatches for GUIDs/TLP headers, config-gated tracepoint build drift, and trace ABI field-name changes breaking tooling. Test with trace-event compile checks under ACPI_EXTLOG/PCIEAER on/off, synthetic EDAC events, CPER ARM/non-standard injection, AER injection, tracefs format verification, and perf/ftrace decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ras/ras_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/frmr_pools.h -->
# sources/distributed-fs/ceph-client/include/rdma/frmr_pools.h

Purpose: declares a device-level fast-registration memory-region pool interface for RDMA devices. It lets provider drivers create/destroy batches of FRMR handles and lets core/users push or pop pool-backed memory regions.

Important APIs and types: `struct ib_frmr_key` describes pool keys with vendor key, optional kernel-only vendor key, DMA block count, access flags, and ATS flag. `struct ib_frmr_pool_ops` supplies provider callbacks `create_frmrs()`, `destroy_frmrs()`, and `build_key()`. Public functions are `ib_frmr_pools_init()`, `ib_frmr_pools_cleanup()`, `ib_frmr_pool_pop()`, and `ib_frmr_pool_push()`.

Control flow: an RDMA provider initializes pools on `ib_device` registration with pool ops, creates batches of FRMR handles for matching keys, hands an available handle to an `ib_mr` on pop, and returns it on push. Cleanup destroys remaining handles through provider ops.

State and persistence: pool state is associated with the `ib_device` and individual `ib_mr` objects at runtime. `kernel_vendor_key` distinguishes kernel-only pools from general pools. Nothing persists beyond device lifetime.

Dependencies and integration points: depends on `ib_device`, `ib_mr`, page sizing, provider MR allocation/destruction, and access flag conventions from verbs. It integrates memory registration acceleration with device-specific handle allocation.

Risks and test signals: risks include key mismatches causing MR reuse with wrong access or DMA geometry, pool leaks on device teardown, kernel-only pool exposure, ATS flag misinterpretation, and pop/push imbalance. Test provider init/cleanup, handle batch creation failure unwind, repeated MR allocation/free, access-flag variants, ATS on/off, and device removal with outstanding MRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/frmr_pools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib.h

Purpose: provides generic InfiniBand address and socket-address definitions plus a safety guard for legacy RDMA file APIs that use `write()` as a bidirectional ioctl-like channel.

Important APIs and types: `struct ib_addr` is a 16-byte address union with byte/word/dword/qword accessors and aliases for raw, subnet-prefix, and interface-id fields. Inline helpers test any-address and loopback, set 32-bit words, and compare addresses. `struct sockaddr_ib` defines AF_IB socket addresses with P_Key, flow info, `ib_addr`, service ID/mask, and scope ID. `ib_safe_file_access()` returns true only when the file credential matches the current credential.

Control flow: RDMA core or userspace-facing paths manipulate IB addresses using the inline helpers. Legacy file operations should call `ib_safe_file_access()` before accepting write-triggered commands to avoid privileged writes through inherited or redirected file descriptors.

State and persistence: no state is stored. All helpers operate on caller-supplied stack/heap structures or file credentials.

Dependencies and integration points: depends on Linux credentials, current task, file structures, uaccess/fs types, and endian/network helpers. It integrates AF_IB address handling with RDMA userspace and legacy char-device/file paths.

Risks and test signals: risks include endian mistakes in address comparisons/setup, incorrect loopback detection, misuse of AF_IB fields as IP addresses, and skipping credential checks on legacy write APIs. Test address helper unit cases, AF_IB socket bind/connect paths, credential mismatch cases for inherited file descriptors, and compat/user ABI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_addr.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_addr.h

Purpose: defines RDMA address-resolution data structures and helpers for translating IP/network-device addresses into RDMA link-layer, GID, P_Key, VLAN, multicast, and MTU information.

Important APIs and types: `struct rdma_dev_addr` stores source/destination/broadcast hardware addresses, device type, bound ifindex, transport, net namespace, selected SGID attribute, RDMA network type, and hop limit. Core APIs are `rdma_translate_ip()`, asynchronous `rdma_resolve_ip()`, `rdma_addr_cancel()`, and sockaddr size helpers. Inline helpers get/set IB P_Key and MGID from encoded broadcast data, compute GID offsets for InfiniBand vs Ethernet-like devices, map VLAN devices, convert IP to/from GIDs, get/set SGID/DGID, derive IBoE MTU, detect link-local and multicast addresses, derive link-local or multicast MACs, extract VLAN ID from a GID, and return real VLAN devices.

Control flow: callers initialize `rdma_dev_addr.net`, optionally provide a source address, and request synchronous translation or asynchronous resolution. Completion invokes the callback with resolved source address and device address or error; cancellation targets a pending resolution. Later connection setup uses the resolved GIDs, MACs, VLAN, P_Key, hoplimit, MTU, and selected SGID attribute.

State and persistence: `rdma_dev_addr` is caller-owned transient state that must remain valid until the resolution callback completes. `sgid_attr` is a referenced RDMA cache object whose lifetime rules come from the cache layer. No persistent state is stored here.

Dependencies and integration points: depends on Linux netdevice/VLAN/IP/IPv6/net namespace headers, `ib_verbs.h`, packet header sizes from `ib_pack.h`, GID attributes, and ARP hardware types. It connects RDMA CM/SA/QP setup to kernel networking address resolution for IB, RoCE, and iWARP transports.

Risks and test signals: risks include callback after caller storage is freed, net namespace or bound ifindex mismatch, incorrect GID offset for ARPHRD_INFINIBAND, VLAN ID sentinel confusion, MTU underflow after encapsulation overhead, multicast MAC derivation errors, and SGID attribute lifetime leaks. Test IPv4/IPv6/v4-mapped conversion, RoCE VLAN and non-VLAN devices, link-local address MAC generation, multicast joins, timeout/cancel races, netns isolation, and smallest-MTU edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_cache.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_cache.h

Purpose: declares cached accessors for RDMA device GID, P_Key, LMC, and port-state information. It hides provider queries behind software caches and reference-counted GID attributes.

Important APIs and types: GID APIs include `rdma_query_gid()`, `rdma_find_gid()`, `rdma_find_gid_by_port()`, `rdma_find_gid_by_filter()`, `rdma_get_gid_attr()`, `rdma_hold_gid_attr()`, `rdma_put_gid_attr()`, `rdma_query_gid_table()`, `rdma_read_gid_hw_context()`, `rdma_read_gid_l2_fields()`, `rdma_read_gid_attr_ndev_rcu()`, and `rdma_is_zero_gid()`. P_Key and port helpers include `ib_get_cached_pkey()`, `ib_find_cached_pkey()`, `ib_get_cached_lmc()`, and `ib_get_cached_port_state()`.

Control flow: cache users query by device/port/index or search by GID/type/netdevice. Returned `ib_gid_attr` objects must be held/put according to cache lifetime rules, and RCU-only netdevice access must occur under RCU protection. Consumers use cached P_Key/LMC/port state to initialize QPs, path records, CM messages, and address handles without synchronously querying hardware.

State and persistence: state lives in RDMA core per-device caches populated from hardware and netdev events. This header declares access, reference, and lookup functions; cache contents are runtime-only and update as ports/GIDs/netdevices change.

Dependencies and integration points: depends on `ib_verbs.h`, `ib_gid_attr`, userspace GID table entries, netdevice references, and provider cache maintenance. It integrates RDMA CM, SA, verbs, RoCE address selection, and user queries with the device cache.

Risks and test signals: risks include leaking or using after put of `ib_gid_attr`, RCU misuse for netdevices, stale GID/P_Key after netdev or port changes, wrong GID type selection for RoCE v1/v2, and index bounds errors. Test GID add/remove events, VLAN netdevice changes, P_Key table updates, port down/up transitions, userspace GID table queries, and refcount/RCU debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_cm.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_cm.h

Purpose: defines the InfiniBand Communication Manager client API, including connection states, event payloads, private-data limits, reject/status reasons, CM identifiers, and send/listen/notify operations for reliable connections and service ID resolution.

Important APIs and types: enums model CM states (`IDLE`, `LISTEN`, request/reply/MRA/established/disconnect/timewait/SIDR states), LAP states, event types, private-data sizes, rejection reasons, APR statuses, and SIDR statuses. Event parameter structs describe request, reply, reject, MRA, LAP/APR, SIDR request, and SIDR reply details, including paths, SGID attributes, P_Key/QP/QKey/PSN/resource depths, retry controls, and ECE data. `struct ib_cm_event` carries the event union and private data. `ib_cm_handler` is the callback contract. `struct ib_cm_id` stores handler/context/device/service IDs/state/local/remote IDs and remote CM QPN. APIs include `ib_create_cm_id()`, `ib_destroy_cm_id()`, `ib_cm_listen()`, `ib_cm_insert_listen()`, `ib_send_cm_req()`, `ib_send_cm_rep()`, `ib_send_cm_rtu()`, `ib_send_cm_dreq()`, `ib_send_cm_drep()`, `ib_cm_notify()`, `ib_send_cm_rej()`, `ib_prepare_cm_mra()`, `ib_cm_init_qp_attr()`, `ib_send_cm_sidr_req()`, `ib_send_cm_sidr_rep()`, and `ibcm_reject_msg()`.

Control flow: consumers allocate a CM ID, optionally listen on a service ID, or initiate a request using SA path records. Incoming request/SIDR listen events may allocate a new child CM ID delivered through the handler. Connection establishment progresses through REQ/REP/RTU and QP attribute initialization, can use MRA/REJ on duplicates or refusal, supports LAP/APR path migration, and tears down through DREQ/DREP and timewait. SIDR resolves service IDs without full connection setup. Callbacks may request CM ID destruction by returning nonzero but must not directly destroy the ID from callback context.

State and persistence: CM ID state is runtime in-memory protocol state tied to device and service/QP context. Private data is message-scoped. SGID/path references, retry timers, timewait state, and local/remote IDs are managed by the CM implementation, not persisted.

Dependencies and integration points: depends on MAD transport, Subnet Administration path records, RDMA CM ECE data, verbs QP attributes/events, GID attributes, and byte-order service ID constants. It is the protocol bridge between RDMA consumers, SA path lookup, MAD CM messages, and QP state transitions.

Risks and test signals: risks include illegal state transitions, destroying CM IDs in callbacks, private-data length overflows, SGID attribute lifetime mistakes, service ID mask conflicts, duplicate/timeout retry behavior, and QP attribute masks missing required fields. Test active/passive connection setup, listener child ID cleanup, rejection reasons, MRA duplicate handling, DREQ/DREP races, timewait exit, SIDR success/failure, LAP/APR path migration, ECE negotiation, and callback-return destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_hdrs.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_hdrs.h

Purpose: defines packed InfiniBand packet header layouts and inline accessors for LRH, GRH/BTH/DETH, RDMA extended headers, atomics, AETH/NAK, congestion bits, and TID RDMA extensions.

Important APIs and types: constants define BTH flags, opcode masks, NAK values, GRH fields, FECN/BECN bits, AETH credit/NAK fields, and packet masks. `struct ib_reth`, `struct ib_atomic_eth`, `union ib_ehdrs`, `struct ib_other_headers`, and `struct ib_header` model packed wire headers, with unaligned 64-bit fields handled by `ib_u64_get()`/`ib_u64_put()` and specific RETH/atomic accessors. LRH helpers return LNH, SC, SL, DLID, SLID, and link version. UD helpers get QKey/SQPN. BTH helpers return pad, P_Key, opcode, ack request, migration request, solicited event, PSN, QPN, FECN/BECN, transport version, and migration/solicited booleans.

Control flow: low-level drivers and packet-processing paths cast packet bytes to these packed structs, use endian/unaligned helpers to inspect headers, and branch on opcode, QPN, PSN, ACK/NAK, path migration, and congestion bits. TID RDMA subheaders are available through the extended header union.

State and persistence: no state is stored; the header exposes wire-format interpretation of caller-owned packet buffers.

Dependencies and integration points: depends on Linux unaligned access helpers, endian conversion, `ib_verbs.h`, and `tid_rdma_defs.h`. It integrates HCA drivers, software RDMA transports, and packet analyzers with InfiniBand wire headers.

Risks and test signals: risks include packed layout drift, unaligned 64-bit access bugs, endian conversion mistakes, duplicate macro definitions, QPN/PSN mask errors, and trusting malformed packet lengths before accessing extended headers. Test with compile-time layout/offset checks, packet encode/decode vectors, ACK/NAK and congestion packets, TID RDMA packets, sanitizers for unaligned access, and fuzzed short packets in receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_hdrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_mad.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_mad.h

Purpose: defines InfiniBand and OPA Management Datagram constants, wire headers, RMPP helpers, notice/class-port-info layouts, and the kernel MAD agent send/receive API.

Important APIs and types: constants cover management base/class versions, management classes, methods, statuses, RMPP flags/statuses, QP0/QP1/QKey, default P_Key values, notice types/producers, and MAD data sizes. Wire structs include `ib_mad_hdr`, `ib_rmpp_hdr`, packed `ib_sa_hdr`, `ib_mad`, `opa_mad`, `ib_rmpp_mad`, `opa_rmpp_mad`, packed `ib_sa_mad`, `ib_vendor_mad`, `ib_class_port_info`, `opa_class_port_info`, and `ib_mad_notice_attr`. Inline helpers get/set class-port-info response time/capmask2 and RMPP response time/flags. Agent-side structs and callbacks include `ib_mad_send_buf`, `ib_mad_agent`, `ib_mad_send_wc`, `ib_mad_recv_buf`, `ib_mad_recv_wc`, `ib_mad_reg_req`, `ib_mad_send_handler`, and `ib_mad_recv_handler`. APIs include `ib_response_mad()`, `ib_register_mad_agent()`, `ib_unregister_mad_agent()`, `ib_post_send_mad()`, `ib_free_recv_mad()`, `ib_modify_mad()`, `ib_cancel_mad()`, `ib_create_send_mad()`, `ib_is_mad_class_rmpp()`, `ib_get_mad_data_offset()`, `ib_get_rmpp_segment()`, `ib_free_send_mad()`, and `ib_mad_kernel_rmpp_agent()`.

Control flow: a client registers a MAD agent on a device port/QP with optional unsolicited receive method mask and RMPP support. It allocates a send buffer, fills common and class-specific headers/data, posts it, receives send completions through the send handler, and receives solicited or unsolicited MADs through the recv handler. RMPP transfers segment/reassemble long payloads; received buffers must be freed by the consumer and send buffers by the sender.

State and persistence: MAD agent registrations, TID high bits, security list membership, QP/MR references, outstanding sends, retries, timeouts, and RMPP segment chains are runtime state owned by the MAD layer. The header also defines on-wire state that must remain ABI-stable.

Dependencies and integration points: depends on verbs QPs/AHs/MRs/WCs, userspace MAD UAPI flags, list/bitmap infrastructure, SA component masks, OPA structures, and management classes. It is the common transport for SA, CM, SMI, PMA, vendor management, and userspace MAD access.

Risks and test signals: risks include packed wire layout mismatch, RMPP header/data length errors, send buffer lifetime races, missing `ib_free_recv_mad()`, method-mask registration gaps, timeout/retry corner cases, TID collisions, and OPA/IB size confusion. Test MAD agent register/unregister, QP0/QP1 sends, solicited response matching, unsolicited traps, RMPP multi-segment transfers, cancel/modify timeout paths, receive buffer free accounting, and wire-format layout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_mad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_marshall.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_marshall.h

Purpose: declares marshalling helpers that copy kernel RDMA objects into userspace ABI structures for uverbs and userspace SA consumers.

Important APIs and types: `ib_copy_qp_attr_to_user()` converts `struct ib_qp_attr` to `struct ib_uverbs_qp_attr`; `ib_copy_ah_attr_to_user()` converts `struct rdma_ah_attr` to `struct ib_uverbs_ah_attr`; `ib_copy_path_rec_to_user()` converts `struct sa_path_rec` to `struct ib_user_path_rec`.

Control flow: uverbs query paths and SA user responses call these helpers after obtaining kernel attributes, before copying ABI-formatted data to userspace. The helpers centralize transport-specific field mapping and byte-order/packing details.

State and persistence: no state is kept. Destination buffers are caller-owned and typically short-lived ABI responses.

Dependencies and integration points: depends on kernel verbs types, SA path records, and user ABI headers `ib_user_verbs.h` and `ib_user_sa.h`. It integrates RDMA core kernel state with stable userspace structure layouts.

Risks and test signals: risks include missing fields when kernel structs evolve, endian or width truncation, exposing uninitialized padding, and RoCE/OPA path fields not represented correctly in legacy user records. Test uverbs QP/AH query output, SA path query output, ABI padding initialization checks, cross-architecture 32/64-bit builds, and RoCE/IB/OPA conversion cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_marshall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_pack.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_pack.h

Purpose: declares generic bit-field packing/unpacking utilities and unpacked header structures for InfiniBand UD-style packet construction, including LRH, Ethernet/VLAN, GRH, IPv4/UDP, BTH, DETH, and immediate data.

Important APIs and types: byte-size constants define link, Ethernet/VLAN, GRH, IPv4, UDP, BTH, DETH, atomic/XRC, and ICRC header lengths. `struct ib_field` describes a mapping between C structure fields and bit positions in a packed buffer. Opcode enums define transport bases and concrete RC/UC/RD/UD opcodes through `IB_OPCODE()`, plus local/global LNH values. Unpacked structs model LRH, GRH, BTH, DETH, Ethernet, IPv4, UDP, VLAN, and aggregate `struct ib_ud_header` with presence flags. APIs are `ib_pack()`, `ib_unpack()`, `ib_ud_ip4_csum()`, `ib_ud_header_init()`, and `ib_ud_header_pack()`.

Control flow: callers initialize an `ib_ud_header` for the desired encapsulation and payload size, optionally compute IPv4 checksum fields, then pack the header into a wire buffer. Generic pack/unpack functions use descriptor arrays to move bitfields between native structs and network buffers.

State and persistence: no state is stored. Structures are caller-owned packet assembly/parse state.

Dependencies and integration points: depends on `ib_verbs.h`, Ethernet UAPI constants, GID types, and the RDMA packet transmit path. It integrates software header construction with drivers and transports that need to build UD, RoCE, or encapsulated packets.

Risks and test signals: risks include descriptor offset mistakes, opcode constant drift, bitfield truncation, checksum mismatch, payload length errors, and inconsistent presence flags causing malformed packets. Test pack/unpack round trips, known IB/RoCE header byte vectors, IPv4 checksum vectors, each encapsulation combination, immediate-data cases, and boundary payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_pack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_pma.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_pma.h

Purpose: defines Performance Management Agent MAD attribute IDs, capability bits, wire structures, and counter-select masks for InfiniBand port sampling and port counter queries.

Important APIs and types: capability flags include all-port select, extended width variants, and transmit wait support. Attribute IDs cover class port info, port samples control/result/result-ext, port counters, and extended port counters. `struct ib_pma_mad` provides a PMA MAD wrapper. Sampling structs model control, 32-bit result, and 64-bit extended result records. `struct ib_pma_portcounters` and `struct ib_pma_portcounters_ext` represent standard and extended port counters, with select masks for symbol/link/receive/transmit/discard/constraint/VL15 and 64-bit data/packet/unicast/multicast counters.

Control flow: PMA clients or agents form MADs with these attribute IDs and structs, select counters through masks, and read or update counter records through the MAD subsystem. Extended counters are used when capability bits indicate support.

State and persistence: no local state is stored. The structures mirror hardware-maintained port counters and sampling controls; hardware owns counter persistence until reset/clear per device behavior.

Dependencies and integration points: depends on `ib_mad.h` for MAD headers and byte-order constants. It integrates performance query tooling, subnet management, and provider PMA implementations.

Risks and test signals: risks include packed layout mismatch, counter-select masks not matching struct fields, 32-bit counter wrap handling, extended capability misdetection, and endian mistakes in MAD payloads. Test PMA MAD encode/decode, standard vs extended counter queries, sampling control/result paths, counter wrap behavior, and devices with/without extended-width capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_pma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_sa.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_sa.h

Purpose: defines the kernel Subnet Administration client API, SA record structures, component masks, path conversions for IB/RoCE/OPA, service and multicast records, async query APIs, multicast join/free, and address-handle initialization helpers.

Important APIs and types: constants define SA class versions, methods, attribute IDs, selectors, multicast join states, component masks for path, multicast, service, and GUID info records. `struct sa_path_rec` stores common path fields plus IB, RoCE, or OPA-specific union data and `rec_type`; helpers convert GID type to path record type, convert IB/OPA paths, identify RoCE/OPA paths, get/set SLID/DLID/raw traffic, and set/get RoCE destination MAC. Other records include `sa_service_rec`, `ib_sa_mcmember_rec`, and `ib_sa_guidinfo_rec`. `struct ib_sa_client` tracks users with atomic and completion. APIs include client register/unregister, `ib_sa_cancel_query()`, path/service/GUID info queries, multicast join/free/get-member, AH initialization from multicast or path records, and pack/unpack helpers for path and service records.

Control flow: a consumer registers an SA client, issues asynchronous queries with component masks and callbacks, optionally cancels by query ID, and unregisters after outstanding users drain. Multicast joins allocate an `ib_sa_multicast` tracker and complete through callback; the tracker must be freed outside the callback unless callback returns nonzero. Path records are packed into MAD wire attributes or unpacked from responses, then used to initialize AH/QP/CM state.

State and persistence: `ib_sa_client` and `ib_sa_multicast` are runtime tracking objects. Query results and path/service records are transient copies of subnet manager data. Multicast membership state exists in the subnet manager/fabric and in the kernel tracker for the join lifetime.

Dependencies and integration points: depends on completions, atomics, netdevice, `ib_verbs.h`, MAD, RDMA address helpers, OPA address helpers, GID types, and SA component masks. It feeds RDMA CM, multicast users, address handles, path resolution, and userspace SA marshalling.

Risks and test signals: risks include component-mask mismatch with populated fields, callback lifetime mistakes, freeing multicast from callback, OPA/IB LID conversion errors, RoCE DMAC not set or stale, query cancellation races, and AH attributes missing SGID/netdevice context. Test path queries for IB/RoCE/OPA, service record query/pack/unpack, multicast join failure and fatal reset handling, cancellation before response, client unregister with live queries, AH initialization from path and multicast, and conversion helpers for multicast/OPA GIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_sa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_smi.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_smi.h

Purpose: defines Subnet Management Packet structures, subnet-management attribute IDs, port/node info layouts, notice trap numbers, and helper initialization for basic query SMPs.

Important APIs and types: `struct ib_smp` is the packed SMP wire layout with common fields, hop pointer/count, M_Key, directed-route LIDs, data, initial path, and return path. Attribute constants cover notice, node description/info, switch info, GUID/port/P_Key/SL2VL/VL arbitration/forwarding tables, SM info, vendor diagnostics, LED info, and vendor mask. `struct ib_port_info`, `struct ib_node_info`, and `struct ib_vl_weight_elem` mirror management payloads. `ib_get_smp_direction()` checks the directed-route direction bit. Trap constants define link/local/error/capability/system GUID/bad key notices, and `ib_init_query_mad()` initializes a GET subnet LID-routed query.

Control flow: subnet management users allocate/fill `ib_smp`, initialize common query fields, set attr IDs/modifiers and paths, send through MAD QP0, and interpret returned management payloads. Directed-route responses use the status direction bit and path arrays.

State and persistence: no state is stored. SMP structs are transient wire buffers, while actual subnet state lives in switches, HCAs, and subnet managers.

Dependencies and integration points: depends on `ib_mad.h` for management constants and integrates with SMI agents, subnet managers, fabric discovery, port info reading, and trap handling.

Risks and test signals: risks include packed SMP layout mismatch, path hop overflow, M_Key handling mistakes, wrong endian attr IDs, direction-bit misuse, and stale port/node info field interpretation. Test SMP GET for node/port info, directed-route query/response paths, trap decode, max-hop boundary, M_Key-protected queries, and layout checks against IBTA wire sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_sysfs.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_sysfs.h

Purpose: defines a typed sysfs attribute wrapper for RDMA device port attributes and helper macros to declare read/write/admin/read-only/write-only attributes.

Important APIs and types: `struct ib_port_attribute` embeds `struct attribute` and provides port-aware `show()` and `store()` callbacks receiving `ib_device`, port number, the attribute object, and buffer/count. Macros `IB_PORT_ATTR_RW`, `IB_PORT_ATTR_ADMIN_RW`, `IB_PORT_ATTR_RO`, and `IB_PORT_ATTR_WO` declare attributes with appropriate mode. `ib_port_sysfs_get_ibdev_kobj()` maps a sysfs kobject back to `ib_device` and port number.

Control flow: RDMA core or drivers declare port attributes, sysfs invokes generic wrappers that recover the device/port from kobject, and then dispatch to the port-aware callbacks. Admin attributes restrict mode to owner read/write.

State and persistence: no persistent state is owned here. Sysfs files expose live RDMA device/port state or accept live configuration writes implemented by callbacks.

Dependencies and integration points: depends on Linux sysfs/kobject infrastructure and `struct ib_device`. It integrates RDMA port objects with the device model and sysfs user interfaces.

Risks and test signals: risks include kobject-to-port lookup lifetime races, overly permissive attribute mode, callback buffer length mistakes, and accessing removed devices. Test sysfs read/write for each port, admin mode permissions, device removal while sysfs file is open, invalid kobject lookup, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_ucaps.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_ucaps.h

Purpose: declares RDMA userspace capability file-descriptor support. It lets user access code create, remove, collect, and test capability tokens such as mlx5 local or other-VHCA control.

Important APIs and types: `enum rdma_user_cap` currently defines `RDMA_UCAP_MLX5_CTRL_LOCAL`, `RDMA_UCAP_MLX5_CTRL_OTHER_VHCA`, and `RDMA_UCAP_MAX`. `UCAP_ENABLED()` tests a bitmask for a capability. APIs include global `ib_cleanup_ucaps()`, `ib_get_ucaps()` to derive an index mask from file descriptors, and config-gated `ib_create_ucap()`/`ib_remove_ucap()`. When `CONFIG_INFINIBAND_USER_ACCESS` is disabled, create/remove are no-op stubs returning `-EOPNOTSUPP` or doing nothing.

Control flow: user-access-enabled code creates capability FDs for a requested type, passes FDs back into RDMA ioctls or setup paths, and `ib_get_ucaps()` validates/collects them into an index mask. Cleanup removes global capability resources during subsystem teardown.

State and persistence: capability state is runtime kernel object/file state. The bitmask represents active validated capabilities for a call; it is not persisted.

Dependencies and integration points: depends on RDMA user-access config, Linux FD/file lifetime rules, and provider-specific policy such as mlx5 control scopes. It integrates privileged or delegated RDMA control flows with uverbs-like userspace entry points.

Risks and test signals: risks include capability bit shifts exceeding mask width, accepting stale/wrong FDs, missing cleanup of capability objects, config-stub behavior surprising callers, and confused local vs other-VHCA authority. Test capability FD create/remove, `ib_get_ucaps()` with valid/invalid/duplicate FDs, config-disabled builds, mask testing with `UCAP_ENABLED()`, and permission checks in provider callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_ucaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_umem.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_umem.h

Purpose: defines RDMA user-memory registration objects and helpers for pinned user pages and dma-buf-backed memory, with config-gated APIs for acquiring, releasing, mapping, copying, page-size selection, and revocation.

Important APIs and types: `struct ib_umem` stores owning RDMA device, owning mm, IOVA, length, virtual address, DMA attrs, writable/ODP/dmabuf flags, and an appended scatter-gather table. `struct ib_umem_dmabuf` embeds `ib_umem` and tracks dma-buf attachment, sg table bounds/offset trim, revoke callback/private data, and pinned/revoked state. Inline helpers convert to dmabuf, compute page offset, first DMA address, DMA offset for a page size, number of DMA blocks/pages, best page size from offset bitmask, and contiguity. With `CONFIG_INFINIBAND_USER_MEM`, APIs include `ib_umem_get()`, `ib_umem_release()`, `ib_umem_copy_from()`, `ib_umem_find_best_pgsz()`, dma-buf get/pinned/revocable variants, map/unmap pages, release, revoke lock/unlock, and revoke. Without the config, stubs return `-EOPNOTSUPP`/0 or do nothing.

Control flow: uverbs/provider code pins or attaches user memory, builds DMA mappings in the SG table, selects hardware page size based on supported page-size bitmap and alignment, programs memory regions, and releases/unmaps on MR destruction. Dma-buf users may map lazily, pin, install revoke callbacks under revoke lock, and handle revocation by provider-specific teardown.

State and persistence: `ib_umem` is runtime registration state tying an mm/dma-buf to DMA mappings and an IOVA range. Pinned/revoked bits and SG tables are valid only while the registration exists. No file data is persisted by this layer.

Dependencies and integration points: depends on scatterlist/SG append tables, DMA mapping, pages, mm lifetime, dma-buf attachment APIs, RDMA device/provider MR setup, and config flags. It integrates uverbs memory registration, dma-buf sharing, and hardware page-size programming.

Risks and test signals: risks include page pin leaks, DMA unmap omissions, wrong IOVA/page-size math, overflow in block-count calculations, contiguity false positives, copying past umem bounds, dma-buf revoke races, config-stub signature drift, and writable flag mismatches. Test MR register/deregister under memory pressure, page-size selection matrices, offset/alignment edge cases, contiguous and fragmented SG tables, dma-buf pin/map/revoke/release, config-disabled builds, and lockdep around revoke locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_umem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_umem_odp.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_umem_odp.h

Purpose: defines On-Demand Paging user-memory registration objects for RDMA and config-gated APIs to allocate, map DMA pages under page fault, unmap, and release ODP memory ranges.

Important APIs and types: `struct ib_umem_odp` embeds `ib_umem`, an `mmu_interval_notifier`, owning thread-group PID, `hmm_dma_map`, `umem_mutex`, provider-private pointer, page count, implicit-ODP flag, and page shift. Inline helpers convert from `ib_umem`, return start/end addresses from the notifier interval, and compute page count. With `CONFIG_INFINIBAND_ON_DEMAND_PAGING`, APIs include `ib_umem_odp_get()`, `ib_umem_odp_alloc_implicit()`, `ib_umem_odp_alloc_child()`, `ib_umem_odp_release()`, `ib_umem_odp_map_dma_and_lock()`, and `ib_umem_odp_unmap_dma_pages()`. Without the config, get returns `-EINVAL` and release is a no-op.

Control flow: providers create explicit or implicit ODP umems, register MMU interval notification over the range, and map DMA pages on demand during faults or access. Mapping/unmapping is serialized by `umem_mutex` and coordinates with HMM DMA maps and invalidation counters. Child umems can represent subranges of an implicit root.

State and persistence: ODP state is runtime memory-registration state coupled to an mm interval and DMA mappings. Implicit ODP objects have zero length and serve as anchors. The page map can be invalidated by MMU notifications and is not persistent.

Dependencies and integration points: depends on `ib_umem.h`, verbs access flags, HMM DMA mapping, MMU interval notifier APIs, PID lifetime, mutexes, and provider page-fault handlers. It integrates RDMA memory registration with Linux MM invalidation and hardware page-fault support.

Risks and test signals: risks include notifier lifetime bugs, mapping while invalidation is active, missing mutex coverage, incorrect start/end/page_shift math, implicit ODP misuse as DMA-mappable memory, stale DMA mappings after unmap, and config-disabled behavior mismatches. Test ODP MR creation/release, page fault map/unmap, mmu_notifier invalidation during DMA, implicit and child ODP flows, access-mask enforcement, process exit while ODP exists, and config matrices with ODP disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_umem_odp.h -->
