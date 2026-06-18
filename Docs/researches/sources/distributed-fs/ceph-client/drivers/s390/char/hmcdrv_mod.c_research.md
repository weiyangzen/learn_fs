<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_mod.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_mod.c

**Purpose:** This is the module wrapper for HMC drive DVD access. It wires the FTP transport, cache layer, and character/block-like device facade into a single loadable module.

**Important APIs and functions:** The module parameter `cachesize` is stored in `hmcdrv_mod_cachesize` and defaults to `HMCDRV_CACHE_SIZE_DFLT`. `hmcdrv_mod_init()` probes the FTP backend without cache, starts the cache with the selected size, and finally initializes the exported device. `hmcdrv_mod_exit()` tears down the device and cache in reverse order.

**Control flow, state, and persistence:** Initialization is deliberately staged. A failed `hmcdrv_ftp_probe()` aborts without allocating cache state. A failed cache startup aborts before device exposure. A failed device init shuts the cache down. Persistent module state is limited to the cache size parameter; operational state lives in the cache, device, and FTP layers.

**Dependencies and integration:** It includes `hmcdrv_ftp.h`, `hmcdrv_dev.h`, and `hmcdrv_cache.h`. The module metadata identifies it as "HMC drive DVD access".

**Risks and test signals:** Risk centers on cleanup ordering and partial initialization. The file correctly avoids device exposure before the backend and cache exist, but tests should verify load failure paths, cache-size validation in the cache layer, `hmcdrv_dev_init()` failure cleanup, repeated load/unload, unsupported backend probe failure, and absence of stale device nodes after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_mod.c -->
