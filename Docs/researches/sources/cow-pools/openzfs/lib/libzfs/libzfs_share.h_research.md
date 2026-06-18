# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.h

This header defines the internal libzfs share abstraction used to support ZFS `sharenfs` and `sharesmb` behavior without binding the common code to one protocol.

Primary responsibilities:
- Declare share error constants.
- Declare protocol-neutral share-control functions.
- Define the backend vtable shape for NFS/SMB share implementations.
- Declare internal NFS helper functions and constants.
- Declare internal SMB constants and share-list data structure.

Public/common declarations:
- `sa_errorstr(int)` returns a localized string for an `SA_*` error.
- `sa_protocol_names[]` exposes lower-case protocol names.
- `sa_enable_share()`, `sa_disable_share()`, `sa_is_shared()`, `sa_commit_shares()`, `sa_truncate_shares()` are the protocol-neutral share API.
- `sa_validate_shareopts()` validates protocol-specific option strings.

Error constants:
- Active errors include `SA_OK`, `SA_SYSTEM_ERR`, `SA_SYNTAX_ERR`, `SA_NO_MEMORY`, `SA_INVALID_PROTOCOL`, and `SA_NOT_SUPPORTED`.
- Many compatibility errors are defined but documented as never returned by current libshare, including duplicate name, bad path, no permission, invalid security, section/resource errors, and share-exists cases.

Core internal types:
- `sa_share_impl_t` points to a const structure containing:
  - `sa_zfsname`
  - `sa_mountpoint`
  - `sa_shareopts`
- `sa_fstype_t` is the backend vtable with function pointers:
  - `enable_share`
  - `disable_share`
  - `is_shared`
  - `validate_shareopts`
  - `commit_shares`
  - `truncate_shares`

Backend symbols:
- `libshare_nfs_type`
- `libshare_smb_type`

NFS internals:
- `NFS_FILE_HEADER` is the generated exports-file warning header.
- `nfs_escape_mountpoint()` escapes mountpoints for `/etc/exports`-style matching.
- `nfs_is_shared_impl()` scans exports content for a mountpoint.
- `nfs_toggle_share()` performs locked temporary-file update of exports content.
- `nfs_reset_shares()` truncates generated exports state under lock.

SMB internals:
- Defines `SMB_NAME_MAX`, `SMB_COMMENT_MAX`, `SMB_SHARE_DIR`, `SMB_NET_CMD_PATH`, and `SMB_NET_CMD_ARG_HOST`.
- `smb_share_t` stores Samba usershare metadata: name, path, comment, guest flag, and next pointer.

Research relevance:
- This header is the small contract between generic ZFS sharing code and protocol-specific share backends.
- Its vtable design keeps `libzfs_share.c` protocol-independent while allowing NFS and SMB to use very different persistence mechanisms.
