## sources/distributed-fs/ceph-client/fs/nfs/sysfs.h

Purpose: declares the NFS sysfs interface and the per-net namespace client object used by `sysfs.c`. It defines `CONTAINER_ID_MAXLEN`, `struct nfs_netns_client`, and the sysfs lifecycle/link/server helpers consumed by NFS client setup and teardown code.

The key type embeds two kobjects: one for the namespace-visible `nfs_client` object and one for the intermediate `net` object, plus a `struct net *` and an RCU-protected identifier string. State and persistence are owned by `sysfs.c`, with callers only holding pointers in `struct nfs_net`. Dependencies are forward-declared NFS and kernel kobject/net types from included translation units. Risks are primarily ABI/lifetime risks: changing the struct or prototypes affects netns setup, server sysfs registration, and sysfs shutdown controls. Test signals are compile coverage for all sysfs helper users and runtime creation/destruction of netns and server sysfs objects.
