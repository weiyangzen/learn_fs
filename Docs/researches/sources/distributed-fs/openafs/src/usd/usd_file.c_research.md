
# sources/distributed-fs/openafs/src/usd/usd_file.c

`usd_file.c` is the POSIX implementation of the USD abstraction. It wraps file descriptors in `usd_handle_t`, implements read/write/seek/ioctl/close callbacks, supports large-file seeking when available, maps common tape operations to platform ioctls, and optionally obtains advisory whole-file locks at open time.

Important functions are `usd_FileRead`, `usd_FileWrite`, `usd_FileSeek`, `usd_FileIoctl`, `usd_FileClose`, `usd_FileOpen`, `usd_Open`, `usd_StandardInput`, and `usd_StandardOutput`. `usd_FileIoctl` handles type/device/size/fullname/setsize/tape/blocksize/seekable requests using `fstat`, `ftruncate`, `ioctl(MTIOCTOP)` or AIX `STIOCTOP`, and platform block-size fallbacks. `usd_FileOpen` maps USD flags to `open`/`open64` flags, allocates a handle, installs callbacks, duplicates the path, and applies read or write locks via `fcntl`.

Persistence behavior is direct filesystem/device I/O. Writes go immediately to the fd; `USD_OPEN_SYNC` maps to `O_SYNC` when available. Close calls `fsync` only for writable block devices before closing and freeing the handle. Size changes call `ftruncate`/`ftruncate64`. Standard input/output wrappers allocate dummy handles that do not close the underlying fd.

Dependencies include POSIX I/O, `mtio`/AIX tape headers, OpenAFS assertions, and offset type feature macros. Risks include partial read/write semantics being surfaced only through `xferdP`, advisory locks not guaranteeing device exclusivity everywhere, removed hard-disk attachment checks, platform tape ioctl differences, and standard handles using static string names freed only by dummy close. Test signals include regular-file open/read/write/seek/truncate, lock conflict tests, block/char/fifo seekability, tape ioctl mapping, large offsets, and block-device close fsync behavior.
