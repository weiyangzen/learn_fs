<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/dirutils.c -->
# sources/distributed-fs/openafs/src/vfsck/dirutils.c

## Purpose
Provides a small OpenAFS partition utility used by `vfsck` to canonicalize a filesystem argument into the corresponding device node when the caller passes a mount point or regular path.

## Important APIs, Types, And Functions
The single exported function is `EnsureDevice(char *abuffer)`. It uses `stat`, `opendir`, `readdir`, and `closedir`, plus OpenAFS constants from `afs/partition.h` such as `AFS_DSKDEV`.

## Control Flow
`EnsureDevice` first stats the input path. If it is already a block or character device, it returns success. Otherwise it records the path’s `st_dev`, scans `AFS_DSKDEV` for block devices, and replaces `abuffer` with the first device whose `st_rdev` matches the original `st_dev`. Failure to stat the input or find a matching block device returns nonzero.

## State And Persistence
The function mutates the caller-supplied buffer in place. It does not write to disk or maintain process-global state.

## Dependencies And Integration Points
`main.c` calls this before `setup` so a mount point or file path can be converted into the raw device checked by fsck. It depends on the local `/dev` naming convention encoded by `AFS_DSKDEV` and assumes the caller’s buffer is large enough for the replacement path.

## Risks And Test Signals
Risks include unchecked `strcpy`/`strcat` into 128-byte buffers, no explicit handling when `opendir` fails, and use of `short dev` for `st_dev`. Tests should cover existing block/char devices, mount points backed by a matching `/dev` entry, missing `/dev`, long device names, and no matching block device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/dirutils.c -->
