# sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.h

Purpose: declares the gntdev dma-buf extension interface used by `gntdev.c` when `CONFIG_XEN_GNTDEV_DMABUF` is enabled.

Important APIs/functions: declares `gntdev_dmabuf_init`, `gntdev_dmabuf_fini`, and the four dma-buf IOCTL dispatch helpers for export-from-refs, wait-released, import-to-refs, and import-release.

Control flow: `gntdev_open` allocates the dma-buf private context through this interface, `gntdev_ioctl` dispatches dma-buf commands to these helpers, and `gntdev_release` finalizes the context.

State and persistence: the header defines no storage. It forward-declares `struct gntdev_dmabuf_priv` and `struct gntdev_priv`, keeping dma-buf implementation details private to `gntdev-dmabuf.c`.

Dependencies and integration: depends on `<xen/gntdev.h>` for userspace IOCTL structs and on gntdev core structures via forward declarations.

Risks: prototype drift breaks the optional dma-buf build; because the header hides implementation details, all state lifetime rules must be honored by the implementation and `gntdev.c` call sites.

Test signals: compile with `CONFIG_XEN_GNTDEV_DMABUF=y/m`, issue every dma-buf IOCTL through `/dev/xen/gntdev`, and compile with the option disabled to verify normal gntdev remains independent.
