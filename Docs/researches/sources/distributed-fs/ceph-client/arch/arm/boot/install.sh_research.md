<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/arm/boot/install.sh

## Purpose
Architecture-specific `make install` helper for ARM kernel images. It copies a built image and `System.map` to the requested install directory using versioned names.

## Important APIs/types/functions
- Positional arguments: `$1` kernel version, `$2` kernel image file, `$3` System.map file, `$4` install path.
- Image basename dispatch: `zImage` installs as `vmlinuz-$version`; other images install as `vmlinux-$version`.
- Existing installed files are renamed to `.old`.
- Optional `/sbin/loadmap` is executed if present.

## Control flow
The script enables `set -e`, chooses `base` from `basename $2`, rotates existing `$4/$base-$1`, copies the image via `cat`, rotates/copies `$4/System.map-$1`, and either runs `/sbin/loadmap` or prints a manual-install message.

## State and persistence behavior
Persists files in the install directory and creates `.old` backups. It has no kernel runtime state, but it mutates host filesystem install artifacts.

## Dependencies and integration points
Called by the kernel install target. Depends on a POSIX shell, writable install path, the built image, the map file, and optionally `/sbin/loadmap`.

## Risks and edge cases
Variables are unquoted in path tests and copy commands, so paths containing spaces or glob characters are unsafe. A blank `$4` intentionally addresses root-relative paths but can surprise callers. `cat` rather than `cp` may drop metadata. `set -e` stops on copy or move failure.

## Test signals
Run `make ARCH=arm install INSTALL_PATH=/tmp/...` with `zImage` and non-`zImage` inputs; verify backup rotation, final image contents, and `System.map` placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/install.sh -->
