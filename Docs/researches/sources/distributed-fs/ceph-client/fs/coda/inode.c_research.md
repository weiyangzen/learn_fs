# sources/distributed-fs/ceph-client/fs/coda/inode.c

Purpose: implements Coda filesystem superblock setup, fs_context parsing, inode-cache allocation, mount binding to a Venus pseudo-device slot, and generic inode attribute/statfs operations. It is the mount-time bridge between VFS and the per-device `venus_comm` objects owned by `psdev.c`.

Important APIs/types/functions: `coda_init_inodecache()` and `coda_destroy_inodecache()` manage the `coda_inode_info` slab. `coda_alloc_inode()` initializes Coda fid/cache fields and spinlocks. `coda_set_idx()`, `coda_parse_fd()`, and `coda_parse_monolithic()` accept modern `fd=` or legacy binary mount data. `coda_fill_super()` validates `vc_inuse`, rejects duplicate mounts, stores `vc_sb`, fetches `venus_rootfid()`, creates the root inode with `coda_cnode_make()`, and installs Coda super/dentry operations. `coda_getattr()`, `coda_setattr()`, and `coda_statfs()` delegate to Venus or fill fallback statfs values.

Control flow: mount parsing resolves a coda character-device minor to `ctx->idx`; `get_tree_nodev()` calls `coda_fill_super()`, which temporarily claims the `venus_comm`, initializes the anonymous superblock, asks Venus for the root fid, then creates `s_root`. Error paths clear `vc_sb` and `s_fs_info`. Unmount uses `coda_put_super()` to detach the superblock from the pseudo-device.

State and persistence: persistent kernel state is in `coda_comms[idx].vc_sb`, `sb->s_fs_info`, and per-inode `coda_inode_info`; on-disk persistence is managed by Venus, not this file. `SB_NOATIME` is enforced on mount/reconfigure.

Dependencies/integration: depends on Coda protocol structs, `coda_psdev.h`, `coda_linux.h`, cache helpers, VFS fs_context, inode slab APIs, and upcalls in `upcall.c`. Mounts are restricted to the initial PID namespace.

Risks: pseudo-device lifetime and mount lifetime must stay synchronized under `vc_mutex`; duplicate mount or dead Venus handling must not leak `vc_sb`. Attribute updates rely on Venus truncating backing container files. `coda_put_super()` destroys a mutex in a global `venus_comm`, so open/reopen sequencing around `psdev` must stay disciplined.

Test signals: mount with valid/invalid `fd=`, legacy binary mount data, duplicate mount on one minor, Venus shutdown during mount, setattr/getattr propagation, fake statfs fallback, namespace-restricted mount rejection, and slab leak checks across module unload.
