<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/install.sh

## Purpose
Implements `make install` behavior for RISC-V kernel images.

## Important APIs, Types, And Functions
The script consumes four positional arguments: kernel version, image file, System.map file, and install path. It selects `vmlinuz` for `Image.*` and `vmlinuz.efi`, otherwise `vmlinux`.

## Control Flow
With `set -e`, it renames any existing destination image/System.map to `.old`, copies the new image with `cat`, and copies the map file.

## State And Persistence
Persistent state is the installed kernel image and `System.map` under the requested install path, plus `.old` backups.

## Dependencies And Integration Points
Called by the arch Makefile install command and compatible with traditional Linux installkernel flows.

## Risks And Edge Cases
Unquoted path expansions can be fragile for paths with spaces. Failures abort due to `set -e`. The base name policy intentionally treats all compressed images as `vmlinuz`.

## Test Signals
Signals are `make ARCH=riscv install`, correct image/map files in `INSTALL_PATH`, and preserved `.old` backups after repeated installs.

Source read size: 44 lines, 976 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/install.sh -->
