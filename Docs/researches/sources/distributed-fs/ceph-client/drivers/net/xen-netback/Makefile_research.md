# sources/distributed-fs/ceph-client/drivers/net/xen-netback/Makefile

This Makefile builds the Xen network backend module. It maps `CONFIG_XEN_NETDEV_BACKEND` to `xen-netback.o` and composes the module from `netback.o`, `xenbus.o`, `interface.o`, `hash.o`, and `rx.o`.

There is no runtime control flow or persistent state in the file, but it is the integration point that ensures the hash support researched here is linked with the netback data plane, Xenbus lifecycle, interface code, and RX handling. Dependencies are kernel kbuild and the configuration symbol. Risks are omitted object files causing unresolved symbols or dead feature code, and build changes that split hash/control functionality without updating this list. Test signals are `CONFIG_XEN_NETDEV_BACKEND=m/y` builds, module load, and symbol resolution for functions declared in `common.h`.
