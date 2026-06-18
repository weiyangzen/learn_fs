# sources/distributed-fs/ceph-client/include/uapi/linux/udmabuf.h

Purpose: Defines the userspace DMA-BUF creation ABI for exporting memfd-backed memory as dma-buf objects.

Important APIs/types/functions: `UDMABUF_FLAGS_CLOEXEC` controls close-on-exec. `struct udmabuf_create` describes a single memfd, flags, offset, and size. `struct udmabuf_create_item` describes one segment for list creation. `struct udmabuf_create_list` carries common flags, count, and a flexible array of items. Ioctls `UDMABUF_CREATE` and `UDMABUF_CREATE_LIST` use `_IOW('u', ...)`.

Control flow: Userspace creates/seals or prepares memfd storage, opens udmabuf, and issues create ioctl. The kernel validates offsets/sizes, pins or references pages as required, and returns a dma-buf file descriptor.

State and persistence behavior: The exported dma-buf object persists while file descriptors/references exist. Underlying memfd lifetime and mutability influence sharing semantics.

Dependencies and integration points: Includes `linux/types.h` and `linux/ioctl.h`; integrates with dma-buf, memfd, GPU/display/media drivers, and cross-device buffer sharing.

Risks: Offset/size overflow, memfd seal expectations, cache coherency, lifetime management, and list-count validation are important. CLOEXEC defaults affect descriptor leakage across exec.

Test signals: Create single and multi-item buffers, test invalid offsets/sizes/counts, CLOEXEC behavior, dma-buf import by another subsystem, and 32/64-bit struct layout.
