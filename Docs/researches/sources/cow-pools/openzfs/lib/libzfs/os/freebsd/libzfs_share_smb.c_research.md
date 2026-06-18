# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_smb.c

FreeBSD SMB sharing backend stub. SMB support is not implemented for this platform path.

All operational callbacks either return `SA_NOT_SUPPORTED` with `"No SMB support in FreeBSD yet.\n"` on stderr, or return inactive/no-op status:
- `smb_enable_share()`, `smb_disable_share()`, and `smb_validate_shareopts()` reject use.
- `smb_is_share_active()` always returns `B_FALSE`.
- `smb_update_shares()` returns success as an unimplemented commit hook.

`libshare_smb_type` is still exported so higher-level share code has a platform-defined SMB backend.
