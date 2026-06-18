# sources/distributed-fs/ceph-client/include/linux/nfs_common.h

Purpose: Declares common conversion helpers from NFS protocol status codes to Linux errno values.

Important APIs, types, and functions: Exports `nfs_stat_to_errno()` and `nfs4_stat_to_errno()`. Detected source surface: 18 lines; includes `linux/errno.h`, `uapi/linux/nfs.h`; macros `_LINUX_NFS_COMMON_H`; structs none; enums none; typedefs none; function-like declarations/helpers `nfs4_stat_to_errno`, `nfs_localio_errno_to_nfs4_stat`, `nfs_stat_to_errno`.

Control flow: RPC completion paths call these helpers when translating server status fields into VFS-visible errors.

State and persistence behavior: No state is stored; mappings are deterministic conversion tables in implementation files.

Dependencies and integration points: Depends on errno and UAPI NFS status enums. Used throughout NFSv2/v3/v4 RPC decode paths.

Risks and test signals: Risks are incorrect errno mapping and retry policy changes. Test representative NFS status codes such as stale handle, jukebox/delay, permission, exist, and xattr errors.
