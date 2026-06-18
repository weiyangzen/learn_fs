# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_smb.c

Linux SMB sharing backend using Samba usershares. It creates and deletes shares via `net usershare` and detects active shares by parsing Samba usershare files.

Key behavior:
- `smb_retrieve_shares()` scans `SMB_SHARE_DIR`, reads regular share files, and extracts `path`, `comment`, and `guest_ok`.
- `smb_enable_share_one()` normalizes ZFS dataset names into Samba-safe share names and runs `net -S <host> usershare add ... Everyone:F`.
- `smb_enable_share()` disables any existing share at the same mountpoint before creating a new one.
- `smb_disable_share()` finds active shares by path and runs `net usershare delete`.
- `smb_validate_shareopts()` only accepts `on` and `off`.
- `smb_available()` requires both the Samba `net` command and usershare directory.

Commit/update is a no-op; Samba usershare changes are effected by command execution.
