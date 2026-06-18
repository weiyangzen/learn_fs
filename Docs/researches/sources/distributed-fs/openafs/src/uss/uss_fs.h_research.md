
# sources/distributed-fs/openafs/src/uss/uss_fs.h

Purpose: `uss_fs.h` declares the cache-manager and token operations used by account creation and deletion.

Important APIs: it defines `USS_FS_MAX_SIZE` as the shared 2048-byte buffer size and declares `uss_fs_InBuff`/`uss_fs_OutBuff`. The public functions get/set ACLs, get/set volume status, refresh backup mappings, create/remove mount points, and unlog tokens for a cell.

Control flow and integration: `uss_acl.c` uses ACL and volume-status setters, `uss_vol.c` uses volume status and mount-point handling, and `uss.c` allocates the declared buffers and calls token unlog on exit when administrator authentication was staged.

State and persistence: callers must allocate the two exported buffers before functions that rely on them. The API directly represents persistent AFS cache-manager effects.

Risks and test signals: the header exposes raw mutable buffers and raw `char *` path arguments, so callers must enforce size and lifetime. Tests should verify buffer allocation before use, pioctl error propagation, and dry-run callers avoiding persistent calls.
