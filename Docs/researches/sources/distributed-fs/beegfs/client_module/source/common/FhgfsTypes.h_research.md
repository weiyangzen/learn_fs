# sources/distributed-fs/beegfs/client_module/source/common/FhgfsTypes.h

## Research
`FhgfsTypes.h` defines a compact BeeGFS stat structure used by the client module. `struct fhgfs_stat` carries mode, link count, uid, gid, logical size, block count, access/modification/change times as BeeGFS `Time`, and `metaVersion`. The type is a bridge between remote metadata responses and Linux inode/stat update code.

There is no executable control flow and no persistent state. Dependencies are Linux `in.h`, `time.h`, and `common/toolkit/Time.h`. Integration points are metadata/stat message handling and filesystem inode attribute conversion, where callers need a BeeGFS-specific stat payload before translating into kernel `struct kstat` or inode fields. Risks are layout and semantic drift from server/user-space common definitions, especially `ctime` meaning attribute change time and not creation time, integer width mismatches for size/block fields, and time conversion precision. Test signals are stat/getattr paths returning expected ownership, mode, size, timestamps, and metadata version after remote operations.
