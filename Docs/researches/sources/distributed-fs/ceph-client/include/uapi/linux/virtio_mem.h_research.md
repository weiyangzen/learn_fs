<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mem.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mem.h

Purpose: defines the virtio memory hotplug ABI for a resizable memory region whose blocks can be plugged, unplugged, queried, and requested by a host.

Important APIs and types: feature bits cover ACPI PXM node IDs, inaccessible unplugged memory, and suspend persistence. Request types are `PLUG`, `UNPLUG`, `UNPLUG_ALL`, and `STATE`, represented by `struct virtio_mem_req`. Response codes are ACK, NACK, BUSY, and ERROR with state values plugged, unplugged, or mixed. `struct virtio_mem_config` exposes block size, node, base address, region size, usable size, plugged size, and requested size.

Control flow, state, and persistence: the driver watches config changes, tries to reach `requested_size`, retries BUSY operations, and may request full unplug after reset. Plugged block state persists in device memory state and may survive suspend when negotiated.

Dependencies and integration points: depends on virtio types/config and integrates with Linux memory hotplug, NUMA, ACPI PXM, memory offlining, and crash dump rules.

Risks and test signals: risks include touching inaccessible unplugged memory, inconsistent usable-region shrink, alignment errors, and races with memory offlining. Test plug/unplug cycles, reset recovery, suspend/resume, BUSY retry, and crash dump behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_mem.h -->
