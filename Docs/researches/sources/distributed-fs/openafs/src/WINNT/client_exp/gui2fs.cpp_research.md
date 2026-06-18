## sources/distributed-fs/openafs/src/WINNT/client_exp/gui2fs.cpp

Purpose: Implements the Explorer-facing equivalents of many `fs` commands: flush, ACL read/write/copy/clean, mount point and symlink operations, volume quota/status, token display, server/cell lookup, owner/group lookup, and Unix mode bits.

Important APIs/functions: Public entry points match `gui2fs.h`, including `Flush`, `FlushVolume`, `GetRights`, `SaveACL`, `CopyACL`, `ListMount`, `MakeMount`, `RemoveMount`, `GetVolumeInfo`, `SetVolInfo`, `GetTokenInfo`, `MakeSymbolicLink`, `GetCellName`, `GetServers`, `GetOwner`, `GetGroup`, `GetUnixModeBits`, and `SetUnixModeBits`. Internal helpers handle UTF-8 path conversion, AFS error mapping, ACL list mutation, NetBIOS root repair, freelance-root detection, and AFS Client Admin membership checks.

Control flow/state: Most operations build a `ViceIoctl` blob and call `pioctl_T`/`pioctl_utf8`; results either populate MFC `CStringArray` data for dialogs or show immediate message boxes. Process-local static state includes the VLDB client pointer, RX-init flag, cached NetBIOS name, and cached admin membership. Registry reads provide `NetbiosName` and shell/admin policy.

Dependencies/integration: Bridges MFC dialogs, `msgs.cpp`, `HOURGLASS`, `fs_acl`, cache-manager `VIOC*` ioctls, token APIs, protection-server APIs, registry helpers, and host lookup. `shell_ext.cpp`, property pages, ACL dialogs, and volume dialogs call this file heavily.

Risks/tests: Fixed buffers and manual UTF-8 conversions need long Unicode path tests. `CopyACL` appears to use `normal[i]` while copying negative entries, which can corrupt copied negative ACL names. Several paths ignore return values (`SetCacheSizeCmd`, `SetUnixModeBits`) or rely on global `errno`. Test AFS/non-AFS paths, UNC NetBIOS freelance roots, ACL round trips, symlink/mount create/remove, quota updates, token enumeration, owner/group PRDB lookup, and unavailable cache-manager/service cases.
