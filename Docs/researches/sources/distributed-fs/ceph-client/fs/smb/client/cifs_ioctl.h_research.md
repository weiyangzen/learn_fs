<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_ioctl.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_ioctl.h

Purpose: defines userspace-visible CIFS/SMB3 ioctl data structures and command numbers.

Important APIs and types: structures include `smb_mnt_fs_info`, `smb_mnt_tcon_info`, `smb_snapshot_array`, `smb_query_info`, `smb3_key_debug_info`, `smb3_full_key_debug_info`, `smb3_notify`, and `smb3_notify_info`. Ioctl commands include copychunk, set integrity, mount info, snapshots, passthrough query/set/fsctl, key dump, notify, full key dump, tcon info, and shutdown. Shutdown flags mirror XFS-style going-down modes.

Control flow: no executable code; `ioctl.c` and user tools include these layouts to marshal fixed and flexible-array payloads.

State and persistence: structures describe transient ioctl input/output. `__packed` fixes ABI layout, so field ordering and width are persistent userspace ABI.

Dependencies and integration: depends on SMB protocol constants such as key sizes and cipher types, Linux ioctl encoding macros, and userspace headers consuming the command numbers.

Risks: ABI compatibility is the main risk. Packed structs with flexible tails require careful size validation in handlers. Key dump ioctls expose session and encryption keys and must remain gated by debug/security policy. Boolean fields inside packed ABI need consistent userspace interpretation.

Test signals: ioctl size/offset checks on 32-bit and 64-bit userspace, snapshot enumeration buffer sizing, passthrough query input/output lengths, notify info flexible payload, key dump permission/config gating, and shutdown flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_ioctl.h -->
