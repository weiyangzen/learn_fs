# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_cache.h

Purpose: declares the HMC drive cache API and default cache sizing.

Important APIs/types/functions: defines `HMCDRV_CACHE_SIZE_DFLT`, typedefs `hmcdrv_cache_ftpfunc`, and declares `hmcdrv_cache_cmd()`, `hmcdrv_cache_startup()`, and `hmcdrv_cache_shutdown()`.

Control flow: no standalone flow. The cache wraps a backend FTP function supplied by `hmcdrv_ftp.c`.

State and persistence behavior: no state in the header; implementation maintains a global transient cache.

Dependencies and integration points: includes memory-zone sizing and HMC FTP command definitions; used by HMC module core and FTP layer.

Risks and test signals: default size depends on `MAX_ORDER_NR_PAGES`, so memory-fragmentation behavior should be tested at module load.
