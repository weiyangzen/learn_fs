# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.c

This file is the protocol-neutral libshare dispatcher used by libzfs for ZFS dataset sharing. It presents a small common API over protocol-specific NFS and SMB implementations.

Primary responsibilities:
- Validate share protocol enum values.
- Dispatch enable, disable, status, commit, truncate, and option-validation operations to the selected protocol backend.
- Provide lower-case protocol names for NFS and SMB.
- Convert internal `SA_*` share errors into localized strings.

Key definitions:
- `sa_protocol_names[]` maps `SA_PROTOCOL_NFS` to `"nfs"` and `SA_PROTOCOL_SMB` to `"smb"`.
- `fstypes[]` maps protocol ids to `libshare_nfs_type` and `libshare_smb_type`.
- `init_share()` initializes the small internal share descriptor with dataset name, mountpoint, and share options.
- `VALIDATE_PROTOCOL()` rejects protocol ids outside `[0, SA_PROTOCOL_COUNT)`.

Main functions:
- `sa_enable_share()` validates the protocol and share options, then calls the backend `enable_share`.
- `sa_disable_share()` constructs a share descriptor from the mountpoint and calls backend `disable_share`.
- `sa_is_shared()` checks backend sharing state for a mountpoint.
- `sa_commit_shares()` lets a backend commit pending share changes.
- `sa_truncate_shares()` calls optional backend truncation, if present.
- `sa_validate_shareopts()` rejects control characters/newlines and delegates protocol-specific validation.
- `sa_errorstr()` maps `SA_*` integer errors to human-readable localized text, falling back to `"unknown %d"`.

Important behavior:
- This file does not implement NFS or SMB mechanics itself. It is a stable dispatch layer.
- `sa_validate_shareopts()` assumes `options` is non-NULL and checks for `\a\b\f\n\r`.
- `sa_commit_shares()` and `sa_truncate_shares()` return void and silently ignore invalid protocols via the macro expansion.
- Many `SA_*` values are listed in the header as never returned by current libshare, but `sa_errorstr()` still preserves their strings for compatibility.

Dependencies:
- `libzfs_share.h` for protocol types, errors, and backend vtables.
- `libzfs_impl.h` and `libzfs.h` for libzfs integration and protocol enum definitions.
- Protocol backend objects are defined in NFS/SMB implementation files.
