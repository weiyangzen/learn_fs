# File Research: sources/cow-pools/bcachefs-tools/fs/Kconfig

- Kernel Kconfig entries for bcachefs.
- Main `BCACHEFS_FS` tristate depends on block support and selects exportfs, CRC, compression, crypto, keys, RAID/XOR, xxhash, ACL, and symbolic error-name support.
- Defines optional quota, debug, transaction restart injection, tests, lock timing, latency-accounting disable, six-lock optimistic spinning, path tracepoints, transaction kmalloc tracing, and mean/variance KUnit test options.
