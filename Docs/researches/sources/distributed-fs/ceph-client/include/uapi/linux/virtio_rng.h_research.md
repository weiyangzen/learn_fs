<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rng.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rng.h

Purpose: provides the minimal UAPI include wrapper for virtio random number generator devices.

Important APIs and types: the header defines no RNG-specific structures or commands; it includes virtio IDs and config definitions so implementations can identify and configure `VIRTIO_ID_RNG`.

Control flow, state, and persistence: entropy bytes are transferred through virtqueues defined by the virtio core, not by this header. No persistent state is defined here.

Dependencies and integration points: integrates virtio RNG drivers with virtio device discovery, the Linux hwrng subsystem, and hypervisor entropy providers.

Risks and test signals: risks are mostly ABI absence assumptions and feature/config include drift. Test device probing, hwrng registration, entropy reads of varying sizes, backend stalls, and compile coverage with virtio config changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rng.h -->
