# Group Research: group_1650_qemu_sources_virtualization_qemu_hw_virtio_vhost_vdpa_c_sources_vir_c4b7fc77f3bb

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/qemu`. All files listed in this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vdpa.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-vdpa.c

## Purpose
Implements the vhost-vDPA backend `VhostOps` for QEMU virtio devices, bridging generic vhost lifecycle calls to Linux vhost-vDPA ioctls and IOTLB messages. It owns vDPA-specific memory listener behavior, device status sequencing, host notifier mmap setup, and shadow virtqueue setup used for migration/logging paths.

## Key Elements
- DMA map/unmap path: `vhost_vdpa_dma_map()` and `vhost_vdpa_dma_unmap()` emit `VHOST_IOTLB_MSG_V2` update/invalidate messages to the vDPA device fd, including ASID support when available.
- Memory listener: `vhost_vdpa_listener_region_add()`, `vhost_vdpa_listener_region_del()`, and `vhost_vdpa_listener_commit()` translate QEMU RAM/IOMMU region changes into vDPA IOTLB updates, including batched begin/end messages when `VHOST_BACKEND_F_IOTLB_BATCH` is negotiated.
- IOMMU handling: `vhost_vdpa_iommu_region_add()` registers notifiers and replays mappings; `vhost_vdpa_iommu_map_notify()` maps or unmaps translated IOTLB entries against the vDPA device.
- Backend setup: `vhost_vdpa_init()` negotiates backend capabilities, initializes shadow virtqueues, blocks migration when needed, disables RAM discard, sets initial virtio status, and installs the custom memory listener.
- Shadow virtqueues: `vhost_vdpa_svqs_start()`, `vhost_vdpa_svqs_stop()`, `vhost_vdpa_svq_map_rings()`, and helper routines map SVQ driver/device areas into vDPA IOVA space and substitute SVQ kick/call fds.
- Device start/stop: `vhost_vdpa_dev_start()` initializes host notifiers and SVQs, registers the memory listener in the active DMA address space, and sets `DRIVER_OK`; stop suspends or resets and tears down SVQ/notifier state.
- Exported backend table: `vdpa_ops` wires this file into generic `vhost.c` through callbacks for feature negotiation, mem table validation, vring operations, config access, reset, IOMMU forcing, and device status.

## Dependencies
Uses Linux `vhost.h`, `vfio.h`, eventfd/ioctl/mmap APIs, QEMU memory listeners, IOMMU notifiers, `VhostShadowVirtqueue`, `VhostIOVATree`, migration blockers, RAM discard controls, and tracepoints. It depends heavily on generic vhost lifecycle contracts from `hw/virtio/vhost.h`.

## Behavior/Risks
- Only RAM or IOMMU regions are accepted; protected memory, RAM devices, MMIO, out-of-range IOVAs, and unaligned page mappings are skipped or reported.
- `shadow_data` mode allocates GPA-to-IOVA mappings and must remove partially inserted mappings on failure.
- SVQ is explicitly rejected when a virtio IOMMU is enabled, because the implementation cannot combine those modes.
- Full 64-bit unmap size is split because the unmap ioctl cannot accept a full 64-bit size.
- Many operations are first-device or last-device gated to avoid repeating shared vDPA state changes across queue-pair split devices.
- Stop prefers `VHOST_VDPA_SUSPEND` when supported; otherwise reset is used, which affects whether vring base can be trusted later.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vdpa.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vsock-common.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-vsock-common.c

## Purpose
Provides the abstract shared implementation for vhost-vsock virtio devices. It handles common feature filtering, queue creation, vhost start/stop, guest notifier masking, and migration post-load transport reset behavior.

## Key Elements
- `feature_bits` exposes `VIRTIO_VSOCK_F_SEQPACKET`, ring reset, and packed ring filtering through generic vhost feature negotiation.
- `vhost_vsock_common_get_features()` implements `seqpacket=on/off/auto` behavior and errors if forced seqpacket is unsupported.
- `vhost_vsock_common_start()` enables vhost host notifiers, binds guest notifiers through the virtio bus, starts the backend, and unmasks all vhost queues.
- `vhost_vsock_common_stop()` stops the backend, unbinds guest notifiers, and disables host notifiers.
- `vhost_vsock_common_send_transport_reset()` injects a `VIRTIO_VSOCK_EVENT_TRANSPORT_RESET` event into the event virtqueue after migration.
- `vhost_vsock_common_realize()` creates receive, transmit, and event queues, with only the event queue owned by QEMU.
- Class init marks the type abstract, exposes the `seqpacket` property, and installs guest notifier and `get_vhost` hooks.

## Dependencies
Uses `virtio_vsock.h`, `virtio-bus`, generic `vhost`, QEMU iovec helpers, monitor infrastructure, and QOM properties.

## Behavior/Risks
- Migration pre-save asserts that the vhost backend is stopped so it cannot continue writing guest memory.
- Post-load transport reset is deferred through a virtual clock timer so virtqueue changes occur after migration completes.
- Config interrupt index is explicitly ignored in guest notifier mask/pending callbacks.
- Start error paths unwind guest and host notifier setup in reverse order.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vsock-common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vsock-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-vsock-pci.c

## Purpose
Implements the PCI transport wrapper for the `TYPE_VHOST_VSOCK` virtio device.

## Key Elements
- Defines `VHostVSockPCI`, embedding a `VirtIOPCIProxy` and a `VHostVSock` child device.
- Exposes `vectors` property with default value `3`.
- `vhost_vsock_pci_realize()` forces virtio 1 for non-legacy-check-disabled configurations to avoid migration issues on newer machine types, then realizes the child on the PCI proxy bus.
- Class init sets vendor/device IDs, PCI class `PCI_CLASS_COMMUNICATION_OTHER`, revision `0`, device category `MISC`, and the realize callback.
- Registers generic and non-transitional PCI type names.

## Dependencies
Uses QEMU virtio-pci, qdev property, QOM, PCI IDs, and `vhost-vsock.h`.

## Behavior/Risks
This is transport glue; most vsock behavior is in `vhost-vsock.c` and `vhost-vsock-common.c`. The important compatibility behavior is conditional `virtio_pci_force_virtio_1()`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vsock-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vsock.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost-vsock.c

## Purpose
Implements the concrete kernel vhost-vsock virtio device, including guest CID validation, backend fd acquisition, vhost initialization, status-driven start/stop, and VMState hooks.

## Key Elements
- `vhost_vsock_get_config()` writes the guest CID into `virtio_vsock_config`.
- `vhost_vsock_set_guest_cid()` and `vhost_vsock_set_running()` call backend-specific vhost-vsock ops.
- `vhost_vsock_set_status()` starts vhost when virtio status says the device should run, then sets backend running state; stop clears running and stops common vhost state.
- `vhost_vsock_device_realize()` validates `guest-cid > 2` and 32-bit range, obtains either monitor-provided `vhostfd` or `/dev/vhost-vsock`, makes it nonblocking, realizes common queues, initializes a kernel vhost backend, and sets guest CID.
- VMState uses common pre-save and post-load callbacks to ensure backend quiescence and transport reset.
- Properties are `guest-cid` and optional `vhostfd`.

## Dependencies
Uses Linux virtio-vsock headers, QEMU socket/fd monitor helpers, qdev properties, common vhost-vsock code, and generic kernel vhost backend initialization.

## Behavior/Risks
- Reserved CIDs `0`, `1`, and `2` are rejected.
- If `qemu_set_blocking(vhostfd, false)` fails after opening `/dev/vhost-vsock`, this function returns without the later vhost cleanup path; callers should be aware of fd lifetime assumptions around early failures.
- `set_status()` logs backend start/stop failures but returns `0`, matching virtio set-status callback expectations.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost-vsock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost.c -->
# File Research: sources/virtualization/qemu/hw/virtio/vhost.c

## Purpose
Provides QEMU's generic vhost core shared by kernel, vhost-user, and vhost-vDPA backends. It manages backend selection, memory tables, dirty logging, notifier handoff, virtqueue setup/teardown, IOMMU invalidation, migration blockers, inflight buffers, and backend state transfer.

## Key Elements
- Global state tracks all vhost devices, per-backend shared dirty log buffers, and elected dirty-log scanners.
- Memory slot helpers `vhost_get_max_memslots()` and `vhost_get_free_memslots()` summarize backend memory table limits across active devices.
- Dirty logging: `vhost_dev_sync_region()`, `vhost_sync_dirty_bitmap()`, `vhost_log_get()`, `vhost_log_put()`, and `vhost_dev_log_resize()` maintain vhost dirty bitmaps and mark QEMU memory dirty during migration.
- Backend selection: `vhost_set_backend_type()` installs `kernel_ops`, `user_ops`, or `vdpa_ops` based on build-time support.
- Memory listener: `vhost_begin()`, `vhost_region_add_section()`, `vhost_region_addnop()`, and `vhost_commit()` collect RAM sections, merge compatible neighbors, rebuild `struct vhost_memory`, verify ring mappings, and update backend memory tables.
- IOMMU listener: `vhost_iommu_region_add()`, `vhost_iommu_region_del()`, and `vhost_iommu_unmap_notify()` invalidate backend IOTLB entries when translated mappings disappear.
- Virtqueue lifecycle: `vhost_virtqueue_init()`, `vhost_virtqueue_start()`, `vhost_virtqueue_stop()`, and `do_vhost_virtqueue_stop()` configure vring size/base/endian/address/kick/call fds and keep QEMU queue indices synchronized.
- Notifier handoff: `vhost_dev_enable_notifiers()` grabs ioeventfd ownership and assigns host notifiers; `vhost_dev_disable_notifiers()` reverses it.
- Device lifecycle: `vhost_dev_init()`, `vhost_dev_start()`, `vhost_dev_stop()`, `vhost_dev_force_stop()`, and `vhost_dev_cleanup()` compose backend ops, memory listeners, migration blockers, vring enable, config interrupts, logging, and IOMMU listeners.
- Migration support includes VMState descriptions for inflight buffers and `vhost_save_backend_state()` / `vhost_load_backend_state()` pipe-based backend state transfer.

## Dependencies
Uses QEMU memory API, address-space mapping, RAMBlock helpers, migration blockers and QEMUFile, memfd, virtio bus/device APIs, Linux vhost type headers, DMA/IOMMU APIs, and per-backend `VhostOps`.

## Behavior/Risks
- Memory region selection excludes ROM and unsupported dirty-log users; vhost-user may require fd-backed shared RAM and reject private memslots.
- Dirty logging uses a per-backend shared log and elects one device to scan memory sections to avoid duplicate scanning.
- Runtime memory table changes can abort on ring mapping verification failure.
- `vhost_dev_init()` rejects configurations where memory device auto-sizing assumed more memslots than the backend can support.
- vhost-user disconnects can alter state during logging setup, so migration-log code checks whether the device stopped while communicating with the backend.
- State transfer asserts the device is stopped while saving/loading backend state.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/vhost.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-9p-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-9p-pci.c

## Purpose
Implements the PCI transport wrapper for the virtio 9p filesystem device.

## Key Elements
- Defines `V9fsPCIState`, embedding `VirtIOPCIProxy` and `V9fsVirtioState`.
- `virtio_9p_pci_realize()` realizes the child `TYPE_VIRTIO_9P` device on the PCI proxy bus.
- Exposes `ioeventfd` default-on and `vectors=2` properties.
- Class init sets Red Hat virtio vendor ID, `PCI_DEVICE_ID_VIRTIO_9P`, ABI revision, storage category, and class id `0x2`.
- Registers base, generic, transitional, and non-transitional virtio-pci type names.

## Dependencies
Uses virtio-pci glue, 9p virtio device definitions, qdev properties, and QOM module registration.

## Behavior/Risks
This file is pure transport binding; 9p filesystem semantics live in the `hw/9pfs` implementation.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-9p-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-acpi.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-acpi.c

## Purpose
Builds ACPI DSDT entries for MMIO virtio devices.

## Key Elements
- `virtio_acpi_dsdt_add()` iterates `num` devices starting at `start_index`.
- For each device, creates `VR%02u` ACPI device with `_HID` `LNRO0005`, `_UID`, and `_CCA=1`.
- Creates `_CRS` containing a fixed 32-bit memory resource and a level, active-high, exclusive interrupt.
- Increments base address by `size` and IRQ by one per device.

## Dependencies
Uses QEMU AML builders from `hw/acpi/aml-build.h` and `virtio-acpi.h`.

## Behavior/Risks
Assumes consecutive MMIO windows and IRQ numbers. It emits cache-coherent devices through `_CCA=1`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-acpi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-balloon-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-balloon-pci.c

## Purpose
Implements the PCI transport wrapper for the virtio balloon device.

## Key Elements
- Defines `VirtIOBalloonPCI`, embedding `VirtIOPCIProxy` and `VirtIOBalloon`.
- Exposes default-on `ioeventfd` and `vectors` defaulting to `DEV_NVECTORS_UNSPECIFIED`.
- `virtio_balloon_pci_realize()` defaults unspecified vectors to `2`, sets PCI class code to `PCI_CLASS_OTHERS`, and realizes the child balloon device.
- Instance init creates the child `TYPE_VIRTIO_BALLOON` and adds PCI-level aliases for `guest-stats` and `guest-stats-polling-interval`.
- Registers base, generic, transitional, and non-transitional PCI type names.

## Dependencies
Uses virtio-pci, qdev property, `virtio-balloon.h`, QAPI error handling, and QOM aliases.

## Behavior/Risks
Transport-only file. The property aliases are important because management tooling can access balloon stats through the PCI device.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-balloon-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-balloon.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-balloon.c

## Purpose
Implements the virtio balloon device: inflation/deflation, guest statistics, free-page hinting, free-page reporting, page poison handling, QMP balloon target integration, reset behavior, and VMState subsections.

## Key Elements
- Inflate/deflate: `virtio_balloon_handle_output()` reads PFNs from inflate/deflate queues, validates RAM sections, and calls `balloon_inflate_page()` or `balloon_deflate_page()`.
- Page discard: `balloon_inflate_page()` discards whole host pages immediately when host page size equals virtio balloon page size, or tracks partially ballooned host pages with a bitmap until a whole host page can be discarded.
- Deflate hinting: `balloon_deflate_page()` issues `QEMU_MADV_WILLNEED` for the containing host page.
- Stats: `balloon_stat_names`, `reset_stats()`, `virtio_balloon_receive_stats()`, and QOM properties expose guest stats and polling interval, using a timer to prompt the stats virtqueue.
- Free-page reporting: `virtio_balloon_handle_report()` discards guest-reported free page ranges from writable RAM if discards are not inhibited and page poison is not active.
- Free-page hinting: `get_free_page_hints()`, `virtio_ballloon_get_free_page_hints()`, and migration notifier callbacks coordinate hinting through an IOThread and precopy migration phases.
- Config: `virtio_balloon_get_config()` and `virtio_balloon_set_config()` expose `num_pages`, `actual`, free-page command IDs, and `poison_val`, with config size depending on negotiated host features.
- Realize/unrealize: `virtio_balloon_device_realize()` registers the global balloon handler, creates queues, validates that free-page hinting has an IOThread, installs migration notifier/BH as needed, and registers resettable state.
- VMState: saves `num_pages`, `actual`, and optional free-page-hint/page-poison subsections.

## Dependencies
Uses QEMU virtio core/accessors, RAMBlock discard APIs, memory-region lookup, QAPI balloon events, migration notifiers, reset framework, IOThread/AIO BHs, timers, QOM properties, and machine memory sizing.

## Behavior/Risks
- Ballooning is inhibited when RAM discard is disabled, incoming postcopy is active, or background snapshotting is active.
- Free-page hinting is skipped when postcopy RAM is possible because hinted pages are removed from the dirty bitmap.
- Backing page sizes larger than 4 KiB are warned as potentially unreliable and require partial-page tracking.
- Only one balloon handler is supported.
- `free-page-hint` requires an `iothread`; realization fails otherwise.
- Reset stops free-page hinting and returns any saved stats queue element; wakeup reset intentionally preserves stats.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-balloon.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-blk-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-blk-pci.c

## Purpose
Implements the PCI transport wrapper for the virtio block device.

## Key Elements
- Defines `VirtIOBlkPCI`, embedding `VirtIOPCIProxy` and `VirtIOBlock`.
- Exposes `class`, default-on `ioeventfd`, and `vectors` properties.
- `virtio_blk_pci_realize()` chooses an optimal queue count when `num_queues` is automatic and defaults MSI-X vectors to `num_queues + 1`.
- Class init marks the device as storage, installs PCI-specific qdev property handling, sets Red Hat virtio block PCI IDs, ABI revision, and default class `PCI_CLASS_STORAGE_SCSI`.
- Instance init creates the child `TYPE_VIRTIO_BLK` and aliases `bootindex`.
- Registers base, generic, transitional, and non-transitional virtio-pci type names.

## Dependencies
Uses virtio-pci, virtio-blk config, qdev PCI property helpers, and QOM.

## Behavior/Risks
This is transport glue; queue count and vector defaults affect guest-visible interrupt layout and migration compatibility.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-blk-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-bus.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-bus.c

## Purpose
Implements the abstract virtio bus support layer used by transports. It coordinates device plug/unplug, feature discovery, config forwarding, ioeventfd ownership, host notifier setup, firmware path delegation, and IOMMU checks.

## Key Elements
- `virtio_bus_device_plugged()` calls transport pre-plug hooks, obtains device features through `get_features_ex` or legacy `get_features`, invokes transport `device_plugged`, and sets DMA address space/IOMMU feature state.
- `virtio_bus_reset()` stops ioeventfd and resets the attached virtio device.
- Config helpers forward get/set config, bad-features, device id, and config length requests to the attached `VirtIODevice`.
- `virtio_bus_grab_ioeventfd()` and `virtio_bus_release_ioeventfd()` implement shared ownership so vhost can temporarily take ioeventfd control.
- `virtio_bus_start_ioeventfd()` and `virtio_bus_stop_ioeventfd()` delegate to device `start_ioeventfd`/`stop_ioeventfd` when the transport supports assignment and ownership is not grabbed.
- `virtio_bus_set_host_notifier()` initializes/assigns/unassigns host notifiers and updates virtqueue notifier enabled state.
- `virtio_bus_cleanup_host_notifier()` drains and destroys an event notifier after assignment is removed.
- Class init delegates device paths to the parent proxy.

## Dependencies
Uses QEMU virtio device APIs, address-space globals, qdev bus infrastructure, event notifiers, and transport callbacks supplied by `VirtioBusClass`.

## Behavior/Risks
- IOMMU platform handling fails plug when the transport DMA address space is not system memory and the device did not retain `VIRTIO_F_IOMMU_PLATFORM`.
- `ioeventfd_started` is preserved when grabbed so release can restart ioeventfd.
- Host notifier cleanup must happen after assignment is disabled and pending events are drained.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-bus.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-config-io.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-config-io.c

## Purpose
Provides byte/word/dword config-space read/write helpers for legacy and modern virtio config access.

## Key Elements
- Legacy helpers `virtio_config_readb/readw/readl()` bounds-check, refresh config via `get_config`, and load using host-endian unaligned helpers.
- Legacy write helpers store byte/word/dword into `vdev->config` and call `set_config` if implemented.
- Modern helpers mirror the same behavior but use little-endian accessors for 16-bit and 32-bit values.
- Out-of-range reads return `(uint32_t)-1`; out-of-range writes are ignored.

## Dependencies
Uses `hw/virtio/virtio.h` and QEMU unaligned load/store helpers.

## Behavior/Risks
The split between legacy host-endian and modern little-endian helpers is guest ABI visible. Callers rely on the simple bounds behavior for config-space holes or short accesses.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-config-io.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-crypto-pci.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-crypto-pci.c

## Purpose
Implements the PCI transport wrapper for virtio-crypto.

## Key Elements
- Defines `VirtIOCryptoPCI`, embedding `VirtIOPCIProxy` and `VirtIOCrypto`.
- Exposes default-on `ioeventfd` and `vectors=2`.
- `virtio_crypto_pci_realize()` requires a valid `cryptodev` link before realizing the child device and forces virtio 1.0.
- Class init sets device category `MISC`, PCI class `PCI_CLASS_OTHERS`, and the realize callback.
- Registers `virtio-crypto-pci` through virtio-pci type registration.

## Dependencies
Uses virtio-pci, `virtio-crypto.h`, qdev properties, QOM, and QAPI errors.

## Behavior/Risks
Virtio-crypto is modern-only here through `virtio_pci_force_virtio_1()`. Missing `cryptodev` is a realization error.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-crypto-pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-crypto.c -->
# File Research: sources/virtualization/qemu/hw/virtio/virtio-crypto.c

## Purpose
Implements the virtio-crypto device model backed by QEMU `cryptodev` backends, with control queue session management, data queue crypto operations, optional vhost-crypto acceleration, config reporting, and unmigratable VMState.

## Key Elements
- Session management: `virtio_crypto_handle_ctrl()` parses control queue requests, supports symmetric cipher/chaining session creation, RSA akcipher session creation, and destroy-session requests.
- Session helpers allocate and validate cipher keys, auth keys, and asymmetric keys against backend-advertised limits before calling `cryptodev_backend_create_session()` or close-session APIs.
- Completion callbacks `virtio_crypto_create_session_completion()` and `virtio_crypto_destroy_session_completion()` write virtio status/session IDs back to guest buffers and notify the queue.
- Data request parsing: `virtio_crypto_handle_request()` copies in/out iovecs, validates headers, locates the trailing input header, parses opcodes, and builds `CryptoDevBackendOpInfo`.
- Symmetric operations: `virtio_crypto_sym_op_helper()` validates lengths, bounds total data by `max_size`, lays out IV/AAD/src/dst/digest buffers in one allocation, and captures guest input data.
- Asymmetric operations: `virtio_crypto_handle_asym_req()` handles akcipher src/dst buffers and verify-specific destination input.
- Completion: `virtio_crypto_req_complete()` copies result data/digest or akcipher output into guest iovecs, writes status, pushes the used element, and frees request state.
- Queue scheduling: data queues run through guarded BHs that disable notification while draining and re-enable it after the queue becomes empty.
- Realize/unrealize: validates an unused `cryptodev`, sets `max_queues`, creates data queues plus a control queue, initializes backend-derived config fields, marks the backend used, and clears it on unrealize.
- Vhost path: `virtio_crypto_set_status()` starts/stops vhost crypto when the guest is ready, hardware is ready, and the VM is running; notifier mask/pending callbacks forward to cryptodev-vhost helpers.
- Config path reports status, queue count, service bitmaps, algorithm bitmaps, key limits, and max request size as little-endian virtio 1.0 config.

## Dependencies
Uses virtio core, iovec helpers, guarded BHs, `cryptodev` backend APIs, `cryptodev-vhost`, Linux virtio crypto headers via `virtio-crypto.h`, QOM properties, and QAPI errors.

## Behavior/Risks
- VMState is marked unmigratable.
- Only cipher, algorithm chaining, and RSA akcipher paths are implemented; hash, MAC, AEAD, DSA, and ECDSA paths are unsupported or TODO.
- Serious parse/buffer errors detach the virtqueue element and can require device reset.
- Request buffers containing key/data material are zeroized for symmetric operation info before free, but asymmetric source/destination buffers are simply freed.
- Backend ownership is exclusive; realization fails if the cryptodev backend is already used.
- Vhost start failures fall back to userspace virtio crypto.
<!-- END FILE RESEARCH: sources/virtualization/qemu/hw/virtio/virtio-crypto.c -->