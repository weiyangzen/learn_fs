# sources/distributed-fs/ceph-client/include/uapi/linux/media.h

Purpose: defines the Linux Media Controller userspace ABI for device information, entity/pad/link enumeration, link setup, topology dumps, request allocation, and request queue/reinit operations.

Important APIs and types: `struct media_device_info`, entity function constants `MEDIA_ENT_F_*`, entity flags, `struct media_entity_desc`, pad/link flags, `struct media_pad_desc`, `struct media_link_desc`, `struct media_links_enum`, interface type constants, v2 packed topology structs (`media_v2_entity`, `media_v2_interface`, `media_v2_pad`, `media_v2_link`, `media_v2_topology`), and ioctls `MEDIA_IOC_DEVICE_INFO`, `MEDIA_IOC_ENUM_ENTITIES`, `MEDIA_IOC_ENUM_LINKS`, `MEDIA_IOC_SETUP_LINK`, `MEDIA_IOC_G_TOPOLOGY`, and `MEDIA_IOC_REQUEST_ALLOC`. Request fds support `MEDIA_REQUEST_IOC_QUEUE` and `MEDIA_REQUEST_IOC_REINIT`.

Control flow: userspace queries media device info, enumerates entities/pads/links or requests a full v2 topology, enables/disables mutable links, allocates request fds for atomic per-frame controls/buffers, queues requests, and reinitializes them for reuse.

State and persistence: runtime media graph state includes registered entities, interfaces, pads, links, link flags, topology version, and request objects. No persistent state is stored here. Legacy symbols remain to avoid userspace build breakage and should not drive new topology logic.

Dependencies and integration points: depends on `linux/ioctl.h` and `linux/types.h`; integrates V4L2, DVB, ALSA-adjacent media graphs, camera pipelines, ISPs, encoders/decoders, connectors, devnodes, media-ctl, libcamera, and request API users.

Risks and test signals: risks include packed v2 layout changes, pointer-sized userspace fields, topology version races, legacy entity type confusion, link flag misuse, and request lifecycle bugs. Test topology enumeration with changing graphs, link setup validation, media request allocate/queue/reinit, 32-bit userspace compatibility, and legacy ioctl behavior.
