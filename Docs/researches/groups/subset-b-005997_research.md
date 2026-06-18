# Research: subset-b-005997

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_i2c.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_i2c.h

Purpose: defines the UAPI wire format for a virtio I2C adapter device, including message headers, feature negotiation, message flags, and backend status codes.

Important APIs and types: `VIRTIO_I2C_F_ZERO_LENGTH_REQUEST` advertises zero-length transfer support. `VIRTIO_I2C_FLAGS_FAIL_NEXT` groups requests with failure propagation, and `VIRTIO_I2C_FLAGS_M_RD` marks read transfers. `struct virtio_i2c_out_hdr` carries target address and flags; `struct virtio_i2c_in_hdr` carries `VIRTIO_I2C_MSG_OK` or `VIRTIO_I2C_MSG_ERR`.

Control flow, state, and persistence: guests enqueue one or more OUT headers and payload buffers and receive an IN status after host processing. The header stores no persistent state; device-visible state is transfer-local.

Dependencies and integration points: depends on Linux fixed-width and endian types, and integrates with virtio core and kernel I2C adapter emulation.

Risks and test signals: risks are flag misinterpretation, address endian bugs, and incorrect handling of grouped failures or zero-length transfers. Test read/write transfers, grouped multi-message transactions, NACK/error propagation, and feature-disabled zero-length requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ids.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ids.h

Purpose: assigns stable virtio device IDs and transitional PCI IDs used by drivers, devices, hypervisors, and userspace implementations to identify virtio device classes.

Important APIs and types: `VIRTIO_ID_*` constants cover network, block, console, rng, balloon, SCSI, 9p, GPU, input, vsock, crypto, IOMMU, memory, sound, filesystem, pmem, SCMI, I2C, watchdog, GPIO, SPI, and other virtio classes. `VIRTIO_TRANS_ID_*` defines legacy transitional PCI device IDs.

Control flow, state, and persistence: there is no runtime flow or state; IDs are consumed during device enumeration and driver matching.

Dependencies and integration points: included by virtio device-specific UAPI headers, PCI/MMIO transports, QEMU/vhost-style devices, and kernel module alias generation.

Risks and test signals: ID reuse or mismatch can bind the wrong driver or break userspace device emulation. Test with compile-time include users, module alias generation, virtio bus enumeration, and compatibility against the virtio specification registry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_input.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_input.h

Purpose: defines the virtio input device UAPI used to expose keyboard, pointer, tablet, touchscreen, and other input devices through virtio queues and config-space selectors.

Important APIs and types: `enum virtio_input_config_select` selects name, serial, device IDs, property bits, event bits, and absolute-axis information. `struct virtio_input_absinfo`, `struct virtio_input_devids`, and `struct virtio_input_config` describe device capabilities. `struct virtio_input_event` mirrors Linux input events with type, code, and value fields.

Control flow, state, and persistence: drivers select config categories and subselectors to enumerate capabilities, then consume event queue entries. The header defines no persistent storage; device state is event stream and negotiated config.

Dependencies and integration points: depends on Linux integer types and integrates with virtio input drivers and the Linux input subsystem event model.

Risks and test signals: risks include bitmap sizing, endian conversion, invalid `size`, and absinfo mismatch with evdev expectations. Test device ID reads, event bitmap enumeration, absolute axes, multi-touch events, and malformed config responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_iommu.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_iommu.h

Purpose: defines virtio IOMMU configuration, request, response, probe, and fault structures for attaching endpoints to domains and mapping or unmapping IOVA ranges.

Important APIs and types: feature bits include input/domain ranges, map/unmap, bypass, probe, MMIO, and bypass config. `struct virtio_iommu_config` advertises page sizes, input range, domain range, probe size, and bypass state. Request types include `ATTACH`, `DETACH`, `MAP`, `UNMAP`, and `PROBE`; status values report OK, unsupported, invalid, range, fault, and memory errors. `struct virtio_iommu_fault` reports endpoint faults.

Control flow, state, and persistence: the guest attaches an endpoint to a domain, submits map/unmap requests, probes reserved-memory properties, and receives fault notifications. Mapping state persists in the device until detached or unmapped, but the header owns no storage.

Dependencies and integration points: integrates virtio with the kernel IOMMU subsystem, DMA API, PCI/platform endpoint enumeration, and reserved MSI/MMIO regions.

Risks and test signals: high-risk areas are inclusive range handling, page-size validation, reserved-region parsing, bypass semantics, and fault reporting. Test attach/detach, overlapping maps, unmap holes, MSI reserved memory, bypass modes, and DMA fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mem.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mem.h

Purpose: defines the virtio memory hotplug ABI for a resizable memory region whose blocks can be plugged, unplugged, queried, and requested by a host.

Important APIs and types: feature bits cover ACPI PXM node IDs, inaccessible unplugged memory, and suspend persistence. Request types are `PLUG`, `UNPLUG`, `UNPLUG_ALL`, and `STATE`, represented by `struct virtio_mem_req`. Response codes are ACK, NACK, BUSY, and ERROR with state values plugged, unplugged, or mixed. `struct virtio_mem_config` exposes block size, node, base address, region size, usable size, plugged size, and requested size.

Control flow, state, and persistence: the driver watches config changes, tries to reach `requested_size`, retries BUSY operations, and may request full unplug after reset. Plugged block state persists in device memory state and may survive suspend when negotiated.

Dependencies and integration points: depends on virtio types/config and integrates with Linux memory hotplug, NUMA, ACPI PXM, memory offlining, and crash dump rules.

Risks and test signals: risks include touching inaccessible unplugged memory, inconsistent usable-region shrink, alignment errors, and races with memory offlining. Test plug/unplug cycles, reset recovery, suspend/resume, BUSY retry, and crash dump behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mmio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mmio.h

Purpose: defines the memory-mapped register layout for virtio MMIO transport devices used primarily by platform and embedded virtual machines.

Important APIs and types: register offsets cover magic/version/device/vendor IDs, feature selection, driver feature selection, queue selection, queue size, queue ready, notifications, interrupt status/ack, status, 64-bit queue descriptor/avail/used addresses, shared memory selection, config generation, and per-device config space. Interrupt bits are `VIRTIO_MMIO_INT_VRING` and `VIRTIO_MMIO_INT_CONFIG`.

Control flow, state, and persistence: the driver validates magic/version, negotiates features, configures queues, writes queue addresses, sets status, notifies queues, and acknowledges interrupts. Registers reflect volatile transport state only.

Dependencies and integration points: consumed by virtio-mmio drivers, device tree/ACPI platform enumeration, and virtio core queue setup.

Risks and test signals: risks include offset regressions, legacy page-size/PFN handling, config generation races, and 64-bit address half ordering. Test modern and legacy devices, shared memory regions, interrupt ack, queue reset paths, and config-change reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_net.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_net.h

Purpose: defines the full virtio network device ABI: feature bits, config space, packet header formats, control virtqueue commands, RSS/hash configuration, notification coalescing, and device statistics replies.

Important APIs and types: `VIRTIO_NET_F_*` covers checksum, GSO/TSO/UFO/USO, merged receive buffers, status, control virtqueue, VLAN, MAC, multiqueue, RSS/hash, RSC, standby, speed/duplex, UDP tunnel GSO, notification coalescing, and device stats. `struct virtio_net_config` exposes MAC, status, queue pairs, MTU, speed, duplex, and RSS limits. Packet metadata is in `struct virtio_net_hdr_v1`, hash/tunnel variants, and legacy headers. Control classes configure RX mode, MAC filters, VLAN filters, announce ACK, multiqueue/RSS/hash, guest offloads, coalescing, and stats.

Control flow, state, and persistence: data queues carry packet buffers prefixed by virtio net headers; the control queue changes filtering, queue steering, offloads, and coalescing. Runtime state lives in the device and driver netdev, not in the header.

Dependencies and integration points: depends on virtio IDs/config/types and Ethernet constants; integrates with Linux netdev, ethtool offloads/stats, NAPI, XDP-adjacent receive paths, and vhost/QEMU backends.

Risks and test signals: high-risk areas are packed layout, endian conversion, variable-length RSS/hash structs, feature-gated header sizes, offload correctness, MAC/VLAN filter semantics, and stats reply parsing. Test feature matrices, checksum/GSO variants, multiqueue resize, RSS indirection, hash reports, coalescing, and legacy compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pci.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pci.h

Purpose: defines legacy and modern virtio PCI transport registers, PCI vendor capabilities, common configuration layout, and virtio admin command data structures.

Important APIs and types: legacy offsets include host/guest features, queue PFN, queue select/notify, status, ISR, MSI-X vectors, and config offset helpers. Modern capability types identify common config, notify config, ISR, device config, PCI config access, shared memory, and vendor data. `struct virtio_pci_common_cfg` and `struct virtio_pci_modern_common_cfg` hold feature selectors, queue configuration, notification data, queue reset, and admin queue info. Admin structures cover command headers/status, legacy register access, notify info, capability query/set, resource objects, device parts metadata/get/set, and device mode.

Control flow, state, and persistence: PCI enumeration discovers caps, driver negotiates features, configures queues, maps notify regions, and optionally uses admin queues for SR-IOV/member management. State is volatile PCI/device state.

Dependencies and integration points: used by virtio-pci, PCI core, MSI-X, SR-IOV, transitional devices, and user-space device models.

Risks and test signals: risks include using `sizeof` on extensible common cfg, wrong capability lengths, queue address ordering, MSI vector disable handling, and admin flexible-array parsing. Test legacy/modern/transitional devices, MSI-X on/off, queue reset, shared memory caps, and admin command error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pcidev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pcidev.h

Purpose: defines a virtio protocol for virtual PCI device operations, letting a device backend receive config, MMIO/PIO, interrupt, MSI, and PME messages.

Important APIs and types: `enum virtio_pcidev_ops` names config read/write, MMIO read/write/memset, INTx, MSI, and PME operations. `struct virtio_pcidev_msg` carries operation, BAR, size, address, and variable payload data; scalar fields are native endian while many payload values are little endian.

Control flow, state, and persistence: a frontend emits operation messages for PCI access and interrupt signaling; the backend fills read data or consumes write data. Persistent state is the emulated PCI device configuration and BAR content outside this header.

Dependencies and integration points: integrates with virtio transport, PCI emulation, interrupt routing, and hypervisor/device-model code.

Risks and test signals: risks include native-endian vs little-endian confusion, invalid access sizes, BAR bounds, and interrupt message ordering. Test config read/write widths, MMIO variable sizes, memset, INTx/MSI delivery, and PME notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pcidev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pmem.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pmem.h

Purpose: defines the virtio persistent memory ABI for exposing a persistent memory range and issuing flush requests.

Important APIs and types: `VIRTIO_PMEM_F_SHMEM_REGION` indicates that the pmem guest physical range is exposed as shared memory region 0, with `VIRTIO_PMEM_SHMEM_REGION_ID`. `struct virtio_pmem_config` carries start and size. `VIRTIO_PMEM_REQ_TYPE_FLUSH`, `struct virtio_pmem_req`, and `struct virtio_pmem_resp` define flush commands and host return status.

Control flow, state, and persistence: the guest maps the advertised range and submits flush requests to ensure persistence. Actual durable state is in the backing storage, while the header only defines command/config format.

Dependencies and integration points: depends on virtio IDs/config and integrates with Linux pmem, DAX, nvdimm-like persistence, and shared-memory virtio capability handling.

Risks and test signals: risks include incorrect flush completion semantics, range/config mismatch, and shared-memory region ID drift. Test fsync/msync durability paths, DAX mappings, shared-memory feature negotiation, and backend flush failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_pmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ring.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ring.h

Purpose: defines the split and packed virtqueue ring ABI shared by virtio drivers and devices.

Important APIs and types: descriptor flags include NEXT, WRITE, and INDIRECT; packed ring flags encode avail/used bits and event suppression. Feature bits include `VIRTIO_RING_F_INDIRECT_DESC` and `VIRTIO_RING_F_EVENT_IDX`. `struct vring_desc`, `vring_avail`, `vring_used_elem`, `vring_used`, and `struct vring` define split-ring memory layout. Helpers `vring_init()`, `vring_size()`, and `vring_need_event()` calculate layout and event decisions. Packed descriptors use `struct vring_packed_desc` and `struct vring_packed_desc_event`.

Control flow, state, and persistence: guests publish descriptor chains through avail rings, devices consume and return used elements, and both sides use index/event suppression to reduce notifications. Ring state is shared memory and volatile across device reset.

Dependencies and integration points: consumed by virtio core, vhost, KVM-backed devices, and userspace virtio implementations.

Risks and test signals: high risk lies in alignment, wraparound arithmetic, event-index logic, descriptor ownership, endian mode, and indirect descriptor validation. Test split/packed rings, 16-bit index wrap, notification suppression, indirect chains, malformed descriptors, and legacy layout sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rng.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rng.h

Purpose: provides the minimal UAPI include wrapper for virtio random number generator devices.

Important APIs and types: the header defines no RNG-specific structures or commands; it includes virtio IDs and config definitions so implementations can identify and configure `VIRTIO_ID_RNG`.

Control flow, state, and persistence: entropy bytes are transferred through virtqueues defined by the virtio core, not by this header. No persistent state is defined here.

Dependencies and integration points: integrates virtio RNG drivers with virtio device discovery, the Linux hwrng subsystem, and hypervisor entropy providers.

Risks and test signals: risks are mostly ABI absence assumptions and feature/config include drift. Test device probing, hwrng registration, entropy reads of varying sizes, backend stalls, and compile coverage with virtio config changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rtc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rtc.h

Purpose: defines the virtio RTC ABI for reading virtual clocks, cross-reading clocks with hardware counters, querying clock capabilities, and configuring alarms.

Important APIs and types: feature `VIRTIO_RTC_F_ALARM` gates alarm support. Request types include read, cross read, config, clock capability, cross capability, read alarm, set alarm, and alarm enable. Common request/response/notification headers carry message type and status. Clock types include UTC, TAI, monotonic, and smeared UTC variants; counter IDs include ARM virtual counter and x86 TSC. Unions group requestq responses and alarmq notifications.

Control flow, state, and persistence: the guest sends control/read requests and receives status plus clock/alarm data; alarm events arrive on an alarm queue. Alarm state persists in the device until changed or reset.

Dependencies and integration points: integrates with virtio core, RTC/timekeeping, clocksource calibration, and alarm/timer subsystems.

Risks and test signals: risks include time type confusion, leap smear semantics, cross-counter race handling, alarm enable flags, and status mapping. Test all request types, unsupported clocks, alarm notifications, cross reads around migration, and invalid clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scmi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scmi.h

Purpose: defines feature bits and virtqueue indexes for transporting ARM SCMI protocol messages over virtio.

Important APIs and types: `VIRTIO_SCMI_F_P2A_CHANNELS` advertises platform-to-agent notifications or delayed responses, and `VIRTIO_SCMI_F_SHARED_MEMORY` advertises statistics shared memory. Queue indexes define TX command queue, RX event queue, and maximum queue count.

Control flow, state, and persistence: SCMI commands flow on the TX queue and asynchronous events or delayed responses flow on RX when negotiated. The header owns no protocol state; SCMI agents/platform firmware maintain it.

Dependencies and integration points: depends on virtio types and integrates Linux SCMI transports, firmware protocol stacks, and virtio core.

Risks and test signals: risks include queue-index mismatch, missing notification support, and shared-memory feature drift. Test SCMI command/response, delayed responses, event delivery, stats region negotiation, and operation without P2A channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scsi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scsi.h

Purpose: defines virtio SCSI configuration, control events, command request/response formats, task management, and sense data sizing.

Important APIs and types: feature bits cover hotplug, change events, target reset, request priority, and IO alignment. `struct virtio_scsi_config` exposes queues, segment limits, target/channel/lun limits, CDB and sense sizes, and alignment. Control types include TMF, asynchronous notification, and event acknowledgments. Request structures include `virtio_scsi_cmd_req`, `virtio_scsi_cmd_req_pi`, `virtio_scsi_cmd_resp`, and task management request/response formats with status and response codes.

Control flow, state, and persistence: the guest submits SCSI CDBs and optional protection information through request queues; control queue handles TMFs and events. Device state is SCSI target/lun state and pending commands outside this header.

Dependencies and integration points: integrates virtio with the Linux SCSI midlayer, block layer, hotplug, sense handling, and hypervisor storage backends.

Risks and test signals: risks include CDB/sense length mismatch, LUN encoding, TMF response handling, PI fields, queue count limits, and event ack ordering. Test inquiry/read/write, hotplug, abort/reset TMFs, sense data truncation, multi-queue I/O, and protection information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_snd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_snd.h

Purpose: defines the virtio sound ABI for jacks, PCM streams, channel maps, mixer/control elements, events, and PCM I/O statuses.

Important APIs and types: `struct virtio_snd_config` exposes counts of jacks, streams, channel maps, and controls. Queue IDs define control, event, TX, and RX queues. Request/status codes cover jack info/remap, PCM info/set_params/prepare/release/start/stop, channel map info, control info/read/write/TLV, and event notifications. PCM definitions include feature bits, formats, rates, stream info, set parameters, transfer headers, and latency status. Control element structures define roles, value types, access rights, value unions, IEC958 data, and notify events.

Control flow, state, and persistence: control queue discovers and configures ALSA-like topology, TX/RX queues carry PCM data, and event queue reports jack, period, xrun, and control changes. Runtime mixer/stream state is device maintained.

Dependencies and integration points: integrates with ALSA PCM/control/jack/channel-map APIs and virtio core.

Risks and test signals: risks include bitmap width overflow, unsupported format/rate selection, PCM state-machine errors, period/xrun notification loss, and large control value parsing. Test stream setup/start/stop, duplex audio, jack events, mixer read/write, TLV operations, and invalid IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_snd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_spi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_spi.h

Purpose: defines the virtio SPI controller ABI for advertising controller capabilities and describing individual SPI transfers.

Important APIs and types: mode bits cover CPHA, CPOL, active-high chip select, LSB-first, and loopback. `struct virtio_spi_config` reports chip-select count, cs-change support, dual/quad/octal TX/RX widths, bits-per-word mask, supported mode functions, maximum frequency, and timing delays. `struct spi_transfer_head` describes chip select, bits per word, cs-change behavior, bus widths, mode, frequency, and delay timings. `struct spi_transfer_result` returns OK, parameter error, or transfer error.

Control flow, state, and persistence: the guest validates transfer parameters against config and submits transfer descriptors with data buffers; the device returns a per-transfer result. Bus/device state is held in the controller and attached SPI device.

Dependencies and integration points: depends on virtio config/IDs/types and integrates with Linux SPI controller APIs.

Risks and test signals: risks include invalid bus widths, unsupported mode combinations, timing-unit mistakes, chip-select toggling semantics, and result handling. Test single and multi-transfer messages, CPOL/CPHA modes, dual/quad/octal, frequency limits, and parameter rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_types.h

Purpose: defines the bitwise-tagged virtio scalar integer types used in device structures whose endian interpretation differs between legacy and modern virtio.

Important APIs and types: `__virtio16`, `__virtio32`, and `__virtio64` are bitwise typedefs over unsigned integer widths. Comments define their contract: native-endian for legacy devices and little-endian for standards-compliant devices.

Control flow, state, and persistence: no control flow or state; these types annotate wire-format fields to force explicit conversion at use sites.

Dependencies and integration points: depends on Linux fixed-width types and sparse bitwise annotations; included by virtio ring and device-specific ABI headers.

Risks and test signals: risks include silently treating virtio fields as host endian, sparse warning suppression, and mixing `__le*` with `__virtio*` in shared structs. Test with sparse, big-endian builds, legacy vs modern device negotiation, and compile users of all virtio UAPI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_vsock.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_vsock.h

Purpose: defines the virtio transport packet format and config values for AF_VSOCK communication between guests, hosts, hypervisors, and nested VMs.

Important APIs and types: feature `VIRTIO_VSOCK_F_SEQPACKET` gates sequenced packet sockets. `struct virtio_vsock_config` exposes the guest CID. `struct virtio_vsock_hdr` carries source/destination CIDs and ports, payload length, socket type, operation, flags, buffer allocation, and forward count. Operations cover request, response, reset, shutdown, read/write, credit update, and credit request. Flags mark shutdown direction and seqpacket end markers.

Control flow, state, and persistence: connections handshake with request/response/RST, payloads use RW packets, and credit fields implement flow control. Socket state lives in vsock core and transport queues.

Dependencies and integration points: included by vsockmon and virtio-vsock drivers; integrates with AF_VSOCK sockets, socket diagnostics, and hypervisor transports.

Risks and test signals: risks include credit accounting bugs, CID/port confusion, seqpacket boundary loss, reset handling, and packed layout drift. Test stream and seqpacket connect, shutdown, flow-control exhaustion, transport reset events, and packet capture decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_vsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets.h

Purpose: defines the public AF_VSOCK socket address, socket options, well-known CIDs, flags, ioctls, and zerocopy notification constants.

Important APIs and types: socket options configure stream buffer size/min/max, peer VM ID, trust, connect timeout, and kernel-endpoint nonblocking TX/RX. `VMADDR_CID_*`, `VMADDR_PORT_ANY`, and `VMADDR_FLAG_TO_HOST` define addressing. `struct sockaddr_vm` is the AF_VSOCK address layout. `IOCTL_VM_SOCKETS_GET_LOCAL_CID` reports the local CID. `SOL_VSOCK` and `VSOCK_RECVERR` identify zerocopy error-queue notifications.

Control flow, state, and persistence: userspace binds/connects AF_VSOCK sockets using `sockaddr_vm`, queries or sets socket options, and may receive zerocopy completions. Per-socket state is in the networking stack.

Dependencies and integration points: integrates with Linux sockets, virtio/vmci/hyperv vsock transports, error queues, and libc time-size compatibility.

Risks and test signals: risks include 32/64-bit timeout compatibility, address structure size, CID routing flags, and option clamping. Test bind/connect/listen, local/host/hypervisor CIDs, zerocopy completion, old/new timeout constants, and mixed arch userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets_diag.h

Purpose: defines the sock_diag request and response structures for querying open AF_VSOCK sockets.

Important APIs and types: `struct vsock_diag_req` carries family, protocol, state bitmap, reserved inode/show fields, and cookie. `struct vsock_diag_msg` returns family, socket type, state, shutdown bits, source/destination CID and port, inode, and cookie.

Control flow, state, and persistence: userspace sends a netlink sock_diag request and receives one message per matching vsock. It snapshots kernel socket state but stores no persistent data.

Dependencies and integration points: integrates AF_VSOCK with sock_diag/netlink tooling such as `ss` and diagnostics libraries.

Risks and test signals: risks include state bitmap mismatch with TCP-style socket states, reserved field validation, cookie uniqueness, and missing socket types. Test listen/connected/closed sockets, stream and datagram if supported, shutdown flags, and filtered state queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmclock-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vmclock-abi.h

Purpose: defines a shared-memory VM clock ABI that exposes counter-to-real-time calibration, migration disruption markers, clock status, leap-second hints, and generation counters to guests and optionally userspace.

Important APIs and types: `struct vmclock_abi` contains constant fields (`VMCLOCK_MAGIC`, size, version, counter ID, time type), seqcount-protected mutable fields, disruption marker, flags for TAI offset, pending disruption, error validity, monotonicity, VM generation counter, and notification support. It also carries clock status, leap-smear hint, TAI offset, leap indicator, counter period/error, paired counter/time values, and VM generation counter.

Control flow, state, and persistence: readers use `seq_count` as a seqlock to obtain coherent calibration and detect migration or snapshot events through marker changes. The mapped page is shared volatile hypervisor state.

Dependencies and integration points: designed for virtualization timekeeping, vDSO-style reads, ACPI `VMCLOCK`, and virtio-rtc alignment.

Risks and test signals: risks include seqlock memory ordering, smeared UTC misuse, signed TAI offset handling, monotonicity promises during updates, and generation counter semantics. Test coherent reads under updates, live migration, snapshot restore, TSC/ARM counter calibration, and userspace mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmclock-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmcore.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vmcore.h

Purpose: defines UAPI structures and constants for device dump notes embedded in vmcore crash dumps and hardware error type classification.

Important APIs and types: `VMCOREDD_NOTE_NAME` and `VMCOREDD_MAX_NAME_BYTES` describe device dump note naming. `struct vmcoredd_header` carries ELF note name size, descriptor size, type, fixed `LINUX` name, and a device dump name. `enum hwerr_error_type` categorizes recoverable CPU, memory, PCI, CXL, and other errors.

Control flow, state, and persistence: crash dump producers write device dump headers into vmcore notes; crash analysis tooling reads them later. Persistence is the vmcore file, not kernel runtime state.

Dependencies and integration points: integrates with kdump/vmcore, device crash dump providers, ELF note parsing, and hardware error reporting.

Risks and test signals: risks include note size mismatches, non-terminated dump names, and enum drift in user tools. Test kdump generation with device dumps, vmcore parser compatibility, maximum name length, and hardware error note consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vsockmon.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vsockmon.h

Purpose: defines the packet capture header and enums for the vsockmon AF_VSOCK monitoring device.

Important APIs and types: `struct af_vsockmon_hdr` records source/destination CIDs and ports, operation, transport type, and transport header length. Operations include unknown, connect, disconnect, control, and payload. Transport values include no-info and virtio, where the transport header is `struct virtio_vsock_hdr`.

Control flow, state, and persistence: captured records contain vsockmon header, optional transport header, and payload for payload operations. The monitor snapshots traffic; no persistent state is defined here.

Dependencies and integration points: depends on `virtio_vsock.h` and integrates with packet capture tooling, AF_PACKET-like monitoring, and vsock transport debugging.

Risks and test signals: risks include length misparsing, missing payload for non-payload ops, and transport-specific header drift. Test capture of connect/disconnect/control/payload packets, virtio header decoding, and truncated capture handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vsockmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vt.h

Purpose: defines Linux virtual terminal ioctl numbers and structures for VT switching, process-controlled release/acquire, resizing, event wait, and console state queries.

Important APIs and types: constants cover console count bounds and ioctls from `VT_OPENQRY` through `VT_GETCONSIZECSRPOS`. `struct vt_mode` configures automatic or process-controlled switching and signals. `struct vt_stat`, `vt_sizes`, `vt_consize`, `vt_event`, `vt_setactivate`, and `vt_consizecsrpos` define state, geometry, event, activation, and cursor-size payloads.

Control flow, state, and persistence: userspace queries/sets VT mode, activates or waits for consoles, acknowledges release/acquire, resizes kernel console geometry, and waits for switch/blank/unblank/resize events. VT state persists while consoles exist.

Dependencies and integration points: integrates with tty/vt console code, framebuffer/DRM console layers, session managers, and terminal emulators.

Risks and test signals: risks include signal races, historical `VT_GETSTATE` short limits, resize geometry mismatch, and event bitmask validation. Test process-controlled switching, lock/unlock switch, resize ioctls, event waits, and cursor position queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vtpm_proxy.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vtpm_proxy.h

Purpose: defines the userspace ABI for creating virtual TPM proxy devices and selecting TPM protocol/locality behavior.

Important APIs and types: `enum vtpm_proxy_flags` currently defines `VTPM_PROXY_FLAG_TPM2`. `struct vtpm_proxy_new_dev` carries input flags and output TPM number, file descriptor, major, and minor. `VTPM_PROXY_IOC_NEW_DEV` creates a proxy device. `TPM2_CC_SET_LOCALITY` and `TPM_ORD_SET_LOCALITY` define vendor-specific locality commands.

Control flow, state, and persistence: userspace issues the new-device ioctl, receives a proxy fd and device identifiers, then handles TPM command traffic through the proxy. Device state persists until fd/device teardown.

Dependencies and integration points: integrates with the TPM subsystem, container/VM TPM emulation, character devices, and ioctl userspace managers.

Risks and test signals: risks include fd lifetime leaks, TPM 1.2/2.0 flag mismatch, locality command handling, and device-number races. Test new device creation, fd closure cleanup, TPM2 flag behavior, command forwarding, and multi-device allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vtpm_proxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wait.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wait.h

Purpose: defines wait-family option flags and waitid selector constants exposed to userspace.

Important APIs and types: wait flags include `WNOHANG`, `WUNTRACED`/`WSTOPPED`, `WEXITED`, `WCONTINUED`, `WNOWAIT`, and Linux-specific `__WNOTHREAD`, `__WALL`, and `__WCLONE`. waitid selectors include `P_ALL`, `P_PID`, `P_PGID`, and `P_PIDFD`.

Control flow, state, and persistence: process-management syscalls consume these flags to decide which child state changes to report and whether to reap. No state is stored in this header.

Dependencies and integration points: used by libc, wait4/waitid syscall wrappers, pidfd APIs, and kernel exit/reaping logic.

Risks and test signals: risks include conflicting libc definitions, pidfd selector compatibility, and misuse of Linux-private flags. Test waitpid/waitid behavior for exited, stopped, continued, clone, thread-group, and pidfd children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watch_queue.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/watch_queue.h

Purpose: defines notification pipe watch queue records, filters, removal records, and key/keyring notification payloads.

Important APIs and types: `O_NOTIFICATION_PIPE` selects notification pipes via `pipe2()`. Ioctls set queue size and filters. `struct watch_notification` encodes type, subtype, length, watch ID, and type-specific info flags. Filter structures match notification types, info masks, and subtype bitmaps. Meta notifications report removal and loss. `struct key_notification` reports key instantiation, update, link/unlink, clear, revoke, invalidate, and setattr events.

Control flow, state, and persistence: userspace creates a notification pipe, sets size/filter, attaches watches through subsystem APIs, and reads records. Queue contents are transient; watched object state lives in the producing subsystem.

Dependencies and integration points: integrates pipes, keyrings, file notification-style watchers, and ioctl control.

Risks and test signals: risks include bitfield ABI layout, record length validation, filter masking, loss notification, and flexible-array bounds. Test queue sizing, filter rules, keyring events, watch removal, overflow/loss, and 32/64-bit readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watch_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watchdog.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/watchdog.h

Purpose: defines generic watchdog character-device ioctls, capability/status structures, and option/status flags.

Important APIs and types: `struct watchdog_info` reports supported options, firmware version, and identity. `WDIOC_*` ioctls get support/status/bootstatus/temp/timeouts/timeleft, set options, keepalive, and set pretimeout. `WDIOF_*` option flags report reset causes and capabilities; `WDIOS_*` status flags enable/disable card and temperature panic.

Control flow, state, and persistence: userspace opens a watchdog, queries capabilities, sets timeout/pretimeout, periodically sends keepalive, and may enable/disable or magic-close depending on driver support. Hardware timer state persists until disabled, reset, or device close semantics.

Dependencies and integration points: integrates watchdog core, platform watchdog drivers, systemd/watchdog daemons, and reboot/panic handling.

Risks and test signals: risks include ioctl direction quirks, timeout unit mismatch, magic close behavior, and pretimeout support drift. Test keepalive, timeout set/get, bootstatus, magic close, pretimeout interrupt, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireguard.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wireguard.h

Purpose: defines the generic netlink UAPI for configuring and dumping WireGuard devices, peers, and allowed IPs.

Important APIs and types: `WG_GENL_NAME`, version, and `WG_KEY_LEN` identify the family and key size. Device flags include peer replacement. Peer flags remove, replace allowed IPs, or update only. Allowed-IP flags remove entries. Attribute enums cover device ifindex/name, private/public keys, listen port, fwmark, peer nesting, peer endpoint, keepalive, handshake time, byte counters, allowed IP nesting, and protocol version. Commands are get and set device.

Control flow, state, and persistence: userspace sends netlink set/get messages with nested peers and allowed IPs; kernel updates device configuration and counters. Configuration persists in kernel netdevice state until changed or device removal.

Dependencies and integration points: auto-generated from YNL spec; integrates generic netlink, WireGuard netdevice, routing, and key management tools.

Risks and test signals: risks include nested attribute validation, accidental private-key exposure in dumps, replacement semantics, and counter width handling. Test get/set, peer replace/remove/update-only, allowed IP replace/remove, endpoint changes, and netns/device lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireguard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireless.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wireless.h

Purpose: defines legacy Wireless Extensions version 22: ioctl numbers, event IDs, wireless statistics, request payloads, scan/auth/encoding structures, capability constants, and event stream layout.

Important APIs and types: `SIOCSIW*`/`SIOCGIW*` ioctls configure name, NWID, frequency, mode, sensitivity, range, stats, spy, AP, scan, ESSID, rates, RTS, fragmentation, TX power, retry, encoding, power, WPA IEs, MLME, auth, encode-ext, and PMKSA. `IWEV*` events report drops, quality, custom data, registration, WPA IEs, MIC failures, association IEs, and PMKID candidates. Core structs include `iw_param`, `iw_point`, `iw_freq`, `iw_quality`, `iw_statistics`, `iwreq`, `iw_range`, `iw_priv_args`, and `iw_event`.

Control flow, state, and persistence: userspace issues ioctl requests through netdevs and receives rtnetlink wireless events; drivers translate them to device configuration and stats. Runtime state is wireless driver/device state, not this header.

Dependencies and integration points: integrates legacy wireless tools, net/core wireless handlers, rtnetlink `IFLA_WIRELESS`, and older 802.11 drivers predating cfg80211/nl80211.

Risks and test signals: high-risk areas are 32/64-bit pointer layout, event packing without leaking kernel memory, private ioctl argument encoding, variable-length `iw_point` buffers, and obsolete WPA fields. Test `iwconfig`/wireless-tools compatibility, scan event parsing, private ioctls, mixed-arch compat, and stats/range reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireless.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wmi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wmi.h

Purpose: defines ACPI-WMI userspace ioctl payloads for vendor WMI requests, especially Dell SMBIOS-over-WMI commands.

Important APIs and types: `struct wmi_ioctl_buffer` is a generic length-prefixed variable payload. `struct calling_interface_buffer` carries Dell command class/select plus volatile input/output registers modified through SMM. `struct dell_wmi_extensions` and `dell_wmi_smbios_buffer` wrap extended data. Whitelisted class/select constants and token constants constrain supported SMBIOS operations. `DELL_WMI_SMBIOS_CMD` is the ioctl.

Control flow, state, and persistence: userspace sends a whitelisted SMBIOS command through the WMI char device; firmware may mutate the calling buffer in SMM and returns output words/data. Hardware/firmware settings may persist depending on the command.

Dependencies and integration points: integrates with ACPI WMI bus, Dell SMBIOS WMI driver, firmware SMM interfaces, and ioctl userspace tools.

Risks and test signals: risks include SMM side effects, whitelist bypass, packed/volatile layout, variable length validation, and firmware-specific persistence. Test allowed and rejected commands, token read/write, firmware error returns, and buffer length bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wwan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wwan.h

Purpose: defines rtnetlink attributes for WWAN network device link metadata.

Important APIs and types: the enum defines `IFLA_WWAN_LINK_ID` as a u32 attribute and `IFLA_WWAN_MAX` for validation.

Control flow, state, and persistence: userspace reads or sets WWAN link attributes through rtnetlink when creating or inspecting WWAN netdevices. The header contains no runtime state; per-link state is stored in netdevice/driver structures.

Dependencies and integration points: integrates WWAN core, netlink link attributes, modem drivers, and network management tools.

Risks and test signals: risks are mainly attribute-number drift and missing validation for link IDs. Test netlink dump/newlink paths, multiple WWAN links, invalid attribute lengths, and userspace manager compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wwan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/x25.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/x25.h

Purpose: defines the Linux X.25 public socket, ioctl, facility, route, subscription, call user data, and cause/diagnostic ABI.

Important APIs and types: `SIOCX25*` ioctls get/set subscriptions, facilities, call user data, cause/diagnostic, call accept approval, and DTE facilities. `X25_QBITINCL` is a socket option. Packet size constants encode X.25 sizes. `struct x25_address`, `sockaddr_x25`, `x25_subscrip_struct`, `x25_route_struct`, `x25_facilities`, `x25_dte_facilities`, `x25_calluserdata`, `x25_causediag`, and `x25_subaddr` define control payloads.

Control flow, state, and persistence: userspace configures X.25 routes/facilities and binds/connects AF_X25 sockets with X.121 addresses; facilities affect call setup and negotiation. Routing/subscription state persists in kernel networking state.

Dependencies and integration points: integrates with AF_X25, LAPB/WAN drivers, socket ioctls, and legacy networking tools.

Risks and test signals: risks include fixed-size compatibility fields, facility negotiation masks, subaddress matching, and call user data length validation. Test bind/connect, route ioctls, facilities on/off, DTE address extensions, and cause/diagnostic reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/x25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xattr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xattr.h

Purpose: defines extended attribute operation flags, optional `xattr_args`, namespace prefixes, and standard security/system attribute names.

Important APIs and types: under libc compatibility, `XATTR_CREATE`, `XATTR_REPLACE`, and `struct xattr_args` support xattr set semantics and aligned user pointers. Namespace prefixes include OS/2, macOS, btrfs, GNU/Hurd, security, system, trusted, and user. Named security attributes include EVM, IMA, SELinux, SMACK variants, AppArmor, capabilities, and BPF LSM. POSIX ACL xattr names are defined under `system.`.

Control flow, state, and persistence: xattr syscalls use names and flags to create, replace, list, get, or remove filesystem metadata. Attribute values persist on filesystem objects subject to filesystem support.

Dependencies and integration points: integrates VFS xattr handlers, LSMs, IMA/EVM, capabilities, POSIX ACLs, and libc header compatibility.

Risks and test signals: risks include libc duplicate definitions, namespace permission mistakes, name length assumptions, and security attribute interoperability. Test setxattr flags, all namespaces, ACL/capability xattrs, LSM labels, and filesystem round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xdp_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xdp_diag.h

Purpose: defines the sock_diag interface for querying AF_XDP/XDP socket information, rings, UMEM, memory info, and statistics.

Important APIs and types: `struct xdp_diag_req` and `xdp_diag_msg` carry family/protocol, inode, show mask, and cookies. Show flags request basic info, ring config, UMEM, meminfo, and stats. Attribute enum names diagnostic attributes. `struct xdp_diag_info`, `xdp_diag_ring`, `xdp_diag_umem`, and `xdp_diag_stats` report ifindex/queue, ring entries, UMEM geometry/flags/refs, and drop/invalid/empty counters.

Control flow, state, and persistence: userspace sends sock_diag requests and receives snapshots of XDP socket state. No persistent state is defined here.

Dependencies and integration points: integrates AF_XDP sockets, sock_diag netlink, XDP zero-copy UMEM, and observability tools.

Risks and test signals: risks include stale cookie matching, UMEM refcount visibility, stats races, and optional attribute gating. Test sockets with RX/TX rings, shared UMEM, zero-copy flag, invalid descriptors, and show-mask combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xdp_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xfrm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xfrm.h

Purpose: defines the IPsec/XFRM netlink ABI for security associations, policies, algorithms, lifetimes, replay state, offload, migration, defaults, multicast groups, and IPTFS attributes.

Important APIs and types: address, ID, selector, lifetime, replay, algorithm, stats, SA, policy, acquire/expire, migration, mapping, offload, and default-policy structs form the fixed netlink payloads. Message types cover new/delete/get/update/flush SA and policy, allocate SPI, acquire/expire, AE events, report, migrate, SAD/SPD info, mapping, and default policy. Attributes include algorithms, templates, security context, replay ESN, marks, offload dev, IF ID, SA direction, NAT keepalive, per-CPU SA, and IPTFS options.

Control flow, state, and persistence: key managers configure SAs and policies over netlink; kernel XFRM applies them to packet paths and emits acquire/expire/events. State persists in XFRM SAD/SPD tables until expired, flushed, or deleted.

Dependencies and integration points: integrates netlink, IPsec transforms, LSM security contexts, crypto algorithms, route lookup, hardware offload, NAT traversal, and IKE daemons.

Risks and test signals: high-risk areas are fixed struct size ABI, flexible-array bounds for keys/replay/security contexts, endian address/SPI fields, policy direction, replay ESN, offload flags, and compatibility aliases. Test SA/policy CRUD, IPv4/IPv6, AE events, migration, offload, marks/if_id, replay windows, IPTFS attrs, and strongSwan/libreswan interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xfrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xilinx-v4l2-controls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xilinx-v4l2-controls.h

Purpose: defines private V4L2 control IDs for Xilinx video IP, especially the test pattern generator.

Important APIs and types: `V4L2_CID_XILINX_OFFSET` and `V4L2_CID_XILINX_BASE` allocate a private control range. `V4L2_CID_XILINX_TPG` and child controls configure crosshairs, moving box, color mask, stuck pixel, noise, motion, motion speed, crosshair row/column, zplate starts/speeds, box size/color, stuck-pixel threshold, and noise gain.

Control flow, state, and persistence: userspace uses V4L2 control ioctls to configure Xilinx video IP parameters; values are applied to driver/device registers and persist while the video pipeline is active.

Dependencies and integration points: depends on generic V4L2 controls and integrates with Xilinx media drivers, pipelines, and test-pattern userspace.

Risks and test signals: risks include control ID collisions, range/default mismatch, and hardware register mapping errors. Test control enumeration, set/get for every TPG control, streaming with changing patterns, and media pipeline reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xilinx-v4l2-controls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/zorro.h

Purpose: defines Amiga Zorro AutoConfig bus identifiers, ROM/config structures, helper macros, and GVP product flag handling.

Important APIs and types: `ZORRO_MANUF`, `ZORRO_PROD`, `ZORRO_EPC`, and `ZORRO_ID` encode and decode 32-bit board IDs. `zorro_id` is the public ID type. GVP masks and flags classify I/O, accelerator, SCSI, DMA, bank, and clock properties. `struct Node`, `ExpansionRom`, and `ConfigDev` mirror AutoConfig data. Type bits distinguish Zorro II and III boards, and `ZORRO_NUM_AUTO` sets the autoconfig slot count.

Control flow, state, and persistence: firmware/kernel AutoConfig reads ROMs, builds config-device records, and matches IDs against drivers. Physical board configuration persists in hardware; kernel state is bus enumeration data.

Dependencies and integration points: includes `zorro_ids.h` and integrates with m68k Amiga bus drivers and legacy expansion cards.

Risks and test signals: risks include packed big-endian layout drift, GVP extended product masking, ID macro misuse, and slot-size limits. Test ID matching, ROM parsing, Zorro II/III devices, GVP variants, and big-endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro_ids.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/zorro_ids.h

Purpose: provides the sorted public manufacturer and product ID database for Amiga Zorro expansion boards.

Important APIs and types: `ZORRO_MANUF_*` constants assign manufacturer IDs, while `ZORRO_PROD_*` constants compose full IDs through `ZORRO_ID(manuf, prod, epc)`. The list covers Commodore, GVP, Phase5, Village Tronic, Individual Computers, MacroSystem, and many other official, unofficial, and test IDs, including documented ID clashes.

Control flow, state, and persistence: no control flow or state; bus drivers and module tables use these constants to match enumerated AutoConfig boards.

Dependencies and integration points: included by `zorro.h`, kernel Zorro drivers, module alias generation, and userspace tooling that decodes board IDs.

Risks and test signals: risks include unsorted additions, duplicate/clashing IDs, misspelled macro names becoming ABI, and dependency on `ZORRO_ID` being defined by the includer. Test compile inclusion through `zorro.h`, driver ID tables, known-board matching, and duplicate-ID review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/zorro_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/amd-apml.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/amd-apml.h

Purpose: defines AMD APML sideband userspace ioctls and message payloads for mailbox, CPUID, MCA/MSR, and register-transfer protocols.

Important APIs and types: `struct apml_mbox_msg` carries mailbox command, data word, and firmware return code. `apml_cpuid_msg` and `apml_mcamsr_msg` carry packed 64-bit request/response values plus status. `apml_reg_xfer_msg` carries register address, byte data, and read/write flag. Ioctls under `SB_BASE_IOCTL_NR` are `SBRMI_IOCTL_MBOX_CMD`, `CPUID_CMD`, `MCAMSR_CMD`, and `REG_XFER_CMD`.

Control flow, state, and persistence: userspace sends ioctl messages to the APML/SBRMI device; firmware/hardware returns data and soft error codes. Register writes may alter platform state depending on address.

Dependencies and integration points: integrates AMD sideband management drivers, platform firmware, monitoring tools, and RMI/SBI mailbox protocols.

Risks and test signals: risks include packed bitfield interpretation in 64-bit messages, firmware error translation, register access authorization, and ioctl number compatibility. Test valid and invalid commands, per-thread CPUID/MSR reads, register read/write, and firmware soft-error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/amd-apml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/fastrpc.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/fastrpc.h

Purpose: defines Qualcomm FastRPC userspace ioctls and payloads for creating DSP processes, invoking remote methods, and mapping DMA/shared memory into DSP address spaces.

Important APIs and types: ioctls allocate/free DMA buffers, invoke calls, attach/create process domains, mmap/munmap legacy buffers, map/unmap memory, and query DSP capabilities. Map flags distinguish static, fd-backed, delayed, and no-CPU-map mappings. Process attributes include debug, ptrace, CRC, unsigned module, adaptive QoS, system process, and privileged mode. Payload structs include invoke args, create/static-create, DMA allocation, mmap, mem_map/unmap, and capability query.

Control flow, state, and persistence: userspace creates or attaches to a DSP process, maps buffers, invokes remote handles with argument arrays, and unmaps/frees resources. DSP process and mappings persist until explicit teardown or fd close.

Dependencies and integration points: integrates Qualcomm remoteproc/DSP services, DMA-BUF/fd passing, SMMU mappings, and userspace RPC runtimes.

Risks and test signals: high-risk areas are user pointer validation, fd lifetime, cache maintenance responsibility, secure mappings, typo-preserved ABI fields, and DSP virtual address returns. Test invoke marshalling, map/unmap variants, process creation, capability query, invalid fd/length, and secure-map access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/fastrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/mrvl_cn10k_dpi.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/mrvl_cn10k_dpi.h

Purpose: defines Marvell Octeon CN10K DPI ioctl payloads for configuring PCIe MPS/MRRS and DPI engine FIFO/outstanding-load parameters.

Important APIs and types: `DPI_MAX_ENGINES` is six. `struct dpi_mps_mrrs_cfg` carries max read request size, max payload size, and EBUS port. `struct dpi_engine_cfg` carries FIFO mask, per-engine maximum outstanding load requests, update flag, and reserved field. Ioctls `DPI_MPS_MRRS_CFG` and `DPI_ENGINE_CFG` use magic `0xB8`.

Control flow, state, and persistence: privileged userspace sends configuration ioctls to tune DPI hardware behavior. Settings persist in device registers until changed or reset.

Dependencies and integration points: integrates the CN10K DPI driver, PCIe transaction sizing, DMA engines, and platform tuning tools.

Risks and test signals: risks include invalid MPS/MRRS values, port mismatch, FIFO mask interpretation, and partial engine updates. Test ioctl validation, all engine indexes, reset defaults, performance counters, and invalid reserved fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/mrvl_cn10k_dpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/ocxl.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/ocxl.h

Purpose: defines the OpenCAPI Accelerator Function Unit userspace ABI for attach, metadata, interrupt allocation, eventfd binding, P9 wait, features, and kernel events.

Important APIs and types: event structures report XSL fault errors with address, DSISR, and count. `ocxl_ioctl_attach` carries AMR and reserved fields. `ocxl_ioctl_metadata` reports version, AFU version, PASID, per-PASID/global MMIO sizes, and reserved space. `ocxl_ioctl_p9_wait`, `ocxl_ioctl_features`, and `ocxl_ioctl_irq_fd` support waiting and interrupt setup. Ioctls allocate/free IRQs, set IRQ fd, get metadata/features, attach, and enable P9 wait.

Control flow, state, and persistence: userspace opens an AFU, attaches a context, maps MMIO, allocates IRQs, binds eventfds, reads events, and may enable P9 wait. Context and IRQ state persist until fd close or ioctl teardown.

Dependencies and integration points: integrates OpenCAPI/Power platform AFU drivers, PASID/IOMMU, eventfd, MMIO mapping, and userspace accelerator runtimes.

Risks and test signals: risks include reserved-field ABI growth, PASID lifetime, IRQ/eventfd leaks, event ordering, and fault event sizing. Test attach/detach, metadata versions, IRQ allocation/free, eventfd delivery, P9 wait, and XSL fault reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/ocxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/pvpanic.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/pvpanic.h

Purpose: defines bit flags written to a paravirtual panic device to notify the host of guest panic, crash-kernel load, or shutdown.

Important APIs and types: `PVPANIC_PANICKED`, `PVPANIC_CRASH_LOADED`, and `PVPANIC_SHUTDOWN` are bit values built with `_BITUL`.

Control flow, state, and persistence: guest kernel or userspace writes event bits to a pvpanic IO/MMIO device; the hypervisor consumes them for logging, management actions, or crash handling. No persistent state is defined by the header.

Dependencies and integration points: integrates with pvpanic platform/PCI devices, QEMU/libvirt management, crash dump workflows, and guest shutdown paths.

Risks and test signals: risks include bit assignment drift, host ignoring combined flags, and event ordering around panic/crash-kernel boot. Test panic notification, kdump loaded notification, clean shutdown notification, and hypervisor event logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/pvpanic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/hisi_qm.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/uacce/hisi_qm.h

Purpose: defines HiSilicon queue-manager UACCE ioctls and payloads for configuring queue-pair context and queue depth/element sizing.

Important APIs and types: `struct hisi_qp_ctx` returns/sets queue pair ID and accelerator algorithm type. `struct hisi_qp_info` carries SQE size, submission queue depth, completion queue depth, and reserved data. API version strings identify supported queue-manager ABIs. Ioctls `UACCE_CMD_QM_SET_QP_CTX` and `UACCE_CMD_QM_SET_QP_INFO` use magic `H`.

Control flow, state, and persistence: userspace configures a UACCE queue before starting accelerator work; queue parameters persist for that queue lifetime.

Dependencies and integration points: integrates UACCE common queue files, HiSilicon accelerator drivers, hardware queue managers, and userspace crypto/compression runtimes.

Risks and test signals: risks include incompatible API version selection, queue depth mismatch, invalid algorithm type, and reserved field handling. Test QP setup, queue start, accelerator submission/completion, version negotiation, and invalid depths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/hisi_qm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/uacce.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/uacce/uacce.h

Purpose: defines common UACCE userspace accelerator queue ioctls, device flags, and queue file mmap region types.

Important APIs and types: `UACCE_CMD_START_Q` starts a queue and `UACCE_CMD_PUT_Q` stops/frees a queue before fd close. `UACCE_DEV_SVA` indicates Shared Virtual Addressing with PASID and device page fault support. `enum uacce_qfrt` distinguishes MMIO and device-user-share mmap regions.

Control flow, state, and persistence: userspace opens a UACCE queue file, maps regions, configures device-specific state, starts the queue, submits work, and uses PUT_Q or close to release resources. Queue state persists only for the queue fd lifetime.

Dependencies and integration points: integrates UACCE core, IOMMU SVA/PASID, accelerator device drivers, mmap, and device-specific headers such as HiSilicon QM.

Risks and test signals: risks include `BIT()` include assumptions, queue lifetime races, stale mmaps after PUT_Q, and SVA fault handling. Test start/put sequencing, mmap region offsets, SVA-capable and non-SVA devices, fd close cleanup, and concurrent queue users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/uacce/uacce.h -->
