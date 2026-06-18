# sources/distributed-fs/ceph-client/drivers/dax/super.c

Purpose: DAX core pseudo-filesystem and exported service layer. It allocates `struct dax_device`, maintains liveness with SRCU, manages DAX holders/ops, exposes direct-access/copy/zero/recovery helpers, and registers the DAX char-device major and bus.

Important APIs/types/functions: `struct dax_device`, `dax_read_lock()/unlock()`, `dax_direct_access()`, copy/zero/recovery helpers, `dax_holder_notify_failure()`, cache/sync/nocache/nomc setters, `dax_set_ops()`, `kill_dax()`, `run_dax()`, `dax_dev_get()`, `alloc_dax()`, `put_dax()`, `inode_dax()`, `dax_inode()`, `dax_get_private()`, FS-DAX holder APIs, and `dax_core_init()/exit()`.

Control flow and state: DAX devices are private inodes on a pseudo filesystem, keyed by char devt and allocated from a slab cache. Alive state is guarded by `dax_srcu`; `kill_dax()` clears alive, notifies holders of pre-remove failure, waits for SRCU readers, and clears holder data. `alloc_dax()` allocates a minor, inode, private data, and ops; device drivers later add cdevs. FS-DAX can exclusively acquire a holder on block-backed or devdax-backed DAX devices.

Dependencies and integration: depends on VFS, pseudo_fs, cdev, SRCU, xarray host mapping for block DAX, DAX operations, cache flush APIs, FS_DAX, block layer, and DAX bus init.

Risks and test signals: liveness races, holder exclusivity, aliasing-cache rejection, ops replacement, char minor cleanup, and init error unwind are key. Test direct_access before/after kill, fs_dax_get exclusivity, block-device host lookup, dax_set_ops conflicts, cache-copy variants, memory failure notification, module init failures, and final inode destruction warnings.
