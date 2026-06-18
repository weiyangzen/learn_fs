## sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel.go

Purpose: Implements CephFS kernel-client mounting for the node server.

Important APIs: `KernelMounter` interface, `kernelMounter`, `NewKernelMounter`, `Mount`, `Name`, `mountKernel`, and `filesystemSupported`.

Control flow: `NewKernelMounter` checks `/proc/filesystems` for Ceph support and records whether `modprobe ceph` is needed. `mountKernel` creates the mountpoint, loads the kernel module if needed, resolves FSID from volume options, builds `mount -t ceph <user>@<fsid>.<fsName>=<rootPath> <mountPoint> -o mon_addr=...,secretfile=...,...,_netdev`, and optionally executes inside a network namespace.

State and persistence: Mutates the node mount table and may load a kernel module. `needsModprobe` is process-local state.

Dependencies and risks: Depends on Linux kernel CephFS support, `mount.ceph`/kernel mount behavior, keyfiles, monitor address formatting, and network namespace helper. `filesystemSupported` reads `/proc/filesystems`; test coverage verifies positive `proc` and negative fake filesystem, but not Ceph mounting. Integration should cover FSID lookup and mount option propagation.
