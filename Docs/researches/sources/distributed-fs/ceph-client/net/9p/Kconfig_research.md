<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Kconfig -->
# sources/distributed-fs/ceph-client/net/9p/Kconfig

This Kconfig fragment defines Plan 9 resource-sharing protocol support. `NET_9P` is a tristate menu option and selects `NETFS_SUPPORT`. Transport options include FD/TCP/Unix (`NET_9P_FD`), virtio, Xen, USB gadget, and RDMA. `NET_9P_DEBUG` enables debug logging.

There is no runtime logic in the file, but it shapes which transport modules and dependencies are built. FD transport implies INET and UNIX; virtio depends on VIRTIO; Xen selects the Xen frontend; USB gadget selects configfs and USB composite support; RDMA depends on networking and InfiniBand address translation.

Risks are configuration gaps where a filesystem mount selects 9p but no usable transport is enabled or loadable. Tests should build common transport combinations and verify module autoload names match the transport lookup paths in `mod.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Kconfig -->
