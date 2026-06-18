# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debugfs.c

## Purpose

`mpt3sas_debugfs.c` implements the mpt3sas debugfs surface. It creates a global `mpt3sas` debugfs directory, per-adapter `scsi_hostN` directories, a binary-ish `ioc_dump` file that exposes the in-memory `struct MPT3SAS_ADAPTER`, and a `host_recovery` byte attribute. This is diagnostic-only infrastructure intended for kernel debugging and field support, not a stable user ABI.

## Important APIs, Types, And Functions

- Global root: `static struct dentry *mpt3sas_debugfs_root`.
- File operations: `mpt3sas_debugfs_iocdump_fops` wires `_debugfs_iocdump_open()`, `_debugfs_iocdump_read()`, and `_debugfs_iocdump_release()`.
- `_debugfs_iocdump_open()` allocates `struct mpt3sas_debugfs_buffer`, points `debug->buf` directly at the adapter object from `inode->i_private`, sets `debug->len` to `sizeof(struct MPT3SAS_ADAPTER)`, and stores it in `file->private_data`.
- `_debugfs_iocdump_read()` copies from `debug->buf` using `simple_read_from_buffer()`.
- `_debugfs_iocdump_release()` frees the small wrapper but not the adapter memory.
- `mpt3sas_init_debugfs()` creates `/sys/kernel/debug/mpt3sas`.
- `mpt3sas_exit_debugfs()` removes the global tree recursively.
- `mpt3sas_setup_debugfs()` creates per-adapter directory and files.
- `mpt3sas_destroy_debugfs()` removes the per-adapter tree recursively.

## Control Flow

Driver initialization calls `mpt3sas_init_debugfs()` once to create the root. Per adapter setup calls `mpt3sas_setup_debugfs(ioc)`, which names the directory `scsi_host%d` using `ioc->shost->host_no`, creates it under the root, creates `ioc_dump` with mode `0444` and `ioc` as private data, and creates a read-only `host_recovery` u8 file backed by `ioc->shost_recovery`.

When a user opens `ioc_dump`, debugfs passes the adapter pointer through `inode->i_private`. The open helper allocates an independent wrapper so reads can use `file->private_data`. Reads then return bytes from the live adapter structure, respecting file position. Release clears `private_data` and frees the wrapper. Teardown removes adapter or global directories recursively; debugfs handles file dentries.

## State And Persistence Behavior

Debugfs state is runtime-only. The root dentry is global. Each adapter stores `ioc->debugfs_root` and `ioc->ioc_dump` dentries. The `ioc_dump` buffer is not a snapshot: it is a pointer to the live `struct MPT3SAS_ADAPTER`, so repeated reads can observe changing fields. The wrapper allocated at open is per file descriptor and freed at release. `host_recovery` reads the current `ioc->shost_recovery` byte.

## Dependencies And Integration Points

The file depends on Linux debugfs, SCSI host structures, PCI/kernel types, and `mpt3sas_base.h` for `struct MPT3SAS_ADAPTER` and `struct mpt3sas_debugfs_buffer`. It integrates with the mpt3sas adapter lifecycle: setup must happen after `ioc->shost` and `ioc->pdev` are valid, and destroy must happen before or during adapter removal so debugfs no longer exposes freed adapter memory.

## Risks And Edge Cases

- `ioc_dump` exposes the raw in-kernel adapter structure, including pointers and layout-dependent data. This is useful for debugging but unsuitable as a stable ABI and potentially sensitive on systems where debugfs is accessible.
- The dump reads live memory without locking or snapshotting; concurrent adapter updates can produce inconsistent data.
- Lifetime safety depends on debugfs removal and open-file handling relative to adapter free. Because the wrapper points directly at `ioc`, stale opens during removal deserve scrutiny.
- Error handling logs failures but does not always clear partially created dentries. For example, if `ioc_dump` creation fails, it removes `ioc->debugfs_root` but does not reset the stored pointer in this file.
- If debugfs is disabled or unavailable, the create helpers may return error pointers on some kernels; consumers should align with kernel debugfs API expectations.

## Test Signals

With debugfs mounted, tests should verify `/sys/kernel/debug/mpt3sas` appears after driver init, per-host `scsi_hostN` directories appear after adapter setup, `ioc_dump` can be read and has `sizeof(struct MPT3SAS_ADAPTER)` bytes available through normal offset reads, and `host_recovery` reflects `ioc->shost_recovery`. Removal tests should open/read/release across adapter teardown and ensure no use-after-free or stale debugfs entries remain. Permission checks should confirm files are read-only (`0444`) and no stable parsing is assumed by tooling.
