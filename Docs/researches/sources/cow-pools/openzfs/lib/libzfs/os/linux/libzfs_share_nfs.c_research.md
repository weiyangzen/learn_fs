# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_share_nfs.c

Linux NFS sharing backend. It translates Solaris/ZFS NFS share options into Linux export entries under `/etc/exports.d/zfs.exports` and commits with `exportfs -ra`.

Key components:
- `foreach_nfs_shareopt()` parses comma-separated share options; `"on"` expands to `rw,crossmnt`.
- `foreach_nfs_host_cb()` parses `rw=`/`ro=` host lists, including bracketed IPv6 literals and CIDR suffixes.
- `get_linux_shareopts_cb()` validates Linux export options, maps `anon` to `anonuid`, `root_mapping` to `root_squash,anonuid`, and `nosub` to `subtree_check`.
- `get_linux_shareopts()` always adds `no_subtree_check` and `mountpoint`.
- `nfs_add_entry()` writes escaped mountpoint lines in Linux exports syntax: `path host(sec=...,access,...opts)`.

Availability is cached by checking `/usr/sbin/exportfs`; truncation separately checks `/etc/exports.d`. Unknown or unsupported share options return syntax errors.
