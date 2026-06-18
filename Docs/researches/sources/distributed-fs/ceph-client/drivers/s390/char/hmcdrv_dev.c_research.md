# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.c

Purpose: exposes HMC drive FTP access through a misc character device named `/dev/hmcdrv`.

Important APIs/types/functions: `hmcdrv_dev_fops` implements open, release, llseek, read, and write. `hmcdrv_dev_open()` starts FTP services; `hmcdrv_dev_release()` shuts them down; `hmcdrv_dev_seek()` resets command state on `SEEK_END`; `hmcdrv_dev_read()` and `hmcdrv_dev_write()` call `hmcdrv_dev_transfer()`; `hmcdrv_dev_init()`/`exit()` register/deregister the misc device.

Control flow: open rejects nonblocking and read-only access, pins the module, and starts backend FTP. The first write stores a NUL-terminated FTP command string in `file->private_data`. Later reads/writes transfer data for that command at the file offset, retrying `-EBUSY` three times with 500 ms sleeps. `SEEK_END` clears the command so the next write supplies a new command.

State and persistence behavior: per-file state is the current command string and file offset. FTP backend refcount state is managed by `hmcdrv_ftp_startup()`/`shutdown()`. No local persistent data is stored.

Dependencies and integration points: depends on miscdevice, VFS file ops, user-copy helpers, module refs, and `hmcdrv_ftp_cmd()`.

Risks and test signals: API semantics are unusual because the first write is command setup and subsequent writes may be file data. Read-only/nonblocking rejection, command reset via seek, retry timing, and cleanup on startup failure need tests. Multiple openers rely on FTP-layer serialization/refcounting.
