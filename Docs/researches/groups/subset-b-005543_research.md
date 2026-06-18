# Research: subset-b-005543

Grouped research for USBIP virtual UDC files and vDPA driver files under `sources/distributed-fs/ceph-client`. Each section preserves its source path and is intended to be split into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_main.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_main.c

Purpose: module entry and exit for the USB/IP virtual USB device controller. It registers a `platform_driver` named by `GADGET_NAME`, creates `num` emulated controller platform devices, and tears them down on init failure or module exit.

Important APIs/types/functions: `module_param_named(num, vudc_number, uint, S_IRUGO)` exposes the controller count. `vudc_driver` binds `.probe = vudc_probe`, `.remove = vudc_remove`, and `vudc_groups` sysfs attributes. `vudc_init()` checks `usb_disabled()`, validates at least one device, registers the driver, then calls `alloc_vudc_device()`, `platform_device_add()`, and `platform_get_drvdata()`. `vudc_cleanup()` reverses the global `vudc_devices` list with `platform_device_del()` and `put_vudc_device()`.

Control flow: successful init is driver registration followed by per-index device allocation/addition/listing. Any device allocation, add, or failed probe jumps to cleanup that removes already-added devices and unregisters the driver. Exit always walks the same list and unregisters after deleting all devices.

State and persistence: persistent kernel state is the module parameter and static `vudc_devices` list. Device lifetime is reference-counted through platform device put paths. There is no disk persistence.

Dependencies and integration: depends on platform bus, USB core availability, and helpers from `vudc.h`. Sysfs integration is delegated through `vudc_groups`, and all network/transfer behavior lives in the other vudc files.

Risks: partial init cleanup relies on list membership only after successful `platform_device_add()`, so earlier failures are handled separately. The `platform_get_drvdata()` post-add check treats a probe failure after platform add as `-EINVAL`; diagnostics depend on probe-side logs.

Test signals: load with default and multiple `num=` values, reject `num=0`, verify created platform devices expose sysfs attributes, and inject probe/allocation failures to confirm cleanup leaves no devices or registered driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_rx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_rx.c

Purpose: receive-side USB/IP protocol handling for vudc. It reads TCP PDUs, converts `USBIP_CMD_SUBMIT` into kernel URBs queued on the emulated gadget endpoints, and handles `USBIP_CMD_UNLINK` cancellation requests.

Important APIs/types/functions: `alloc_urb_from_cmd()` allocates `struct urb`, copies USBIP submit fields via `usbip_pack_pdu()`, allocates transfer/setup buffers, and sets a minimal pipe direction/type. `v_recv_cmd_submit()` allocates `struct urbp`, finds the target `vep`, validates isochronous packet counts, receives OUT/ISO payloads with `usbip_recv_xbuff()` and `usbip_recv_iso()`, then queues the URB. `v_recv_cmd_unlink()` marks matching queued URBs with `-ECONNRESET` or queues an immediate RET_UNLINK. `v_rx_pdu()` reads/corrects a `usbip_header`, checks `SDEV_ST_USED`, and dispatches. `v_rx_loop()` is the kthread body.

Control flow: the RX thread loops until stop or USBIP event. Each PDU is read in full, endian-corrected, and rejected if the USBIP device is not in use. SUBMIT resolves endpoint, allocates URB state, receives payload descriptors, kicks the transfer timer, and appends to `udc->urb_queue`. UNLINK scans the same queue under `udc->lock`; found URBs are completed later by the timer, while missing URBs generate an unlink response immediately on `tx_queue`.

State and persistence: `urbp` stores endpoint, type, `seqnum`, and `new` setup-stage flag. Queue state is protected by `udc->lock`; transmit queue insertion additionally uses `lock_tx`. Protocol errors add `VUDC_EVENT_ERROR_TCP`; allocation failures add `VUDC_EVENT_ERROR_MALLOC`.

Dependencies and integration: relies on `usbip_common` PDU helpers, vudc endpoint lookup, transfer timer (`v_kick_timer()`), and TX queue helpers (`v_enqueue_ret_unlink()`). It feeds `vudc_transfer.c`, which consumes `urb_queue`.

Risks: pipe setup is intentionally minimal and marked FIXME, so assumptions in shared usbip helpers matter. Isochronous support is partially validated here but later rejected in the timer path. Endpoint lookup occurs under lock, but endpoint state can still change before transfer, so transfer-side checks remain important.

Test signals: submit to valid/invalid endpoints, OUT payload reception, IN zero-payload submit, unlink before and after completion, malformed/truncated TCP header, non-`SDEV_ST_USED` socket state, and isochronous packet count bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_sysfs.c

Purpose: sysfs control plane for vudc. It exposes device descriptor bytes, USB/IP socket attach/detach, and current USBIP device status.

Important APIs/types/functions: `get_gadget_descs()` synthesizes a GET_DESCRIPTOR setup request through the bound gadget driver and caches `udc->dev_desc`. `dev_desc_read()` serves the binary `dev_desc` attribute once cached. `usbip_sockfd_store()` accepts a userspace socket fd or `-1`, validates gadget readiness and socket type, creates RX/TX kthreads, installs `udc->ud.tcp_socket`, transitions status to `SDEV_ST_USED`, starts the transfer timer, and wakes threads. `usbip_status_show()` returns `udc->ud.status`. `vudc_groups` exports the attributes to the platform driver.

Control flow: attach path takes `sysfs_lock`, checks `driver` and `pullup`, validates availability, looks up a stream socket, creates RX/TX threads outside spinlocks, then publishes socket/thread/status under locks and starts timer. Detach path checks current connection and adds `VUDC_EVENT_DOWN`; teardown is handled by event processing elsewhere. Descriptor read simply fails with `-ENODEV` until descriptor cache is populated.

State and persistence: caches `struct usb_device_descriptor`, `desc_cached`, `connected`, `start_time`, socket pointer, thread task pointers, and USBIP status. State is protected by `udc->lock`, `udc->ud.lock`, and `udc->ud.sysfs_lock`; no disk persistence.

Dependencies and integration: integrates Linux sysfs, socket fd lookup, kthreads (`v_rx_loop`, `v_tx_loop`), gadget driver `setup()`, transfer timer, and usbip event handling. It is the user-visible attach point used by usbip tooling.

Risks: `get_gadget_descs()` assumes the ep0 request queue contains the descriptor request after calling gadget `setup()`. Attach failure paths must release socket/task references in the right order. `dev_desc_read()` trusts sysfs to bound offset/count to the bin attribute size.

Test signals: write valid TCP socket fd, invalid fd, datagram fd, duplicate attach, detach with `-1`, detach when not connected, descriptor read before/after gadget binding, and race attach/detach under sysfs locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_transfer.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_transfer.c

Purpose: emulates USB bus transfer progress between host-side USBIP URBs and gadget-driver `usb_request`s. A timer processes queued URBs, handles standard control requests, copies payloads, and queues USBIP return packets.

Important APIs/types/functions: `get_frame_limit()` estimates per-frame bandwidth by USB speed. `handle_control_request()` handles standard SET_ADDRESS, SET/CLEAR_FEATURE, and GET_STATUS locally. `transfer()` copies data between URB and gadget request queues, handles short packets, zero packets, overflow status, and gives completed gadget requests back. `v_timer()` is the scheduler over `udc->urb_queue`. `v_init_timer()`, `v_start_timer()`, `v_kick_timer()`, and `v_stop_timer()` manage `transfer_timer` state.

Control flow: RX enqueues URBs and kicks the timer. `v_timer()` computes current frame budget, clears endpoint `already_seen`, scans queued URBs, handles unlink/halt/setup cases, calls gadget `setup()` for unhandled control requests, transfers data for bulk/control/interrupt endpoints, rejects isochronous with `-EXDEV`, and moves completed URBs to the TX queue. If URBs remain, it re-arms for the next frame; otherwise it transitions idle.

State and persistence: mutable state includes `udc->urb_queue`, endpoint flags (`halted`, `wedged`, `setup_stage`, `already_seen`), device status bits, address, URB statuses/actual lengths, request statuses/actual lengths, and timer state (`STOPPED`, `IDLE`, `RUNNING`). All timer processing occurs under `udc->lock`, with temporary unlocks around gadget callbacks/giveback.

Dependencies and integration: bridges `vudc_rx.c` queued URBs, gadget endpoint request queues, Linux USB gadget callbacks, and `vudc_tx.c` return queue helpers. Uses kernel timers and USB descriptor/status constants.

Risks: timer accuracy and bandwidth accounting are approximate. Unlocking around gadget callbacks requires careful rescan logic because request queues may change. Isochronous endpoints are accepted by RX but completed with `-EXDEV`. Standard control emulation is incomplete, so gadget setup fallback is critical.

Test signals: control enumeration requests, endpoint halt/clear halt, bulk IN/OUT short and exact packets, zero-length packet behavior, request overflow/underflow, unlink while active, no-speed idle behavior, and timer re-arm when queues remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_transfer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_tx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_tx.c

Purpose: transmit-side USB/IP response path for vudc. It sends `USBIP_RET_SUBMIT` completions and `USBIP_RET_UNLINK` replies over the attached TCP socket.

Important APIs/types/functions: `setup_base_pdu()`, `setup_ret_submit_pdu()`, and `setup_ret_unlink_pdu()` build response headers. `v_send_ret_submit()` constructs iovecs for header, IN data, and optional ISO descriptors, sends them with `kernel_sendmsg()`, and frees the completed URB package. `v_send_ret_unlink()` sends unlink status and frees the unlink record. `v_send_ret()` drains `udc->tx_queue`. `v_tx_loop()` waits on `tx_waitq`. `v_enqueue_ret_submit()` and `v_enqueue_ret_unlink()` allocate `tx_item`s under spinlocks.

Control flow: transfer/unlink code appends TX items and wakes `tx_waitq`. The TX thread drains all available items under `lock_tx`, releasing the lock while sending each item. Send size mismatches add a TCP error event. Submit completions include IN payload only when appropriate; ISO IN payload is sent per frame descriptor plus an ISO descriptor PDU.

State and persistence: `tx_queue` holds `TX_SUBMIT` and `TX_UNLINK` items. Ownership transfers to TX send functions, which free URB/unlink memory after send attempt. No persistent storage exists.

Dependencies and integration: consumes outputs from `vudc_transfer.c` and `vudc_rx.c`, uses usbip endian/packing helpers, socket `kernel_sendmsg()`, and USBIP event flags. Kthread lifecycle is created from sysfs attach.

Risks: allocation failures in enqueue use `GFP_ATOMIC`; the code reports `VDEV_EVENT_ERROR_MALLOC`, which should be checked against the surrounding event enum naming. A failed submit send still frees the URB package, so recovery is connection-level. ISO handling is mostly passthrough despite transfer-side lack of true ISO support.

Test signals: RET_SUBMIT for IN and OUT, RET_UNLINK success and cancellation status, short socket writes, queue wakeups, empty queue wait behavior, and memory ownership under send failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vdpa/Kconfig

Purpose: Kconfig menu for vDPA drivers, simulators, userspace vDPA, and vendor hardware backends.

Important APIs/types/functions: defines `menuconfig VDPA` gated on `NET`; simulator options `VDPA_SIM`, `VDPA_SIM_NET`, `VDPA_SIM_BLOCK`; `VDPA_USER`; hardware drivers `IFCVF`, `MLX5_VDPA`, `MLX5_VDPA_NET`, `MLX5_VDPA_STEERING_DEBUG`, `VP_VDPA`, `ALIBABA_ENI_VDPA`, `SNET_VDPA`, `PDS_VDPA`, and `OCTEONEP_VDPA`.

Control flow: Kconfig dependency resolution controls which Makefile objects build. `MLX5_VDPA` is a selected bool support library, while `MLX5_VDPA_NET` is the user-visible tristate. `OCTEONEP_VDPA` depends on `m`, forcing module-only builds.

State and persistence: stores build configuration symbols, not runtime state.

Dependencies and integration: selects vhost/IOMMU/virtio helper libraries where needed and ties vendor directories to top-level `drivers/vdpa/Makefile`.

Risks: feature availability is compile-time; missing selects produce link or runtime capability gaps. `ALIBABA_ENI_VDPA` is X86-only and legacy virtio-pci based. Debug steering counters are separately gated.

Test signals: build matrix for built-in/module/off combinations, dependency visibility with and without PCI_MSI/MLX5_CORE/PDS_CORE, and module-only enforcement for Octeon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/Makefile

Purpose: top-level vDPA build routing.

Important APIs/types/functions: maps Kconfig symbols to objects/subdirectories: `vdpa.o`, `vdpa_sim/`, `vdpa_user/`, `ifcvf/`, `mlx5/`, `virtio_pci/`, `alibaba/`, `solidrun/`, `pds/`, and `octeon_ep/`.

Control flow: kbuild descends into vendor subdirectories only when the associated config symbol is enabled.

State and persistence: no runtime state; build graph only.

Dependencies and integration: integrates Kconfig with kbuild object generation for the vDPA subsystem.

Risks: symbol/object mismatches silently omit drivers or cause link failures. The file assumes subdirectory Makefiles provide module composition.

Test signals: `make drivers/vdpa/` with each relevant config enabled, and module list checks for expected `.ko` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/Makefile

Purpose: kbuild entry for Alibaba ENI vDPA.

Important APIs/types/functions: `obj-$(CONFIG_ALIBABA_ENI_VDPA) += eni_vdpa.o`.

Control flow: builds `eni_vdpa.c` into a module or built-in object according to `CONFIG_ALIBABA_ENI_VDPA`.

State and persistence: build-only file.

Dependencies and integration: reached from top-level `drivers/vdpa/Makefile`; depends on Kconfig gating for PCI MSI, X86, and legacy virtio-pci helpers.

Risks: no multi-object composition, so all driver logic must remain in `eni_vdpa.c` unless this file is updated.

Test signals: confirm `eni_vdpa.o` builds and module name matches expectation when config is `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/eni_vdpa.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/eni_vdpa.c

Purpose: vDPA bridge for Alibaba ENI devices implemented as legacy virtio-pci network devices. It exposes a legacy virtio PCI function as a `vdpa_device`.

Important APIs/types/functions: `struct eni_vdpa` embeds `vdpa_device`, `virtio_pci_legacy_device`, vring callback/IRQ state, and config callback. `eni_vdpa_ops` implements feature negotiation, status/reset, virtqueue size/address/ready/callback/kick, config access, and IRQ lookup. `eni_vdpa_request_irq()` allocates one MSI-X vector per queue plus config. `eni_vdpa_probe()` enables PCI, probes legacy virtio, allocates vring state, and registers with the vDPA bus.

Control flow: probe initializes legacy virtio-pci state, discovers queue count from features/config, prepares notify addresses, and registers the vDPA device. When status gains `DRIVER_OK`, IRQ vectors are requested and programmed with `vp_legacy_queue_vector()`/`vp_legacy_config_vector()`. Reset or clearing `DRIVER_OK` disables vectors. Queue kicks write queue id to the legacy notify register.

State and persistence: state is in `eni_vdpa`: queue count, vector count, per-vring IRQ/callback/notify pointer, config IRQ/callback, and legacy device state. No persistence beyond PCI device lifetime.

Dependencies and integration: uses Linux PCI, vDPA core, `virtio_pci_legacy` accessors, virtio-net config layout, MSI-X, and Red Hat/Qumranet virtio PCI IDs with Alibaba subsystem matching.

Risks: legacy virtio-pci cannot set/get full migration queue state; `get_vq_state()` is unsupported and `set_vq_state()` only accepts initial zero state. Feature negotiation requires `VIRTIO_NET_F_MRG_RXBUF` if any features are negotiated. IRQ allocation result from `eni_vdpa_request_irq()` in `set_status()` is not propagated to the vDPA caller.

Test signals: PCI probe/remove, feature negotiation with/without MRG_RXBUF, DRIVER_OK IRQ setup/free, queue notify writes, config read/write offsets after vector count changes, reset paths, and queue-state migration rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/alibaba/eni_vdpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/Makefile

Purpose: kbuild composition for the Intel IFC VF vDPA driver.

Important APIs/types/functions: `obj-$(CONFIG_IFCVF) += ifcvf.o`; `ifcvf-$(CONFIG_IFCVF) += ifcvf_main.o ifcvf_base.o`.

Control flow: builds a composite `ifcvf` module from the vDPA bus glue and low-level hardware helper files.

State and persistence: build-only file.

Dependencies and integration: selected from the top-level vDPA Makefile and Kconfig `IFCVF`.

Risks: adding new IFCVF files requires updating the composite object list.

Test signals: module build confirms both `ifcvf_main.o` and `ifcvf_base.o` are linked into `ifcvf.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.c

Purpose: low-level Intel IFC VF hardware access layer for modern virtio PCI capabilities, queue registers, live migration state, config space, and notification.

Important APIs/types/functions: `ifcvf_init_hw()` parses vendor PCI capabilities, maps common/notify/isr/device config regions, computes per-queue notify addresses, and initializes IRQ sentinels. `ifcvf_get_hw_features()`, `ifcvf_set_driver_features()`, and `ifcvf_get_driver_features()` access feature registers. `ifcvf_get_config_size()`, `ifcvf_read_dev_config()`, and `ifcvf_write_dev_config()` handle config space. Queue operations include size, address, ready, notify, and LM state access through `ifcvf_get_vq_state()`/`ifcvf_set_vq_state()`. `ifcvf_stop()` synchronizes IRQs and resets handlers/vectors.

Control flow: init scans PCI capabilities from the capability list, validates all required virtio modern regions, allocates `vring_info` for `num_queues`, and records notify offsets. Queue setters select `queue_select` before touching queue registers. Reset writes status 0 and polls until the device reports reset. Config reads retry if `config_generation` changes.

State and persistence: `struct ifcvf_hw` holds MMIO pointers, notify geometry, vring array, feature/config sizes, callbacks, IRQ state, and device type. State lives for the PCI device/mgmt-device lifetime.

Dependencies and integration: used by `ifcvf_main.c`; depends on modern virtio PCI register layout, BAR mappings from pcim, live migration BAR 4, and vDPA/vhost feature constants.

Risks: pointer arithmetic against `ifcvf_lm_cfg.vq_state_region` must match hardware layout. `ifcvf_verify_min_features()` requires `VIRTIO_F_ACCESS_PLATFORM` for nonzero features. Config size is limited to known net/block structs; other virtio IDs return size 0.

Test signals: capability parsing with missing regions, queue notify address calculation, feature read/write, reset completion, config generation retry, queue state save/restore, and invalid queue id returning zero size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.h

Purpose: shared IFCVF constants, data structures, and hardware-helper prototypes.

Important APIs/types/functions: defines N3000 IDs, BAR constants, min queue size, MSI-X allocation modes, `struct vring_info`, `struct ifcvf_lm_cfg`, `struct ifcvf_hw`, `struct ifcvf_adapter`, and `struct ifcvf_vdpa_mgmt_dev`. Declares all hardware operations used by `ifcvf_main.c`.

Control flow: no executable flow; it establishes the contract between hardware access and vDPA glue layers.

State and persistence: describes persistent in-memory state for mapped registers, callbacks, IRQs, features, and vDPA management/adapter ownership.

Dependencies and integration: includes PCI, vDPA, modern virtio-pci, virtio net/block/config, and uapi vDPA headers.

Risks: structure fields encode hardware assumptions such as LM BAR index and MSI-X sharing modes. Consumers must initialize sentinel IRQ values and allocated `vring` arrays consistently.

Test signals: compile coverage across net and block IDs, structure use by both source files, and static analysis for uninitialized fields after allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_main.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_main.c

Purpose: PCI and vDPA management glue for Intel IFC VF devices. It registers a management device at PCI probe time and creates actual vDPA devices through management operations.

Important APIs/types/functions: interrupt handlers dispatch config, per-vq, shared-vq, or fully shared device interrupts to vDPA callbacks. IRQ setup helpers allocate MSI-X vectors and program hardware vectors. `ifc_vdpa_ops` implements vDPA operations over `ifcvf_base.c`. `ifcvf_vdpa_dev_add()` allocates/registers the `vdpa_device` and applies provisioned features. `ifcvf_probe()` enables PCI, maps BARs 0/2/4, initializes hardware, reads features/config size, sets the mgmt id table, and registers `vdpa_mgmt_dev`.

Control flow: PCI probe creates a management device, not an immediate vDPA dataplane device. `dev_add` allocates the adapter, validates requested features against hardware, stores provisioned features, names the vDPA device, and registers it. Status transition to `DRIVER_OK` requests IRQs; reset stops callbacks, frees IRQs if needed, and resets hardware. Queue operations directly call low-level helpers.

State and persistence: `ifcvf_vdpa_mgmt_dev` owns the hardware object and current adapter. `ifcvf_adapter` owns the registered vDPA device. IRQ allocation mode is stored in `msix_vector_status`; callbacks live in vring/config callback fields.

Dependencies and integration: Linux PCI managed resources, DMA mask setup, vDPA mgmt API, modern virtio PCI register helpers, net/block virtio IDs, and MSI-X.

Risks: `ifcvf_vdpa_dev_add()` returns `-EINVAL` after adapter allocation on unsupported provisioned features without explicitly putting the allocated device in that branch. IRQ fallback to shared vectors reduces `get_vq_irq()` support because shared vq IRQ returns `-EINVAL`. No `set_map()` implementation because hardware lacks on-chip IOMMU.

Test signals: probe/remove for supported IDs, mgmt dev add/del, feature provisioning mask validation, per-vq versus shared IRQ modes, DRIVER_OK transitions, reset, queue state migration, and vq notification area reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/Makefile

Purpose: kbuild composition for mlx5 vDPA support.

Important APIs/types/functions: adds the core include path and builds `mlx5_vdpa.o` for `CONFIG_MLX5_VDPA_NET` from `net/mlx5_vnet.o`, `core/resources.o`, `core/mr.o`, and `net/debug.o`.

Control flow: a single module/object contains network vDPA logic, shared resource commands, memory registration, and debugfs support.

State and persistence: build-only file.

Dependencies and integration: depends on top-level vDPA Makefile and Kconfig selecting `MLX5_VDPA`/`MLX5_VDPA_NET`; shares core headers through `subdir-ccflags-y`.

Risks: feature additions split into new files must update the composite object list. Core code is compiled only through the net driver here.

Test signals: module build with `MLX5_VDPA_NET=m/y`, include path resolution for `mlx5_vdpa.h`, and link coverage for resource/MR/debug functions referenced by vnet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mlx5_vdpa.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mlx5_vdpa.h

Purpose: shared mlx5 vDPA core declarations for resource ownership, memory registration, control virtqueue state, async commands, and logging.

Important APIs/types/functions: defines `mlx5_vdpa_direct_mr`, `mlx5_vdpa_mr`, `mlx5_vdpa_resources`, `mlx5_control_vq`, `mlx5_vdpa_mr_resources`, `mlx5_vdpa_dev`, and `mlx5_vdpa_async_cmd`. Enumerates vq groups/asids. Declares resource commands, MR lifecycle/update APIs, CVQ IOTLB update, DMA MR creation/reset, and async command executor.

Control flow: no executable flow; it defines cross-file contracts used by `resources.c`, `mr.c`, and `mlx5_vnet.c`.

State and persistence: central in-memory state includes hardware resources (`pdn`, UAR, kick BAR mapping, uid, null mkey), feature/status/generation, MR arrays/refcounts/deferred-GC lists, CVQ vringh/IOTLB state, workqueues, and async command context.

Dependencies and integration: depends on mlx5 core, vDPA, vringh, vhost IOTLB, and Ethernet constants. Logging macros include function, line, and pid for kernel diagnostics.

Risks: group-to-ASID mapping and MR refcounting must stay synchronized with vnet operations. Header is broad, so structure layout changes affect all mlx5 vDPA files.

Test signals: compile all mlx5 vDPA objects, validate every declared function has implementation, and exercise MR/CVQ/resource lifetimes through vDPA add/reset/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mlx5_vdpa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mr.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mr.c

Purpose: mlx5 vDPA memory registration layer. It converts vhost IOTLB maps or DMA passthrough into mlx5 memory keys used by firmware virtqueues and control VQ translation.

Important APIs/types/functions: direct-MR helpers populate MTTs and create/destroy MTT mkeys asynchronously. `create_user_mr()` merges contiguous IOTLB ranges by permission, creates direct keys capped by KLM size, inserts null-key gaps, and creates an indirect KLM mkey. `create_dma_mr()` builds a physical-address mkey. `mlx5_vdpa_create_mr()`, `mlx5_vdpa_update_mr()`, `mlx5_vdpa_get_mr()`, and `mlx5_vdpa_put_mr()` manage lifetime. `mlx5_vdpa_update_cvq_iotlb()` mirrors maps into `vringh` IOTLB. `mlx5_vdpa_init_mr_resources()` and destroy set up delayed GC.

Control flow: set-map callers create a new MR, then update the ASID slot. Old MRs are refcount-dropped and moved to a GC list when no virtqueue references remain. GC runs after a delay to avoid blocking rapid `.set_map()` calls. Reset clears ASID slots and optionally recreates DMA MR for devices supporting `umem_uid_0`.

State and persistence: `mlx5_vdpa_mr` tracks mkey, direct children, IOTLB copy, user/DMA mode, refcount, and list membership. Direct children hold SG tables and DMA mappings. `mres` owns current ASID MRs, group mapping, active list, GC list, lock, workqueue, and shutdown flag.

Dependencies and integration: used by `mlx5_vnet.c` for `.set_map`, `.reset_map`, vq mkey updates, and CVQ vringh translation. Depends on mlx5 mkey commands, DMA mapping, scatterlists, vhost IOTLB, GCD/page sizing, and async command batching from `resources.c`.

Risks: physical addresses are converted with `pfn_to_page(__phys_to_pfn(pa))`, so IOTLB maps must represent normal memory. Error cleanup in `add_direct_chain()` walks `mr->head`, while newly built entries are first stored in a temporary list; cleanup of partially built temp entries is a point to audit. Delayed destruction means resource removal must flush GC and expose leaks.

Test signals: empty map, DMA MR fallback, multi-range IOTLB with holes and permission changes, rapid map replacement while queues hold references, CVQ ASID remap, reset with `VDPA_RESET_F_CLEAN_MAP`, and injected mkey/DMA-map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/resources.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/resources.c

Purpose: shared mlx5 vDPA hardware resource and command utility layer. It allocates protection/doorbell resources, wraps create/destroy commands for TIS/RQT/TIR/TD/mkeys, initializes the control VQ IOTLB, and batches async commands.

Important APIs/types/functions: `mlx5_vdpa_alloc_resources()` allocates UAR, optional user context, PD, null mkey, maps the kick BAR page, and initializes CVQ `vringh` IOTLB. `mlx5_vdpa_free_resources()` releases those in reverse. Command wrappers create/destroy TIS, RQT, TIR, transport domains, and mkeys with the vDPA UID. `mlx5_vdpa_exec_async_cmds()` issues arrays of mlx5 commands using async callbacks with fallback when throttled.

Control flow: allocation validates `res->valid`, obtains resources stepwise, and unwinds on each failure. Async command execution initializes completions, issues until all submitted or error, waits for outstanding completions, and records per-command completion errors.

State and persistence: `mlx5_vdpa_resources` stores PD number, UAR, kick MMIO mapping/physical address, UID, null mkey, and valid flag. CVQ owns a vhost IOTLB and lock. Async command structs carry input/output buffers, completion, and result.

Dependencies and integration: consumed by mlx5 vnet and MR code. Uses mlx5 core command API, HCA capabilities, UAR pages, ioremap, vhost IOTLB, vringh, and async command context.

Risks: resource allocation order is strict; missing unwind can leak UAR/PD/uctx mappings. `create_uctx()` returns success without setting UID when `umem_uid_0` is supported, relying on UID 0 semantics. Async throttling falls back to synchronous command execution only in the external-throttle case.

Test signals: allocation/free under all failure injection points, devices with/without `umem_uid_0`, kick BAR mapping, CVQ IOTLB allocation, async batches larger than firmware command capacity, and destroy after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/debug.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/debug.c

Purpose: debugfs support for mlx5 vDPA net devices, exposing TIR/RX flow-table identifiers and optional steering counters.

Important APIs/types/functions: `mlx5_vdpa_add_debugfs()` creates a per-vDPA debugfs dir under the mlx5 device root and an `rx` child. `mlx5_vdpa_add_tirn()`/remove expose `tirn`; `mlx5_vdpa_add_rx_flow_table()`/remove expose RX table id. Under `CONFIG_MLX5_VDPA_STEERING_DEBUG`, counter files expose packets/bytes from `mlx5_fc_query()` for unicast and multicast rules.

Control flow: vnet setup creates debugfs early, then adds flow table and TIR entries when those resources exist. Teardown removes the same dentries. Counter nodes are created per MAC/VLAN steering node and recursively removed with the node.

State and persistence: debugfs dentries are cached in `mlx5_vdpa_net`, resource structs, and `macvlan_node` counters. Values are live hardware queries; no persistence.

Dependencies and integration: called from `mlx5_vnet.c` setup/teardown and steering rule management. Depends on debugfs, mlx5 flow counters, and mlx5 device debugfs root.

Risks: debugfs creation failures are mostly tolerated, so callers must not assume dentries exist. Counter creation has partial-failure paths where one child may be missing.

Test signals: debugfs tree after vDPA add, TIR/table files after setup, counter files with steering debug enabled, hot remove cleanup, and counter query error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.c

Purpose: full mlx5 virtio-net vDPA implementation. It registers an auxiliary mlx5 vnet management device, provisions vDPA net devices, manages virtqueues in firmware, handles control virtqueue commands, RX steering, memory map changes, suspend/resume, reset, notifications, stats, and lifecycle.

Important APIs/types/functions: `struct mlx5_vdpa_net` extends `mlx5_vdpa_dev` with net config, virtqueues, event callbacks, resource lock, steering tables, IRQ pool, CVQ work, and UMEM parameters. Virtqueue setup spans CQ/QP/UMEM/counter/MSI-X allocation, `create_virtqueue()`, `modify_virtqueues()`, suspend/resume/query, and teardown. CVQ handling uses `vringh` in `mlx5_cvq_kick_handler()` for MAC, MQ, and VLAN commands. `mlx5_vdpa_ops` implements the vDPA config interface. `mlx5_vdpa_dev_add()` provisions and registers a device; `mlx5v_probe()` registers the mgmt device on the auxiliary bus.

Control flow: auxiliary probe registers a `vdpa_mgmt_dev` with supported features. `dev_add` validates minimum `VERSION_1` and `ACCESS_PLATFORM`, queue capacity, MAC/MTU features, allocates `mlx5_vdpa_net`, initializes resources/MR/fixed transport resources/workqueue, registers vDPA, then sets up initial non-ready vq resources. When guest sets `DRIVER_OK`, status handling initializes CVQ vring, registers link notifier, resumes existing queues or fully sets resources. Kicks either queue CVQ work or write the queue index to the kick BAR. Map changes suspend queues, swap MR, mark mkey fields dirty, optionally teardown/rebuild queues, then resume.

State and persistence: persistent runtime state includes negotiated `actual_features`, exposed `mlx_features`, status/generation/suspended flags, `cur_num_vqs`, per-vq addresses/readiness/indexes/fw state/modified fields/MR refs/MSI maps, net config (MAC/MTU/status), steering hash table, IRQ pool, resource setup flags, and CVQ descriptor counters. State is protected mainly by `reslock`, MR mutexes, and CVQ IOTLB spinlock.

Dependencies and integration: uses mlx5 core commands, auxiliary bus, vDPA mgmt/core, vhost IOTLB, vringh, PCI MSI-X dynamic allocation, mlx5 flow steering/MPFS/vport notifier, debugfs helpers, and core resource/MR files. Exposes vendor stats through netlink attributes.

Risks: the file has many cross-state transitions; queue resources can be initialized while not ready, ready while suspended, or torn down for feature/map changes. Control VQ parsing is serialized with `reslock` but requeues one descriptor at a time. Feature dependencies are security-relevant: MQ without CTRL_VQ is rejected to protect index assumptions. Error paths in `dev_add` rely on `put_device()` invoking `.free` for cleanup of partially initialized resources.

Test signals: mgmt add/delete, feature provisioning validation, DRIVER_OK setup, reset with and without `VDPA_RESET_F_CLEAN_MAP`, set_map/reset_map while queues run, CVQ MAC/MQ/VLAN commands, link notifier updates, suspend/resume, MSI-X and QP notification modes, multiqueue RQT resize, vendor stats, and teardown after partial setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.h

Purpose: mlx5 vDPA net-private declarations shared between the main vnet implementation and debugfs support.

Important APIs/types/functions: conversion macros `to_mlx5_vdpa_ndev()` and `to_mvdev()`, `struct mlx5_vdpa_net_resources`, IRQ pool structures, `struct mlx5_vdpa_net`, steering counter structures, `struct macvlan_node`, `key2vid()`, and debugfs helper prototypes. Inline no-op counter helpers are provided when steering debug is disabled.

Control flow: no executable control flow except `key2vid()` and compile-time selection of counter helper implementations.

State and persistence: defines all net-level state fields: TIS/TD/TIR/RQT identifiers, config, vq/callback arrays, `reslock`, flow table dentries, setup flags, current queue count, link notifier, CVQ work item, MAC/VLAN hash, IRQ pool, debugfs dentry, and UMEM sizing parameters.

Dependencies and integration: included by `mlx5_vnet.c` and `debug.c`; depends on core `mlx5_vdpa.h`.

Risks: the header centralizes state used across resource, steering, and debugfs code; mismatched cleanup of dentries or IRQ entries can leave stale pointers. Hash size and key packing must align with MAC/VLAN operations.

Test signals: compile with and without `CONFIG_MLX5_VDPA_STEERING_DEBUG`, debugfs operations using header structs, and MAC/VLAN lookup behavior for tagged/untagged keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/Makefile

Purpose: kbuild composition for Marvell Octeon endpoint vDPA.

Important APIs/types/functions: `obj-$(CONFIG_OCTEONEP_VDPA) += octep_vdpa.o`; composite object includes `octep_vdpa_main.o` and `octep_vdpa_hw.o`.

Control flow: builds Octeon vDPA only when the module-only Kconfig symbol is enabled.

State and persistence: build-only file.

Dependencies and integration: reached from top-level vDPA Makefile; Kconfig requires PCI MSI and module build.

Risks: adding implementation files requires updating the composite list. Kconfig notes the module cannot be loaded until Octeon emulation software is running.

Test signals: module build with `CONFIG_OCTEONEP_VDPA=m` and link coverage for main/hardware objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa.h

Purpose: shared Marvell Octeon endpoint vDPA definitions for PCI IDs, BAR layout, mailbox/capability registers, hardware state, queue state, and hardware-helper prototypes.

Important APIs/types/functions: defines Octeon PF/VF device IDs, mailbox/caps BAR indices, readiness signatures, mailbox register macros, device lifecycle enum, `struct octep_vring_info`, vendor capability data layout, and `struct octep_hw`. Declares status/reset, queue select/notify/address/size/ready/state, config read, capability read, feature get/set, and feature verification helpers.

Control flow: no implementation here; it establishes the contract between Octeon main and hardware files.

State and persistence: `struct octep_hw` stores PCI device, BAR mappings, common/device/isr/notify regions, per-vq info, config callback, features, queue count, config size, IRQ list, and virtio device id. Runtime persistence is in memory for the PCI device lifetime.

Dependencies and integration: includes PCI, vDPA, modern virtio-pci, virtio net/block/crypto/config, and uapi vDPA headers. Intended for `octep_vdpa_main.c` and `octep_vdpa_hw.c` named by the Makefile.

Risks: readiness depends on firmware/emulation signatures and BAR initialization. Register macros encode PF/VF mailbox addressing; incorrect function type or ring index can target wrong offsets. The header supports several virtio device classes, so config sizing and feature verification in implementation must be device-id aware.

Test signals: compile main/hw users, probe against supported PF/VF IDs, firmware-ready polling, capability parsing, queue notify/state operations, feature verification, and IRQ callback delivery through `octep_vring_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa.h -->
