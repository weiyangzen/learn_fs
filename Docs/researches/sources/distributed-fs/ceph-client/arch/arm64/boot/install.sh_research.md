# sources/distributed-fs/ceph-client/arch/arm64/boot/install.sh

## Purpose
This shell script implements `make install` behavior for the AArch64 Linux port. It installs the kernel image and matching `System.map` into the requested install path.

## APIs, Types, And Functions
The script interface is positional: `$1` kernel version, `$2` kernel image, `$3` system map file, and `$4` install path. It chooses basename `vmlinuz` for `Image.gz` or `vmlinuz.efi`, otherwise `vmlinux`. It preserves previous outputs by renaming existing `$base-$version` and `System.map-$version` to `.old`.

## Control Flow, State, And Persistence
With `set -e`, failures stop the install. The script branches on `basename $2`, moves old files if present, writes the kernel image with `cat $2 > $4/$base-$1`, and copies the map with `cp $3 $4/System.map-$1`. Persistent state is the installed kernel, map, and `.old` backups.

## Dependencies And Integration
It depends on POSIX shell utilities `basename`, `mv`, `cat`, and `cp`. It is called from the arm64 kernel build install target and assumes the install path exists.

## Risks And Test Signals
Arguments are mostly unquoted, so paths containing whitespace are risky. An empty or unexpected install path could install in the wrong location. Test with `make ARCH=arm64 install INSTALL_PATH=...`, compressed and uncompressed images, and verification of backup rotation.
