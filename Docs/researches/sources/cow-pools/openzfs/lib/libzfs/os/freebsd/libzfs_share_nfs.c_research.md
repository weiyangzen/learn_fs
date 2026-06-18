# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_share_nfs.c

FreeBSD NFS sharing backend for libshare. It writes ZFS-managed exports to `/etc/zfs/exports`, using `/etc/zfs/exports.lock` for serialized updates, and signals `mountd` after changes.

Key behavior:
- `translate_opts()` converts comma/space-separated ZFS share options into FreeBSD `exports(5)` syntax by prefixing recognized keywords with `-`.
- `nfs_enable_share_impl()` emits one export line per semicolon-separated option set, escaping mountpoints through common NFS helpers.
- `nfs_disable_share_impl()` emits nothing, relying on `nfs_toggle_share()` to rewrite the export file without the removed share.
- `nfs_commit_shares()` opens `/var/run/mountd.pid` and sends `SIGHUP` when `mountd` is running.
- `libshare_nfs_type` wires enable/disable/status/validate/commit/truncate callbacks into the common libshare layer.

Validation is minimal: empty share options are rejected, otherwise accepted for export-file translation.
