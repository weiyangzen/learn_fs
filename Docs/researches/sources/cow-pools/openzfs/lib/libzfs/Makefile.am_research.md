# File Research: sources/cow-pools/openzfs/lib/libzfs/Makefile.am

This Automake fragment defines the `libzfs.la` build.

Build flags:
- `libzfs_la_CFLAGS` includes common AM/library flags, libcrypto flags, zlib flags, and `-fvisibility=hidden`.

Library registration:
- Adds `libzfs.la` to `lib_LTLIBRARIES`.
- Adds `libzfs.la` to `CPPCHECKTARGETS`.

Distributed libzfs sources include:
- `libzfs_impl.h`
- `libzfs_share.h`
- `libzfs_changelist.c`
- `libzfs_config.c`
- `libzfs_crypto.c`
- dataset, diff, import, iter, mount, pool, share, send/recv, status, and utility implementation files.

Platform-specific sources:
- FreeBSD builds add compatibility, NFS/SMB share, and zmount files under `os/freebsd`.
- Linux builds add mount, pool, NFS/SMB share, and utility files under `os/linux`.

Nondistributed compiled-in common sources:
- zcommon modules such as cityhash, features, delegation, fletcher variants, namecheck, props, value strings, and zpool props.
- Special handling includes `module/zfs/btree.c` and `module/zfs/range_tree.c` as sources rather than `LIBADD` dependencies so their symbols are not exported as libzfs API.

Link dependencies:
- `libzfs_core.la`
- `libnvpair.la`
- `libzutil.la`
- system/libs: `-lrt`, `-lm`, libcrypto, zlib, libfetch, gettext.
- FreeBSD adds `-lutil -lgeom`.

LDFLAGS:
- Version info is `7:0:0`.
- Adds `-Wl,-z,defs` when ASAN is not enabled.

Install/data outputs:
- Installs `libzfs.pc` as pkg-config data.
- Distributes ABI and suppression files plus OpenSSL third-party license metadata.
