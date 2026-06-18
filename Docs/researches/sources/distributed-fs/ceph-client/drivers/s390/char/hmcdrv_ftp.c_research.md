# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.c

Purpose: implements the common HMC drive FTP command parser, backend selection, serialization, cache integration, userspace transfer wrapper, and exported kernel FTP API.

Important APIs/types/functions: `struct hmcdrv_ftp_ops` abstracts startup/shutdown/transfer backend operations. `hmcdrv_ftp_cmd_getid()` maps command text via CRC16 table; `hmcdrv_ftp_parse()` parses `<cmd> <filename>`; `hmcdrv_ftp_do()` serializes cached backend transfers; `hmcdrv_ftp_probe()` probes service availability; `hmcdrv_ftp_cmd()` copies user buffers and dispatches read/write/delete commands; `hmcdrv_ftp_startup()`/`shutdown()` manage backend selection and refcounting.

Control flow: startup chooses DIAG FTP on z/VM or SCLP FTP on LPAR/KVM, starts the backend once, and increments a reference count. Userspace commands are parsed, a DMA buffer is allocated, data is copied in for put/append or copied out for dir/nls/get, and `hmcdrv_ftp_do()` calls the selected backend through the cache. Shutdown decrements the refcount and stops the backend at zero.

State and persistence behavior: global state is `hmcdrv_ftp_funcs`, `hmcdrv_ftp_refcnt`, and `hmcdrv_ftp_mutex`, plus cache state in `hmcdrv_cache.c`. Remote HMC files/media may be read or modified by FTP commands; local kernel state is transient.

Dependencies and integration points: integrates `hmcdrv_dev.c`, exported kernel users, cache layer, DIAG backend, SCLP backend, CRC16, machine-type detection, user-copy helpers, and DMA page allocation.

Risks and test signals: command hashing depends on fixed table order and CRC modulo with known collision avoidance; `hmcdrv_ftp_shutdown()` unconditionally decrements refcount and assumes balanced startup. Test parser edge cases, all command IDs, backend selection on VM/LPAR/KVM/unsupported machines, concurrent openers, startup failure, probe mappings, large transfer allocation order, user-copy failures, and cache invalidation after writes/errors.
