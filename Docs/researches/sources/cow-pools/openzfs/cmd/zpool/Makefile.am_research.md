# File Research: sources/cow-pools/openzfs/cmd/zpool/Makefile.am

Automake build/install definition for the `zpool` command and its helper data.

Program build:
- Adds `zpool` to `sbin_PROGRAMS` and `CPPCHECKTARGETS`.
- Sets CFLAGS/CPPFLAGS with common flags plus `libblkid`, `libuuid`, and local include path.
- Builds common sources: `zpool_iter.c`, `zpool_main.c`, `zpool_util.c`, `zpool_util.h`, and `zpool_vdev.c`.
- Adds OS-specific vdev code conditionally: `os/freebsd/zpool_vdev_os.c` for FreeBSD, `os/linux/zpool_vdev_os.c` for Linux.
- Links against `libzfs`, `libzfs_core`, `libnvpair`, `libzutil`, gettext, math, blkid/uuid, and `-lgeom` on FreeBSD.

Installed helper scripts:
- Installs `zpool.d` scripts under `$(zfsexecdir)/zpool.d`.
- Adds these scripts to shellcheck coverage.
- Lists custom-column helpers such as `smart`, SMART aliases, `ses` aliases, `lsblk` aliases, `iostat` aliases, `media`, `dm-deps`, and `upath`.
- `zpoolconfdefaults` controls which helper names get default symlinks under `$(sysconfdir)/zfs/zpool.d`.

Compatibility profiles:
- Installs compatibility feature-set files under `$(pkgdatadir)/compatibility.d`.
- Defines canonical-to-alias symlink pairs for profile names such as years, FreeBSD/TrueNAS/Ubuntu names, GRUB profiles, and OpenZFS version aliases.

Install hook:
- Creates the system `zpool.d` config directory and symlinks default helpers if not already present.
- Creates compatibility alias symlinks forcibly in the compatibility directory.

Role:
- Ties together command compilation, OS-specific implementation selection, helper script distribution, default custom-column availability, and compatibility-profile packaging.
