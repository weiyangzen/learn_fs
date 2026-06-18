# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/qat.c

## Purpose

Top-level Intel QAT integration for OpenZFS when built with `_KERNEL` and `HAVE_QAT`.

## Main State

- `qat_stats`: kstat-named counters for compression, decompression, encryption, decryption, checksum requests, byte totals, and failure counts.
- `qat_ksp`: installed `zfs/qat` kstat.

## Functions

- `qat_mem_alloc_contig(pp, size)`: QAT-compatible contiguous allocation wrapper using `kmalloc`.
- `qat_mem_free_contig(pp)`: frees and nulls contiguous allocation.
- `qat_init()`: creates QAT kstat, initializes compression and crypto/checksum QAT subsystems, and sets disable flags when initialization fails.
- `qat_fini()`: deletes kstat and finalizes crypto/checksum and compression subsystems.

## Notes

Initialization does not fail module loading. If QAT setup fails, it sets runtime disable parameters so QAT can potentially be re-enabled later through sysfs/module parameters.
