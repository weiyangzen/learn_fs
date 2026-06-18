<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Makefile -->
# sources/distributed-fs/ceph-client/net/9p/Makefile

This Makefile builds the 9P network core and transport modules. `9pnet.o` is composed of `mod.o`, `client.o`, `error.o`, `protocol.o`, and `trans_common.o`. Separate transport modules are built for FD, virtio, Xen, RDMA, and USB gadget according to Kconfig.

There is no runtime state. The integration point is object composition: core protocol/client/error handling is shared by all transports, while each transport registers a `p9_trans_module` at runtime.

Risks are missing object inclusion when new core helpers are added or transport module names not matching `request_module("9p-%s")`. Tests should compile each transport and verify symbol dependencies against the core module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Makefile -->
