<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rmap.h -->
# sources/distributed-fs/ceph-client/include/linux/rmap.h

## Purpose
`rmap.h` declares the kernel reverse-mapping interfaces used by memory-management code to find and manipulate every VMA/PTE mapping a folio has. It covers anonymous VMA ancestry, folio mapcount accounting, COW/exclusive-anon transitions, page-table mapped-walk state, migration/unmap/mkclean operations, and rmap walker callbacks.

## Important APIs, types, and functions
Core types are `struct anon_vma`, `struct anon_vma_chain`, `enum ttu_flags`, `rmap_t`, `struct page_vma_mapped_walk`, and `struct rmap_walk_control`. Important APIs include `folio_add_anon_rmap_ptes()`, `folio_add_anon_rmap_pmd()`, `folio_add_new_anon_rmap()`, `folio_add_file_rmap_ptes()`, `folio_add_file_rmap_pmd()`, `folio_remove_rmap_ptes()`, `folio_remove_rmap_pmd()`, hugetlb rmap helpers, `folio_try_dup_anon_rmap_ptes()`, `folio_try_share_anon_rmap_pte()`, `folio_referenced()`, `try_to_unmap()`, `try_to_migrate()`, `page_vma_mapped_walk()`, `folio_mkclean()`, `remove_migration_ptes()`, `rmap_walk()`, and `folio_lock_anon_vma_read()`.

## Control flow, state, and persistence
Anonymous pages point to `anon_vma` rather than directly to VMAs, and `anon_vma_chain` links each VMA to related anon-vmas through both VMA lists and anon-vma interval trees. Mapping add/remove helpers adjust per-page, large-folio, entire-map, and optional per-MM mapcounts while sanity checks reject zeropage, hugetlb misuse, wrong page ranges, and stale anon-vma references. COW duplication may return `-EBUSY` when a possibly DMA-pinned exclusive anon folio cannot be safely shared. Mapped-walk callers initialize `page_vma_mapped_walk`, iterate PTE/PMD locations, then release PTE mappings and PTLs with `page_vma_mapped_walk_done()` or restart after page-table changes.

## Dependencies and integration points
The header depends on `mm.h`, `rwsem.h`, memcg, highmem, pagemap, memremap, bit spinlocks, folio/page helpers, THP/hugetlb configuration, optional `CONFIG_MM_ID`, GUP-fast barriers, and page-table lock discipline. It is used by fork, COW fault handling, KSM, reclaim, migration, compaction, writeback cleaning, hwpoison, and device-private/exclusive-page flows.

## Risks and test signals
Risks include mapcount underflow/overflow, clearing `PageAnonExclusive` while GUP-fast or DMA pins can still observe writability, missing final TLB flushes for batched unmap, anon-vma lifetime races, wrong `TTU_*` flag combinations, and leaked PTLs/PTE mappings when mapped walks abort. Test signals include fork/COW stress with pinned pages, THP split/migration, KSM sharing, reclaim reference sampling, `folio_mkclean()` writeback tests, hugetlb COW, memory hotplug/device-private migration, and debug-VM mapcount warnings staying silent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rmi.h -->
# sources/distributed-fs/ceph-client/include/linux/rmi.h

## Purpose
`rmi.h` is the public interface for Synaptics RMI4 touch/input devices. It describes platform data, function descriptors, transport devices, transport operations, RMI drivers, device-private runtime state, and suspend/resume/attention entry points.

## Important APIs, types, and functions
Key data structures include `struct rmi_2d_axis_alignment`, `enum rmi_sensor_type`, `struct rmi_2d_sensor_platform_data`, `struct rmi_gpio_data`, `enum rmi_reg_state`, `struct rmi_f01_power_management`, `struct rmi_device_platform_data_spi`, `struct rmi_device_platform_data`, `struct rmi_function_descriptor`, `struct rmi_transport_dev`, `struct rmi_transport_ops`, `struct rmi_driver`, `struct rmi_device`, `struct rmi4_attn_data`, and `struct rmi_driver_data`. Public functions are `rmi_register_transport_device()`, `rmi_unregister_transport_device()`, `rmi_set_attn_data()`, `rmi_driver_suspend()`, and `rmi_driver_resume()`.

## Control flow, state, and persistence
Transport drivers allocate an `rmi_transport_dev`, fill bus-specific read/write/reset operations, platform data, and a parent device, then register it with the RMI core. Function discovery uses `struct rmi_function_descriptor` page/offset fields to bind function drivers. Attention data and IRQ state are carried through `rmi4_attn_data` and `rmi_driver_data` FIFOs/lists. Runtime state persists in the device model, function lists, interrupt masks, wakeup settings, and platform-configured sensor overrides until unregister or suspend/resume changes them.

## Dependencies and integration points
The header integrates Linux device core, input subsystem, interrupts, kfifo, lists, modules, and bus transports such as I2C/SPI/HID. Platform data feeds F01 power management, F11 2D absolute/relative reporting, F30/F3A GPIO/button reporting, reset GPIO handling, firmware reset delays, and optional SPI chip-select timing callbacks.

## Risks and test signals
Risks include incorrect axis swap/flip/clipping, invalid firmware quirk overrides, missing interrupt masks, transport read/write block-size mismatches, custom SPI chip-select timing errors, and stale attention data across suspend/resume. Test signals include probe/discovery on RMI4 touchpads and touchscreens, F11 coordinate transformation tests, GPIO/button quirk coverage, suspend wake behavior, IRQ FIFO draining, reset sequencing, and transport error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rndis.h -->
# sources/distributed-fs/ceph-client/include/linux/rndis.h

## Purpose
`rndis.h` defines Remote NDIS protocol constants for USB/network gadget and host code. It covers message IDs, completion IDs, status values, packet flags, medium and hardware status values, packet filters, miniport/MAC options, many NDIS OIDs, power-management OIDs, and connection-oriented RNDIS messages.

## Important APIs, types, and functions
This header exports macros only. Important macro families are `REMOTE_NDIS_*_MSG`, `REMOTE_NDIS_*_CMPLT`, `RNDIS_STATUS_*`, `RNDIS_DF_*`, `RNDIS_MEDIUM_*`, `RNDIS_PACKET_TYPE_*`, `RNDIS_MINIPORT_*`, `RNDIS_MAC_OPTION_*`, `RNDIS_OID_GEN_*`, `RNDIS_OID_802_3_*`, `RNDIS_OID_802_11_*`, `RNDIS_OID_PNP_*`, and `REMOTE_CONDIS_*`. It does not define runtime structures or functions.

## Control flow, state, and persistence
RNDIS control flow is external to this header: USB control/bulk handlers decode `REMOTE_NDIS_INITIALIZE_MSG`, query/set OIDs, reset/halt, and packet messages using these numeric tags, then respond with matching completion/status values. State such as initialized media status, packet filters, multicast lists, power state, and statistics lives in the RNDIS device or host driver, not here.

## Dependencies and integration points
The header is self-contained and acts as the ABI vocabulary between Linux RNDIS implementations and Microsoft-compatible peers. It integrates with USB gadget Ethernet, USB RNDIS host support, NDIS OID emulation, link state notification, wake-on-LAN/power management, and 802.3/802.11 query paths.

## Risks and test signals
Risks include using a wrong completion code for a request, accepting unsupported OIDs without length validation, 32-bit little-endian protocol assumptions in users, exposing stale link/statistics values, and security-sensitive parsing of host-supplied control buffers. Test signals include enumeration with Windows/Linux RNDIS peers, OID query/set conformance, packet-filter transitions, reset/halt handling, malformed control-message fuzzing, and link/power-management notification tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rndis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rodata_test.h -->
# sources/distributed-fs/ceph-client/include/linux/rodata_test.h

## Purpose
`rodata_test.h` declares the read-only data protection self-test hook.

## Important APIs, types, and functions
The only public API is `rodata_test()`, declared when `CONFIG_STRICT_KERNEL_RWX` is enabled and stubbed to an empty inline otherwise.

## Control flow, state, and persistence
The enabled implementation is called by architecture or init code to verify that kernel rodata mappings are not writable after permissions are finalized. The disabled configuration compiles callers away with no runtime state. No persistent data is stored in this header.

## Dependencies and integration points
It depends on the `CONFIG_STRICT_KERNEL_RWX` memory-protection option and integrates with architecture page-permission setup and boot-time kernel self-protection checks.

## Risks and test signals
Risks are mostly coverage risks: a disabled config silently omits the test, and enabled tests must run after final page permissions are applied. Test signals include boot logs from strict RWX kernels, failed write attempts to rodata, and architecture builds with both enabled and disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rodata_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rolling_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/rolling_buffer.h

## Purpose
`rolling_buffer.h` declares a folio-queue backed rolling buffer used to stream folios from a producer to a consumer while tracking the live window with an `iov_iter`.

## Important APIs, types, and functions
The main type is `struct rolling_buffer`, with producer `head`, consumer `tail`, `iter`, `next_head_slot`, and `first_tail_slot`. `struct rolling_buffer_snapshot` records the current queue segment, slot, and folio order for read snapshots. Mark bits are `ROLLBUF_MARK_1` and `ROLLBUF_MARK_2`. APIs include `rolling_buffer_init()`, `rolling_buffer_make_space()`, `rolling_buffer_load_from_ra()`, `rolling_buffer_append()`, `rolling_buffer_delete_spent()`, `rolling_buffer_clear()`, and inline `rolling_buffer_advance()`.

## Control flow, state, and persistence
The buffer is never allowed to become empty: at least one `folio_queue` segment remains so producer and consumer do not both have to mutate both queue pointers. Producers append folios or load them from readahead into head slots, extending the iterator; consumers advance `iter`, delete spent queue segments from the tail, or snapshot the current read position. State is in-memory queue/iterator state and persists only while the owner keeps the rolling buffer live.

## Dependencies and integration points
It depends on `linux/folio_queue.h`, `linux/uio.h`, folio batches, and readahead control. It integrates with file/network/cache paths that want folio-granular producer/consumer buffering without copying data into a linear buffer.

## Risks and test signals
Risks include violating the non-empty invariant, slot index wrap mistakes, deleting a queue segment still referenced by a snapshot or iterator, mismatched folio marks, and producer/consumer races outside the intended one-thread-per-end model. Test signals include init/clear, append across queue segment boundaries, readahead loading, iterator advancement, deleting spent folios, snapshot reads, and concurrent producer/consumer stress under KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rolling_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/root_dev.h -->
# sources/distributed-fs/ceph-client/include/linux/root_dev.h

## Purpose
`root_dev.h` exposes the kernel's selected root block device identifier.

## Important APIs, types, and functions
The header declares the global `ROOT_DEV` device number used by boot and mount code to locate the initial root filesystem device.

## Control flow, state, and persistence
Boot parsing and early block-device discovery assign `ROOT_DEV`; root-mount code consumes it when mounting the real root. The value persists as global kernel state for the booted system but the header itself has no logic.

## Dependencies and integration points
It depends on `dev_t` from kernel types and integrates with init/do_mounts code, root= command-line parsing, initramfs/rootfs handoff, and block-device naming.

## Risks and test signals
Risks include stale or unset `ROOT_DEV`, mismatched major/minor numbers after device discovery races, and confusion between initramfs root and real root. Test signals are boot tests with root by device number, UUID/PARTUUID, NFS/initramfs configurations, and failure-path diagnostics for missing root devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/root_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmb.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmb.h

## Purpose
`rpmb.h` defines the kernel interface for Replay Protected Memory Block devices backed by eMMC, UFS, or NVMe storage.

## Important APIs, types, and functions
Key types are `enum rpmb_type`, `struct rpmb_descr`, `struct rpmb_dev`, and wire-format `struct rpmb_frame`. Request constants include `RPMB_PROGRAM_KEY`, `RPMB_GET_WRITE_COUNTER`, `RPMB_WRITE_DATA`, `RPMB_READ_DATA`, and `RPMB_RESULT_READ`. Enabled APIs include `rpmb_dev_get()`, `rpmb_dev_put()`, `rpmb_dev_find_device()`, `rpmb_interface_register()`, `rpmb_interface_unregister()`, `rpmb_dev_register()`, `rpmb_dev_unregister()`, and `rpmb_route_frames()`; disabled builds return `NULL` or `-EOPNOTSUPP`.

## Control flow, state, and persistence
Storage drivers provide `struct rpmb_descr`, including device ID, capacity, reliable write count, and a `route_frames()` callback, then register an `rpmb_dev`. Consumers find/get the device, construct one or more 512-byte `rpmb_frame` requests, and route frames through the provider. Persistent state is hardware-backed: authentication key programming, write counters, and RPMB data survive reboots; kernel state is the registered device and class-interface list.

## Dependencies and integration points
It depends on the device model, list handling, big-endian integer types, and storage-specific block transports. It integrates with trusted execution environments, key derivation using `dev_id`, eMMC/UFS/NVMe RPMB providers, and class-interface notification.

## Risks and test signals
Risks include programming an irreversible authentication key, wrong frame endianness, mismatched request/response frame counts, stale write counters, unreliable writes exceeding `reliable_wr_count`, and exposing unauthenticated data paths. Test signals include register/unregister lifetime tests, frame routing for all request types, MAC/counter validation with a known device or emulator, disabled-config stubs, and error injection in transport callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmsg.h

## Purpose
`rpmsg.h` is the main Remote Processor Messaging bus API. It lets drivers bind to rpmsg channels, create endpoints, send messages, receive callbacks, poll endpoints, and apply transport flow control.

## Important APIs, types, and functions
Core types include `struct rpmsg_channel_info`, `struct rpmsg_device`, `struct rpmsg_endpoint`, `struct rpmsg_driver`, `rpmsg_rx_cb_t`, and `rpmsg_flowcontrol_cb_t`. Important helpers are `rpmsg16_to_cpu()`, `cpu_to_rpmsg16()`, `rpmsg32_to_cpu()`, `cpu_to_rpmsg32()`, `rpmsg64_to_cpu()`, and `cpu_to_rpmsg64()`. Enabled APIs include `rpmsg_register_device_override()`, `rpmsg_register_device()`, `rpmsg_unregister_device()`, `__register_rpmsg_driver()`, `unregister_rpmsg_driver()`, `rpmsg_create_ept()`, `rpmsg_destroy_ept()`, `rpmsg_send()`, `rpmsg_sendto()`, `rpmsg_trysend()`, `rpmsg_trysendto()`, `rpmsg_poll()`, `rpmsg_get_mtu()`, and `rpmsg_set_flow_control()`.

## Control flow, state, and persistence
Transports instantiate `rpmsg_device` objects with source/destination addresses and endian mode. Drivers register an `rpmsg_driver`; bus matching invokes `probe`, binds the channel endpoint, and calls the driver's receive callback for inbound messages matching the endpoint address. Explicit endpoints carry a callback, private pointer, reference count, callback mutex, local address, and endpoint ops. Disabled builds warn and return `-ENXIO`/`NULL`. State persists as device model objects and endpoint references while the remote processor/channel is alive.

## Dependencies and integration points
The header integrates with device core, module device tables, krefs, mutexes, poll, UAPI rpmsg definitions, byteorder wrappers, remoteproc/virtio transports, userspace rpmsg character devices, and vendor transports such as Qualcomm GLINK/SMD and MediaTek rpmsg.

## Risks and test signals
Risks include endpoint use-after-destroy, callback changes without holding `cb_lock`, MTU overrun, blocking send in atomic context, endian mismatches, stale driver overrides, and flow-control deadlocks. Test signals include driver registration/matching, endpoint create/destroy refcounting, inbound callback dispatch, send/trysend behavior under full vrings, poll readiness, MTU bounds, flow-control pause/resume, and disabled-config stub coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/byteorder.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmsg/byteorder.h

## Purpose
`rpmsg/byteorder.h` provides typed endian conversion helpers for rpmsg protocol fields.

## Important APIs, types, and functions
The header defines rpmsg-specific bitwise types `__rpmsg16`, `__rpmsg32`, and `__rpmsg64`, plus `rpmsg_is_little_endian()`, `__rpmsg16_to_cpu()`, `__cpu_to_rpmsg16()`, `__rpmsg32_to_cpu()`, `__cpu_to_rpmsg32()`, `__rpmsg64_to_cpu()`, and `__cpu_to_rpmsg64()`.

## Control flow, state, and persistence
There is no persistent state. Conversion helpers select little-endian or big-endian conversion based on the transport's endian flag; `rpmsg_is_little_endian()` reflects the default kernel-side rpmsg byte order.

## Dependencies and integration points
It depends on Linux endian annotations and byteorder helpers. `rpmsg.h` wraps these primitives with device-aware helpers using `rpdev->little_endian`, and vendor name-service/message headers use the typed fields for wire formats.

## Risks and test signals
Risks include bypassing the typed helpers, mixing CPU-endian integers with `__rpmsg*` fields, and assuming all transports are little-endian. Test signals are sparse/endian annotation coverage, loopback tests on little- and big-endian transports, and decoding name-service or vendor messages with known byte sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/mtk_rpmsg.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmsg/mtk_rpmsg.h

## Purpose
`mtk_rpmsg.h` exposes MediaTek rpmsg helper APIs for creating a remoteproc subdevice backed by MediaTek IPI operations.

## Important APIs, types, and functions
The header defines `ipi_handler_t` and `struct mtk_rpmsg_info`, whose callbacks are `register_ipi()`, `unregister_ipi()`, and `send_ipi()`, plus `ns_ipi_id` for name-service support. Public APIs are `mtk_rpmsg_create_rproc_subdev()` and `mtk_rpmsg_destroy_rproc_subdev()`.

## Control flow, state, and persistence
MediaTek platform code supplies IPI callbacks, creates an `rproc_subdev`, and remoteproc start/stop paths use that subdevice to register IPI handlers, send rpmsg payloads by IPI ID, and optionally process name-service announcements. State lives in the remoteproc subdevice, platform device, and transport implementation, not in the header.

## Dependencies and integration points
It depends on `platform_device.h` and `remoteproc.h`. It integrates the rpmsg core with MediaTek SCP/remoteproc IPI transports and service discovery through a configured name-service IPI.

## Risks and test signals
Risks include IPI ID collisions, registering handlers before firmware is ready, failing to unregister handlers on remoteproc stop, send timeout misuse, and missing name-service support when `ns_ipi_id` is `-1`. Test signals include MediaTek remoteproc boot/stop, IPI registration/unregistration, send timeout paths, rpmsg channel discovery, remote crash recovery, and subdevice destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/mtk_rpmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/ns.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmsg/ns.h

## Purpose
`rpmsg/ns.h` defines the rpmsg name-service announcement payload used by transports to create or remove rpmsg channels dynamically.

## Important APIs, types, and functions
The central type is `struct rpmsg_ns_msg`, carrying a fixed-size service name, source address, and flags. Name-service flags identify channel creation and destruction announcements, using rpmsg-endian integer fields.

## Control flow, state, and persistence
A remote processor sends a name-service message; the transport decodes it, registers or unregisters an `rpmsg_device`, and the rpmsg bus matches drivers. No local persistent state is stored here, but name-service messages drive persistent device-model channel state until a destroy announcement or transport reset.

## Dependencies and integration points
It depends on rpmsg byteorder types and UAPI name-size constants. It integrates with virtio-rpmsg and other transports that support dynamic service discovery.

## Risks and test signals
Risks include unterminated or oversized names, endian errors in source address/flags, duplicate create messages, missing destroy cleanup, and trusting malformed remote firmware. Test signals include create/destroy announcement parsing, duplicate and malformed NS messages, driver autoload/matching, and transport reset cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_glink.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_glink.h

## Purpose
`qcom_glink.h` declares Qualcomm GLINK SMEM registration and subsystem-restart notification helpers.

## Important APIs, types, and functions
The header forward-declares `struct qcom_glink_smem`. Public helpers are `qcom_glink_ssr_notify()`, `qcom_glink_smem_register()`, and `qcom_glink_smem_unregister()`, with no-op or `NULL` stubs when the relevant GLINK/SMEM configs are disabled.

## Control flow, state, and persistence
Qualcomm platform code registers a GLINK SMEM transport using a parent device and device-tree node, after which GLINK channels can appear as rpmsg devices. Subsystem restart paths call `qcom_glink_ssr_notify()` with an SSR name so GLINK users can react to remote resets. Persistent state is held by the GLINK SMEM transport and device model.

## Dependencies and integration points
It depends on `struct device`, `struct device_node`, `CONFIG_RPMSG_QCOM_GLINK`, and `CONFIG_RPMSG_QCOM_GLINK_SMEM`. Integration points include qcom remoteproc, SMEM-backed GLINK transport, subsystem restart, and rpmsg client drivers.

## Risks and test signals
Risks include edge registration before link readiness, stale channel devices after subsystem restart, disabled-config stubs returning no edge, and teardown races with active endpoints. Test signals include qcom remoteproc boot/shutdown, channel enumeration, endpoint traffic, SSR/restart cleanup, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_glink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_smd.h -->
# sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_smd.h

## Purpose
`qcom_smd.h` declares the Qualcomm Shared Memory Driver rpmsg edge interface.

## Important APIs, types, and functions
The header forward-declares `struct qcom_smd_edge` and exposes `qcom_smd_register_edge()` and `qcom_smd_unregister_edge()` when `CONFIG_RPMSG_QCOM_SMD` is enabled, with stubbed fallbacks otherwise.

## Control flow, state, and persistence
Qualcomm SMD transport probe registers an SMD edge, which lets rpmsg clients bind to SMD channels. Unregistration removes the edge and associated channel devices. Runtime state persists in SMD edge/channel objects owned by the transport.

## Dependencies and integration points
It depends on the device model and Qualcomm SMD rpmsg support. Integration points include legacy Qualcomm remote processors, shared-memory channel discovery, subsystem restart, and rpmsg client drivers.

## Risks and test signals
Risks include channel teardown while clients still hold endpoints, missing cleanup on remote crash, and disabled-config callers not checking returned pointers. Test signals include SMD channel discovery, client probe/remove, message loopback, remote restart cleanup, and disabled Kconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rpmsg/qcom_smd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rseq.h -->
# sources/distributed-fs/ceph-client/include/linux/rseq.h

## Purpose
`rseq.h` provides the scheduler, signal, exec/fork, and virtualization hooks for restartable sequences.

## Important APIs, types, and functions
Important APIs are `rseq_v2()`, `rseq_handle_slowpath()`, `rseq_signal_deliver()`, `rseq_raise_notify_resume()`, `rseq_sched_switch_event()`, `rseq_sched_set_ids_changed()`, `rseq_force_update()`, `rseq_virt_userspace_exit()`, `rseq_reset()`, `rseq_execve()`, `rseq_fork()`, `rseq_alloc_align()`, `rseq_syscall()`, `rseq_syscall_enter_work()`, and `rseq_slice_extension_prctl()`. It declares slow-path implementations such as `__rseq_handle_slowpath()` and `__rseq_signal_deliver()`.

## Control flow, state, and persistence
On context switch or CPU/MM CID change, scheduler code marks `task_struct::rseq.event` and raises `TIF_RSEQ`/notify-resume so exit-to-user updates the user TLS rseq area or aborts an active critical section. Signal delivery invokes rseq fixup before switching register context. `rseq_reset()` clears per-task rseq state under IRQ protection; exec always resets, while fork inherits for separate address spaces and resets for `CLONE_VM`. State persists per task in `task_struct::rseq` until unregister, exec, or clone rules clear it.

## Dependencies and integration points
It depends on `CONFIG_RSEQ`, scheduler task state, UAPI `struct rseq`, generic entry/TIF bits, signal delivery, KVM guest-mode exits, debug RSEQ, and optional slice-extension prctl/syscall hooks.

## Risks and test signals
Risks include lost notify-resume bits on architectures without generic TIF bits, incorrect ABI V1/V2 distinctions, inherited rseq state across clone modes, user TLS faults on exit paths, and virtualization paths clearing notify work too early. Test signals include rseq selftests for registration, fork/clone/exec, signal aborts, CPU migration ID updates, KVM guest-mode return, debug syscall tracing, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rseq_entry.h -->
# sources/distributed-fs/ceph-client/include/linux/rseq_entry.h

## Purpose
`rseq_entry.h` implements the fast and slow exit-to-user mechanics for restartable sequences, including statistics, tracepoints, critical-section validation/fixup, CPU/node/MM-CID updates, and optional time-slice extensions.

## Important APIs, types, and functions
Key elements include `struct rseq_stats`, `rseq_stat_inc()`, `rseq_trace_update()`, `rseq_trace_ip_fixup()`, `rseq_slice_extension_enabled()`, `rseq_arm_slice_extension_timer()`, `rseq_slice_clear_grant()`, `rseq_slice_clear_user()`, `rseq_grant_slice_extension()`, `rseq_note_user_irq_entry()`, `rseq_debug_update_user_cs()`, `rseq_update_user_cs()`, `rseq_set_ids_get_csaddr()`, `rseq_update_usr()`, `rseq_exit_user_update()`, `rseq_exit_to_user_mode_restart()`, `rseq_syscall_exit_to_user_mode()`, `rseq_irqentry_exit_to_user_mode()`, and `rseq_debug_syscall_return()`.

## Control flow, state, and persistence
Exit-to-user checks rseq event bits, writes CPU ID, node ID, and MM CID into the registered user `struct rseq`, reads `rseq_cs`, and either clears it or redirects the user instruction pointer to the abort IP if the interrupted IP is inside the critical section. Debug mode validates descriptor range, overflow, header fields, abort signature, and user-interrupt origin more strictly. Slice-extension code can grant a brief delay by updating user `slice_ctrl`, clearing resched state under IRQ protection, and arming a timer. Per-CPU stats and tracepoints record paths; per-task state is in `current->rseq`.

## Dependencies and integration points
It depends on generic entry, hrtimer rearm, jump labels, scheduler signal state, uaccess unsafe access regions, tracepoints, pagefault disabling, TIF bits, `task_cpu()`, `task_mm_cid()`, NUMA node lookup, and optional `CONFIG_RSEQ_STATS`, `CONFIG_RSEQ_SLICE_EXTENSION`, and `CONFIG_TRACEPOINTS`.

## Risks and test signals
Risks are high because this code runs in exit paths with interrupts/page faults constrained. Hazards include user pointer faults, bad abort IP signatures enabling control-flow attacks, memory-order bugs against GUP or reschedule IPIs, stale `user_irq` state, missed timer arming, and ABI V2 slice fields overwriting legacy users. Test signals include rseq selftests for signal/preemption aborts, debug-mode invalid descriptor death, forced user faults, tracepoint firing, stats increments, generic-entry fast-path loops, slice-extension grant/revoke/yield behavior, and lockdep/pagefault assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rseq_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rseq_types.h -->
# sources/distributed-fs/ceph-client/include/linux/rseq_types.h

## Purpose
`rseq_types.h` defines the per-task and per-mm storage structures used by restartable sequences and scheduler MM CID support.

## Important APIs, types, and functions
Important types are `struct rseq_event`, `struct rseq_ids`, `union rseq_slice_state`, `struct rseq_slice`, `struct rseq_data`, `struct sched_mm_cid`, `struct mm_cid_pcpu`, and `struct mm_mm_cid`. Constants include `RSEQ_HAS_RSEQ_VERSION_MASK`, `MM_CID_UNSET`, `MM_CID_ONCPU`, and `MM_CID_TRANSIT`.

## Control flow, state, and persistence
The header has no functions; it defines state layouts. `rseq_event` packs scheduler, ID-change, user-IRQ, registration-version, fatal, and slowpath flags for efficient stores. `rseq_ids` caches values last written to user space. Slice state tracks enabled/granted/yielded and expiration time. MM-CID structures track task CID ownership, per-CPU CIDs, deferred affinity updates, users, and locks for per-mm allocation/convergence.

## Dependencies and integration points
It depends on irq work and workqueue type definitions, cacheline alignment, raw spinlocks, mutexes, hlist nodes, and Kconfig options `CONFIG_RSEQ`, `CONFIG_RSEQ_SLICE_EXTENSION`, and `CONFIG_SCHED_MM_CID`. Scheduler, rseq syscall, fork/exit, affinity, and exit-to-user code consume these layouts through `task_struct` and `mm_struct`.

## Risks and test signals
Risks include layout changes that break optimized single-word stores, event-bit clearing that drops registration version, false sharing in hot paths, MM-CID state machine races, and empty-struct compatibility when configs are disabled. Test signals include build coverage across Kconfig matrices, scheduler migration/CID selftests, rseq ABI registration tests, cacheline/layout assertions, fork/exit CID cleanup, and affinity mode-change stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rseq_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rslib.h -->
# sources/distributed-fs/ceph-client/include/linux/rslib.h

## Purpose
`rslib.h` declares the kernel Reed-Solomon codec interface for 8-bit and 16-bit data streams.

## Important APIs, types, and functions
Core types are `struct rs_codec` and `struct rs_control`. APIs include optional `encode_rs8()`, `decode_rs8()`, `encode_rs16()`, `decode_rs16()`, `init_rs_gfp()`, inline `init_rs()`, `init_rs_non_canonical()`, `free_rs()`, and inline `rs_modnn()`.

## Control flow, state, and persistence
Callers initialize a codec by symbol size, primitive polynomial or generator function, first consecutive root, primitive element, and root count. The shared `rs_codec` holds Galois field tables, generator polynomial, users count, and list linkage; each `rs_control` carries codec pointer plus scratch buffers for decode. Encode/decode operations use caller data/parity buffers and optional erasure/correction arrays. State persists in allocated codec/control objects until `free_rs()`.

## Dependencies and integration points
It depends on kernel allocation flags and basic types, with encode/decode availability controlled by Reed-Solomon Kconfig symbols. Integration points include storage ECC, NAND/MTD, optical/media protocols, and other drivers needing systematic RS parity or correction.

## Risks and test signals
Risks include invalid primitive polynomials, symbol sizes beyond supported range, parity length mismatches, scratch-buffer lifetime errors, and using `rs_modnn()` outside its expected field range. Test signals include known-vector encode/decode tests, erasure correction, uncorrectable error reporting, non-canonical field initialization, refcounted codec reuse/free, and Kconfig combinations where only encode or decode is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rslib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc.h -->
# sources/distributed-fs/ceph-client/include/linux/rtc.h

## Purpose
`rtc.h` is the generic in-kernel Real Time Clock class interface. It defines driver callbacks, RTC device state, alarm/timer helpers, timestamp limits, NVMEM/sysfs integration, and user-facing IRQ update plumbing.

## Important APIs, types, and functions
Core types are `struct rtc_class_ops`, `struct rtc_timer`, and `struct rtc_device`. Important functions include calendar helpers `rtc_month_days()`, `rtc_year_days()`, `rtc_valid_tm()`, `rtc_tm_to_time64()`, `rtc_time64_to_tm()`, `rtc_tm_to_ktime()`, `rtc_ktime_to_tm()`, inline `rtc_tm_sub()`, registration APIs `devm_rtc_device_register()`, `devm_rtc_allocate_device()`, `devm_rtc_register_device()`, time/alarm APIs `rtc_read_time()`, `rtc_set_time()`, `rtc_read_alarm()`, `rtc_set_alarm()`, `rtc_initialize_alarm()`, IRQ APIs `rtc_update_irq()`, `rtc_irq_set_state()`, `rtc_irq_set_freq()`, `rtc_update_irq_enable()`, `rtc_alarm_irq_enable()`, timer APIs `rtc_timer_init()`, `rtc_timer_start()`, `rtc_timer_cancel()`, offset APIs, inline `is_leap_year()`, and `rtc_bound_alarmtime()`.

## Control flow, state, and persistence
RTC drivers fill `rtc_class_ops`; the core serializes most callbacks with `ops_lock`. `rtc_device` owns cdev state, IRQ wait queues, async notification, timer queues for alarm/update/periodic emulation, feature bits, valid time range, alarm-offset limits, start/offset seconds, and optional UIE emulation state. Setting time uses `set_offset_nsec` to schedule bus writes close to the hardware tick. Persistent time/alarm/NVRAM state lives in the hardware; kernel state tracks registered class devices and emulated timers.

## Dependencies and integration points
It depends on device/class infrastructure, interrupts, cdev, poll, mutexes, timerqueue/hrtimer, workqueues, NVMEM provider support, sysfs groups, and UAPI RTC structs/ioctls. It integrates with `/dev/rtc*`, proc/sysfs, hctosys, alarm wakeups, nvmem cells, legacy IRQ emulation, and bus-specific RTC drivers.

## Risks and test signals
Risks include invalid calendar conversions, time-range overflow, slow-bus set-time skew, missed alarm bounds, IRQ/fasync races, UIE emulation drift, and driver callbacks sleeping or racing outside `ops_lock`. Test signals include leap-year/range tests, read/set time around century boundaries, alarm enable/disable and wakeup tests, periodic/update IRQ emulation, NVMEM registration, hctosys selection, and sysfs group coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/ds1286.h -->
# sources/distributed-fs/ceph-client/include/linux/rtc/ds1286.h

## Purpose
`rtc/ds1286.h` documents register offsets and bits for the Dallas DS1286-compatible RTC.

## Important APIs, types, and functions
The header exports register and bit macros for time/date fields, alarm registers, command/control bits, watchdog/interrupt status, and battery/oscillator flags. It defines no C functions.

## Control flow, state, and persistence
Driver code reads/writes the DS1286 registers using these offsets, typically latching or stopping updates via command bits before changing time or alarm fields. Persistent state is battery-backed RTC time, alarm/watchdog configuration, and status flags in the chip.

## Dependencies and integration points
It is a hardware register map consumed by the DS1286 RTC driver or board code. It integrates with the RTC class through the driver's read/set time, alarm, and status handling.

## Risks and test signals
Risks include BCD/binary conversion mistakes, clearing status bits inadvertently, programming alarms while updates are active, and ignoring low-battery/oscillator-stop status. Test signals include register-level read/write tests, alarm interrupt behavior, watchdog/status flag handling, and time retention across power loss when hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/ds1286.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/ds1307.h -->
# sources/distributed-fs/ceph-client/include/linux/rtc/ds1307.h

## Purpose
`rtc/ds1307.h` provides platform data and trickle-charger constants for DS1307-family I2C RTC devices.

## Important APIs, types, and functions
The header defines trickle-charger setup bits `DS1307_TRICKLE_CHARGER_250_OHM`, `DS1307_TRICKLE_CHARGER_2K_OHM`, `DS1307_TRICKLE_CHARGER_4K_OHM`, `DS1307_TRICKLE_CHARGER_NO_DIODE`, and `DS1307_TRICKLE_CHARGER_DIODE`. The important type is `struct ds1307_platform_data`, with `trickle_charger_setup`.

## Control flow, state, and persistence
Board/platform code passes the platform data to the DS1307 driver. During probe, the driver can program the chip's trickle charger according to the selected resistor/diode bits. Persistent state is in the RTC hardware's charger/control registers and battery-backed timekeeping.

## Dependencies and integration points
It depends on basic integer types and integrates non-DT or board-file configurations with the DS1307 RTC driver.

## Risks and test signals
Risks include unsafe charger configuration for the board's battery/supercap, missing diode/resistor bits, and divergence between platform data and devicetree properties. Test signals include DS1307 probe with and without platform data, register programming for each supported charger option, suspend/resume retention, and hardware validation of charging behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/ds1307.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/ds1685.h -->
# sources/distributed-fs/ceph-client/include/linux/rtc/ds1685.h

## Purpose
`rtc/ds1685.h` is the register, bit, model, frequency, NVRAM-size, and poweroff interface definition for DS1685/DS1687/DS1689/DS1693/DS17x85 RTC chips.

## Important APIs, types, and functions
The header exports extensive macros for bank 0 and bank 1 time/alarm/control registers, control bits `RTC_CTRL_*`, model IDs such as `RTC_MODEL_DS1685`, square-wave/periodic frequencies `RTC_SQW_*`, NVRAM base/size constants, model-specific extended RAM or counter registers, and `ds1685_rtc_poweroff(struct platform_device *pdev)`.

## Control flow, state, and persistence
The driver uses the macros to select register banks, read/write BCD time, manage periodic/alarm/update interrupts, inspect valid-time and auxiliary-battery status, enable wake/kickstart/RAM-clear features, and expose NVRAM regions. Model-specific Kconfig determines which bank-1 registers and extended NVRAM sizes are visible. Persistent state is battery-backed time, alarms, control bits, serial/model fields, counters, and NV-SRAM.

## Dependencies and integration points
It depends on platform-device declarations and selected RTC driver Kconfig symbols. It integrates with rtc-ds1685 driver code, platform poweroff support, RTC class alarm/time operations, and NVRAM access.

## Risks and test signals
Risks include bank-selection mistakes, model-specific register address mismatches, accidentally enabling 32.768 kHz output instead of periodic interrupts, invalid VRT/VRT2 battery status handling, and wrong NVRAM sizing. Test signals include model-detection tests, banked register access, alarm/update interrupt handling, NVRAM read/write bounds per model, poweroff path coverage, and low-battery/status flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/ds1685.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/m48t59.h -->
# sources/distributed-fs/ceph-client/include/linux/rtc/m48t59.h

## Purpose
`rtc/m48t59.h` defines platform data and register offsets for M48T59/M48T02/M48T08 battery-backed RTC/NVRAM chips.

## Important APIs, types, and functions
Macros identify time registers, alarm registers, control bits such as `M48T59_CNTL_READ` and `M48T59_CNTL_WRITE`, interrupt/watchdog/low-battery flags, and chip type IDs. `struct m48t59_plat_data` supplies board-specific `write_byte()`/`read_byte()` callbacks, chip type, mapped IO address, register offset, and year offset.

## Control flow, state, and persistence
The driver uses callbacks or mapped IO to access chip registers. It sets read/write control bits around coherent time updates, handles alarm/watchdog flags, and interprets two-digit years through `yy_offset`. Persistent state is battery-backed RTC time, alarm/watchdog config, flags, and any NVRAM exposed by the device.

## Dependencies and integration points
It depends on `struct device` and `void __iomem` usage by board/platform code. It integrates with the M48T59 RTC driver and platform devices on systems where register access is board-specific.

## Risks and test signals
Risks include wrong register base offset for chip type, callback lifetime bugs, century/year offset errors, and clearing alarm/watchdog/low-battery flags unintentionally. Test signals include platform probe for all supported types, coherent read/write with control bits, alarm IRQ/status behavior, low-battery flag reporting, and year rollover tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/m48t59.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/rtc-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/rtc/rtc-omap.h

## Purpose
`rtc/rtc-omap.h` declares the OMAP RTC power-off programming hook.

## Important APIs, types, and functions
The sole API is `omap_rtc_power_off_program(struct device *dev)`, which lets OMAP platform/power code program the RTC block for power-off behavior.

## Control flow, state, and persistence
Callers pass the RTC device to `omap_rtc_power_off_program()` before system poweroff so the driver/hardware can prepare the RTC-controlled shutdown or wake path. Persistent state is hardware programming in the OMAP RTC/power domain.

## Dependencies and integration points
It depends on `struct device` from normal kernel includes and integrates OMAP RTC driver code with platform poweroff flows and the generic RTC class.

## Risks and test signals
Risks include invoking the hook on the wrong device, failing to program wake/poweroff registers before shutdown, and SoC-specific power sequencing differences. Test signals include OMAP RTC probe, system poweroff, alarm wake from poweroff/suspend, and builds where the hook is referenced by platform power code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtc/rtc-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtmutex.h -->
# sources/distributed-fs/ceph-client/include/linux/rtmutex.h

## Purpose
`rtmutex.h` declares real-time mutexes: blocking mutual exclusion locks with priority-inheritance support.

## Important APIs, types, and functions
Core types are `struct rt_mutex_base` and `struct rt_mutex`. Important macros and APIs include `__RT_MUTEX_BASE_INITIALIZER`, `rt_mutex_base_is_locked()`, `RT_MUTEX_HAS_WAITERS`, `rt_mutex_owner()`, `rt_mutex_base_init()`, `DEFINE_RT_MUTEX()`, `rt_mutex_init()`, `__rt_mutex_init()`, `rt_mutex_lock()`, `rt_mutex_lock_nested()`, `rt_mutex_lock_nest_lock()`, `rt_mutex_lock_interruptible()`, `rt_mutex_lock_killable()`, `rt_mutex_trylock()`, `rt_mutex_unlock()`, and optional `rt_mutex_debug_task_free()`.

## Control flow, state, and persistence
An rtmutex owns a raw spinlock-protected waiter rb-tree and owner pointer. Lock acquisition may block, enqueue waiters by priority, and trigger priority inheritance in the implementation. The low bit of owner can encode waiter presence. Debug-lock builds add lockdep maps and nested-lock variants. State persists in the lock object until initialized again or destroyed with its owner.

## Dependencies and integration points
It depends on compiler annotations, linkage, rbtree types, raw spinlock types, task structs, lockdep, and `CONFIG_RT_MUTEXES`/debug options. It underpins PI locking, futex PI, PREEMPT_RT primitives, and other sleeping locks that need deterministic priority behavior.

## Risks and test signals
Risks include using rtmutexes in atomic context, owner-bit misuse, missing unlock on error paths, lock ordering inversions, priority inheritance chain depth issues, and debug/non-debug API differences. Test signals include rtmutex selftests, lockdep nested-lock coverage, PI futex tests, interruptible/killable acquisition, trylock behavior, task-exit debug cleanup, and PREEMPT_RT scheduling latency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtmutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtnetlink.h -->
# sources/distributed-fs/ceph-client/include/linux/rtnetlink.h

## Purpose
`rtnetlink.h` declares rtnetlink notification helpers and the RTNL locking interface used to serialize network configuration changes.

## Important APIs, types, and functions
Important functions include `rtnetlink_send()`, `rtnetlink_maybe_send()`, `rtnl_unicast()`, `rtnl_notify()`, `rtnl_set_sk_err()`, `rtnetlink_put_metrics()`, `rtnl_put_cacheinfo()`, `rtmsg_ifinfo()`, `rtmsg_ifinfo_newnet()`, `rtmsg_ifinfo_build_skb()`, `rtmsg_ifinfo_send()`, `rtnl_lock()`, `rtnl_unlock()`, `rtnl_trylock()`, `rtnl_lock_interruptible()`, `rtnl_lock_killable()`, `refcount_dec_and_rtnl_lock()`, per-net RTNL lock helpers, `dev_ingress_queue()`, `dev_ingress_queue_rcu()`, `dev_ingress_queue_create()`, `rtnetlink_init()`, `__rtnl_unlock()`, `rtnl_kfree_skbs()`, default FDB/bridge helpers, `rtnl_offload_xstats_notify()`, `rtnl_has_listeners()`, `rtnl_notify_needed()`, and `netif_set_operstate()`. It also defines `struct ndo_fdb_dump_context`.

## Control flow, state, and persistence
Network configuration writers take RTNL or per-net RTNL, update RCU-protected netdev state, and emit rtnetlink multicast/unicast notifications when listeners or echo flags require it. Helper macros combine RCU dereference/update with lockdep checks. Global state includes unregister wait queues/counts and network namespace rwsems declared here but defined elsewhere.

## Dependencies and integration points
It depends on mutexes, netdevice, wait queues, refcounts, netlink/UAPI rtnetlink, RCU, lockdep, ingress/egress queue configs, bridge/FDB operations, and network namespaces. It is used by virtually all netdevice, address, route, neighbor, bridge, and offload xstats configuration code.

## Risks and test signals
Risks include missing RTNL around netdev mutations, deadlocks from nesting RTNL with driver locks, incorrect RCU pointer replacement, notification storms or missing notifications, and small-RTNL/per-net lock mismatches. Test signals include lockdep assertions, rtnetlink selftests, netdev register/unregister races, listener/echo notification tests, FDB add/del/dump coverage, ingress/egress queue creation, and namespace teardown stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtsx_common.h -->
# sources/distributed-fs/ceph-client/include/linux/rtsx_common.h

## Purpose
`rtsx_common.h` holds shared constants and slot metadata for Realtek RTSX card-reader PCI child drivers.

## Important APIs, types, and functions
The header defines driver-name constants, `RTSX_REG_PAIR()`, spread-spectrum clock depth constants, card indexes `RTSX_SD_CARD` and `RTSX_MS_CARD`, clock-conversion direction constants, and `struct rtsx_slot` containing a platform device and card-event callback.

## Control flow, state, and persistence
Parent card-reader code creates platform child devices for card slots and stores each slot's event callback. Card-detect or interrupt handling invokes the callback to notify the SD/MMC or MemoryStick child. State persists in the parent `rtsx_slot` array while the PCI reader is registered.

## Dependencies and integration points
It integrates the RTSX PCI core with platform child drivers, and its constants are shared with `rtsx_pci.h`. It depends only on a forward `struct platform_device`.

## Risks and test signals
Risks include mismatched card indexes between parent and child drivers, wrong packed register/value pairs, and stale callbacks during remove. Test signals include PCI reader probe creating slots, SD/MS card insert/remove notifications, clock conversion paths, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtsx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtsx_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/rtsx_pci.h

## Purpose
`rtsx_pci.h` is the main register map and core interface for Realtek PCIe card-reader controllers.

## Important APIs, types, and functions
The file defines host controller registers (`RTSX_HCBAR`, `RTSX_HDBAR`, interrupt masks), SD/MS/card-power/clock/OCP/PHY/PCIe/L1 substate register constants, transfer state/result constants, DMA/SG buffer sizing, device IDs, package/version helpers, phase macros, and direct MMIO helpers `rtsx_pci_readl()`/`writel()` variants. Key types are `struct pcr_handle`, `struct pcr_ops`, `enum PDEV_STAT`, `enum ASPM_MODE`, `struct rtsx_cr_option`, `struct rtsx_hw_param`, and `struct rtsx_pcr`. APIs include `rtsx_pci_start_run()`, register/PHY read-write helpers, command queue helpers, DMA map/unmap/transfer, ping-pong buffer read/write, pull control, clock/power/voltage/card-exist helpers, `rtsx_pci_complete_unfinished_transfer()`, `rtsx_pci_get_cmd_data()`, `rtsx_pci_write_be32()`, and `rtsx_pci_update_phy()`.

## Control flow, state, and persistence
The PCI core maps BARs, allocates reserved command/SG buffers, fills `struct rtsx_pcr`, and uses batched register commands (`ci`) to program hardware. DMA helpers build SG descriptors in the reserved buffer, trigger transfers, and complete through interrupt/completion state. Chip-specific `pcr_ops` customize PHY access, LED, power, output voltage, ASPM/L1 substate, OCP, and vendor settings. Persistent runtime state includes current clock, card presence flags, interrupt enables, DMA error count, OCP/OVP status, ASPM state, chip revision, pull-control tables, and platform slots.

## Dependencies and integration points
It depends on PCI, scheduler/completion/mutex/spinlock primitives, scatterlist/DMA APIs through implementation files, and `rtsx_common.h`. It integrates the Realtek PCI core with SD/MMC and MemoryStick platform child drivers, runtime PM, MSI/INTx interrupts, card-detect delayed work, over-current protection, voltage switching, and PHY tuning for many Realtek device IDs.

## Risks and test signals
Risks include register constant drift across chip variants, DMA descriptor length limits, command-buffer overflow (`MAX_RW_REG_CNT`/reserved buffer), missed interrupts/completions, ASPM/L1 power-state races, unsafe voltage/OCP thresholds, and PHY tuning regressions. Test signals include probe on supported PIDs/revisions, register read/write batching, SG DMA read/write, card insertion/removal, suspend/resume/runtime PM, voltage switch, OCP interrupt handling, ASPM toggling, and SD high-speed tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtsx_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtsx_usb.h -->
# sources/distributed-fs/ceph-client/include/linux/rtsx_usb.h

## Purpose
`rtsx_usb.h` is the register map and exported core interface for Realtek RTS5139/RTS5179 USB card readers.

## Important APIs, types, and functions
Key constants cover USB endpoint numbers, vendor requests, card IDs/status bits, command packet offsets, stage flags, register maps for SD/MS/card/clock/OCP/USB/FIFO/DMA blocks, and internal bit values. The core type is `struct rtsx_ucr`, storing IDs, package/version, clock, command/response buffers, USB device/interface, current SG request, SG timer, and device mutex. APIs include register read/write via bulk or EP0, command batching/sending, response retrieval, data transfer, ping-pong buffer read/write, clock switching, card-exclusive checks, and inline LED/FSM/DMA error helpers.

## Control flow, state, and persistence
USB child drivers build commands in `cmd_buf` with `rtsx_usb_init_cmd()`, send them via vendor protocol, optionally read responses, and move payloads over bulk endpoints or USB SG. `cmd_idx`, current clock, SG request, and timer track in-flight operations. Inline error helpers flush FIFO and reset DMA on hardware faults. Persistent state is the USB interface/device registration and `rtsx_ucr` contents while the reader is present.

## Dependencies and integration points
It depends on the USB core, timer/mutex support via implementation users, and Realtek SD/MMC/MS child drivers. It integrates with USB control endpoint register access, bulk transfers, card detect/status, clock and voltage programming, OCP handling, and LED control.

## Risks and test signals
Risks include command buffer overflow, endpoint/protocol mismatches, SG timeout races, duplicate register definitions, insufficient locking around `cmd_buf`/`current_sg`, and failing to clear DMA/FSM errors after stalls. Test signals include USB probe/disconnect, EP0 and bulk register access, command batching, bulk read/write with and without SG, timeout/cancel paths, SD/MS card status, LED toggles, OCP status, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rtsx_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rv.h -->
# sources/distributed-fs/ceph-client/include/linux/rv.h

## Purpose
`rv.h` declares the Runtime Verification monitor and reactor interface used by kernel RV monitors.

## Important APIs, types, and functions
Core constants identify monitor scopes (`RV_MON_GLOBAL`, `RV_MON_PER_CPU`, `RV_MON_PER_TASK`, `RV_MON_PER_OBJ`) and name limits. Types include `struct da_monitor`, optional `struct ltl_monitor`, optional `struct ha_monitor`, `struct rv_reactor`, and `struct rv_monitor`. APIs include `rv_monitoring_on()`, `rv_register_monitor()`, `rv_unregister_monitor()`, `rv_get_task_monitor_slot()`, `rv_put_task_monitor_slot()`, `rv_register_reactor()`, `rv_unregister_reactor()`, and `rv_react()`.

## Control flow, state, and persistence
Monitors register with RV core and may be global, per-CPU, per-task, or per-object. Deterministic automata/LTL/HA monitor state is owned by monitor implementations and updated from tracepoints/events. Reactors register callbacks for violation responses; `rv_react()` formats a message and dispatches to the active reactor when RV is enabled. Registered monitors/reactors persist until unregistered.

## Dependencies and integration points
It depends on RV Kconfig options, monitor generated code, task monitor slot allocation, trace/events instrumentation, and optional automata models. Integration points include scheduler/preemption monitors, tracepoint-driven verification, sysfs/debugfs RV controls, and custom reaction policies.

## Risks and test signals
Risks include racing monitor state updates, exhausting per-task slots, reacting recursively from tracing contexts, accepting unknown LTL atoms/states, and build differences when RV subfeatures are disabled. Test signals include monitor register/unregister, per-task slot allocation/free, tracepoint event transitions, deliberate violation reactions, disabled-config no-op behavior, and generated automata state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rw_hint.h -->
# sources/distributed-fs/ceph-client/include/linux/rw_hint.h

## Purpose
`rw_hint.h` defines the block/filesystem write-life hint type.

## Important APIs, types, and functions
The central definition is `enum rw_hint`, with values from `WRITE_LIFE_NOT_SET`/`WRITE_LIFE_NONE` through short, medium, long, and extreme write lifetimes. It also defines the maximum hint value used for validation.

## Control flow, state, and persistence
Callers attach hints to files, inodes, bios, or writeback paths so lower layers can place data according to expected lifetime. The header itself has no logic; persistence depends on filesystem or block-layer storage of the selected hint.

## Dependencies and integration points
It integrates VFS, fcntl/ioctl hint APIs, filesystems, writeback, and block devices that can use data-temperature/lifetime information.

## Risks and test signals
Risks include accepting out-of-range hints, losing hints across inode/file transitions, and devices treating hints as stronger guarantees than intended. Test signals include VFS hint set/get tests, writeback propagation into bios, filesystem persistence where supported, and rejection of values above the max.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rw_hint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwbase_rt.h -->
# sources/distributed-fs/ceph-client/include/linux/rwbase_rt.h

## Purpose
`rwbase_rt.h` declares the PREEMPT_RT base implementation used by RT read/write locks and semaphores.

## Important APIs, types, and functions
It defines the RT reader/writer base structure and low-level initialization/acquire/release helpers used by `rwlock_rt.h` and related RT locking code.

## Control flow, state, and persistence
On RT kernels, rw locking is built on sleeping/PI-aware primitives rather than raw spinning for long sections. The base tracks reader/writer ownership and serializes transitions through RT-mutex-like state. State persists in the lock object.

## Dependencies and integration points
It depends on RT mutex infrastructure, atomic counters or owner tracking from the implementation, and PREEMPT_RT Kconfig selection. It integrates with `rwlock_rt.h`, `rwsem.h` RT variants, lockdep annotations, and scheduler priority inheritance.

## Risks and test signals
Risks include sleeping in contexts that expected raw rwlocks, reader/writer starvation or PI inversion, and differences from non-RT rwlock semantics. Test signals include PREEMPT_RT lock tests, lockdep class coverage, reader/writer contention stress, interrupt-context misuse detection, and latency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwbase_rt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock.h -->
# sources/distributed-fs/ceph-client/include/linux/rwlock.h

## Purpose
`rwlock.h` is the generic public include for kernel read/write spinlocks.

## Important APIs, types, and functions
It selects the appropriate raw or RT implementation and exposes standard rwlock operations such as initialization, read/write lock/unlock, trylock, IRQ-save/IRQ-restore variants, BH variants, and lock state assertions through included API/type headers.

## Control flow, state, and persistence
Non-RT rwlocks are spinning locks that allow multiple readers or one writer; RT builds may route to sleeping/PI-aware implementations. The lock word and optional debug state persist in each `rwlock_t` object.

## Dependencies and integration points
It depends on architecture rwlock primitives, lockdep, preempt/IRQ helpers, and RT conditional headers. It is used throughout kernel code that needs short read-mostly critical sections.

## Risks and test signals
Risks include deadlock from recursive write locking, writer starvation on some patterns, using sleeping code inside raw rwlock sections, IRQ state mismatches, and semantic differences under PREEMPT_RT. Test signals include locktorture, lockdep IRQ/BH nesting checks, trylock behavior, RT and non-RT builds, and architecture primitive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock_api_smp.h -->
# sources/distributed-fs/ceph-client/include/linux/rwlock_api_smp.h

## Purpose
`rwlock_api_smp.h` declares the SMP rwlock API wrappers around raw architecture lock operations with lockdep and preemption/IRQ accounting.

## Important APIs, types, and functions
It exposes `__raw_read_lock()`, `__raw_write_lock()`, interruptible variants where present, trylock helpers, unlock helpers, IRQ/BH save/restore variants, and macro wrappers that map public raw rwlock operations to instrumented implementations.

## Control flow, state, and persistence
Lock wrappers acquire lockdep state, disable preemption or interrupts as required, invoke arch raw rwlock operations, and release instrumentation on unlock. State persists in the lock object plus lockdep maps when enabled.

## Dependencies and integration points
It depends on SMP builds, architecture rwlock primitives, lockdep, preempt count, IRQ flag helpers, and debug spinlock instrumentation. `rwlock.h` includes it for SMP raw rwlock behavior.

## Risks and test signals
Risks include mismatched IRQ restore flags, missing lockdep acquire/release pairs, architecture primitive bugs hidden by wrappers, and using the wrong variant for interrupt context. Test signals include lockdep splats staying clean, locktorture rwlock runs, IRQ/BH nesting tests, trylock failure paths, and SMP contention stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock_api_smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock_rt.h -->
# sources/distributed-fs/ceph-client/include/linux/rwlock_rt.h

## Purpose
`rwlock_rt.h` provides the PREEMPT_RT implementation and API mapping for rwlocks.

## Important APIs, types, and functions
It defines RT-specific `rwlock_t` initialization and maps read/write lock, unlock, trylock, BH, IRQ, and IRQ-save forms onto RT-aware helper functions. It relies on the RT rwbase layer rather than pure spinning.

## Control flow, state, and persistence
RT rwlocks preserve source-level rwlock APIs while turning contended sections into sleeping/priority-inheritance aware waits where possible. IRQ/BH variants keep API compatibility but must respect RT's restrictions on sleeping locks. State persists in the RT lock object and lockdep metadata.

## Dependencies and integration points
It depends on PREEMPT_RT, `rwbase_rt.h`, scheduler/PI locking, lockdep, and public rwlock type definitions. It integrates with code compiled unchanged across RT and non-RT kernels.

## Risks and test signals
Risks include code assuming hard spinning or IRQ-safe semantics when RT may sleep, lock ordering differences, and trylock behavior under priority inheritance. Test signals include PREEMPT_RT locktorture, IRQ-context misuse tests, lockdep class validation, and latency benchmarks under reader/writer contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock_rt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock_types.h -->
# sources/distributed-fs/ceph-client/include/linux/rwlock_types.h

## Purpose
`rwlock_types.h` defines the public `rwlock_t` type and initializer macros.

## Important APIs, types, and functions
The key type is `rwlock_t`, wrapping `arch_rwlock_t` plus optional lockdep/debug fields. Important macros include unlocked initializers and `DEFINE_RWLOCK()`/initializer helpers selected for debug, lockdep, and RT configurations.

## Control flow, state, and persistence
There is no runtime control flow in the header. It establishes the memory layout and static initialization state for rwlock objects, including lock class metadata when enabled.

## Dependencies and integration points
It depends on architecture rwlock type definitions, lockdep/debug lock allocation, and PREEMPT_RT conditional type choices. It is included before API headers so all rwlock users share the same object layout.

## Risks and test signals
Risks include initializer/layout mismatches across configs, missing lock class keys for static locks, and embedding rwlocks in ABI-sensitive structures without considering debug fields. Test signals include build coverage for debug/lockdep/RT configs, static `DEFINE_RWLOCK()` use, structure size expectations where relevant, and lockdep recognizing distinct classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwsem.h -->
# sources/distributed-fs/ceph-client/include/linux/rwsem.h

## Purpose
`rwsem.h` declares sleeping reader/writer semaphores. It provides initialization, lock state queries, lockdep assertions, acquire/release APIs, guard constructors, downgrade support, and non-owner read variants.

## Important APIs, types, and functions
Important macros and APIs include `RWSEM_UNLOCKED_VALUE`, `RWSEM_WRITER_LOCKED`, `__RWSEM_INITIALIZER`, `DECLARE_RWSEM()`, `init_rwsem()`, `rwsem_is_locked()`, `rwsem_assert_held()`, `rwsem_assert_held_write()`, `rwsem_is_contended()`, `rwsem_owner()`, `is_rwsem_reader_owned()`, `down_read()`, `down_read_interruptible()`, `down_read_killable()`, `down_read_trylock()`, `down_write()`, `down_write_killable()`, `down_write_trylock()`, `up_read()`, `up_write()`, `downgrade_write()`, nested lock variants, lock-guard class constructors, `down_read_non_owner()`, and `up_read_non_owner()`.

## Control flow, state, and persistence
Readers and writers sleep when they cannot acquire the semaphore. Non-RT builds use an atomic count, waiter list, owner tracking, optional optimistic spinning queue, and lockdep map; RT builds use RT-specific rwsem types and operations. Guard constructors create scoped acquire/release wrappers for cleanup-style locking. State persists in `struct rw_semaphore` for the protected object.

## Dependencies and integration points
It depends on atomic longs, wait queues, optimistic spin queues, lockdep, mutex/RT internals, cleanup guards, scheduler/task ownership, and PREEMPT_RT configuration. It is used by MM (`mmap_lock`), filesystems, module/sysfs paths, and many sleeping read-mostly kernel subsystems.

## Risks and test signals
Risks include calling rwsems from atomic context, read/write lock ordering deadlocks, missed unlocks on error paths, ownership assertion false positives for non-owner read APIs, starvation/optimistic spinning issues, and RT semantic differences. Test signals include lockdep assertions, rwsem locktorture, interruptible/killable return-path tests, downgrade tests, mmap-lock stress, scoped-guard cleanup checks, and RT/non-RT build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rwsem.h -->
