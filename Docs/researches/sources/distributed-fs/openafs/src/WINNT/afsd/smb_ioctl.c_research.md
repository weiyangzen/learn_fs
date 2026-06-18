# sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.c

## Purpose
Implements the legacy SMB pseudo-file pioctl transport for the Windows OpenAFS client. Opens of `_._AFS_IOCTL_._` become special FIDs; writes accumulate a VIOC request; the first read dispatches the opcode; later reads stream status/data back.

## Important APIs, Types, And Functions
`smb_InitIoctl` fills `smb_ioctlProcsp[SMB_IOCTL_MAXPROCS]` for ACL, volume, cache, cell, token, symlink, mountpoint, rxstat, uuid, Unicode, Unix mode, owner/group, verify-data, and caller-access operations. `smb_SetupIoctlFid` marks `SMB_FID_IOCTL`, attaches `cm_data.fakeSCache`, allocates `smb_ioctl_t`, and copies subst prefix state. Transport entry points are core/V3/raw read/write plus `smb_IoctlPrepareRead` and `smb_IoctlPrepareWrite`. `smb_ParseIoctlPath` and `smb_ParseIoctlParent` translate UTF-8/ANSI/OEM paths, UNC shares, `\\afs\all`, literal mode, and tree-relative names into `cm_scache_t` objects. Handlers mostly delegate to matching `cm_Ioctl*` functions.

## Control Flow
Writes allocate/zero buffers, set `CM_IOCTLFLAG_DATAIN`, append bytes, and enforce `SMB_IOCTL_MAXDATA`. Reads resolve SMB UID to `cm_user_t`, detect LocalSystem, resolve TID path, consume the first 32-bit opcode, validate dispatch bounds, reserve output space for the return code, invoke the handler, and copy the handler status into output. Subsequent reads stream `outAllocp` until `outCopied` reaches `outDatap`.

## State And Persistence
Per-FID state is `smb_ioctl_t`: active UID, tree path, subst prefix, and mutable `cm_ioctl_t` buffer pointers/counters/flags. Persistent effects are delegated to cache-manager state: tokens, ACL cache, cache contents, volume/cell preferences, symlinks, mountpoints, Unix metadata, trace settings, and validation data. `smb_IoctlSetToken` is the major stateful path and stores Kerberos ticket/session key/kvno/expiration under `userp->mx`.

## Dependencies And Integration Points
Depends on Windows SID/account APIs, SMB UID/TID/share APIs, `cm_NameI`, scache synchronization, pioctl query options, NetBIOS raw send, logging, and broad `cm_Ioctl*` cache-manager handlers. It integrates command tools, Explorer, logon token flow, SMB tree connections, and redirector compatibility.

## Risks
Security-sensitive areas include LocalSystem token installation, RPC SID validation, path encoding confusion, UNC/share/cell parsing, fixed-size path arrays, opcode-table drift, output buffer overrun by delegated handlers, and user/UID lifetime handling. Set-owner/group/mode paths assume required query options supply an scache.

## Test Signals
Test core and AndX reads/writes, fragmented writes, raw read, invalid/unassigned opcodes, UTF-8 and OEM paths, UNC and `\\afs\all` paths, query-by-FID, literal mountpoint behavior, LocalSystem and non-LocalSystem token logon, symlink/mountpoint ops, and cache/volume/cell operations.
