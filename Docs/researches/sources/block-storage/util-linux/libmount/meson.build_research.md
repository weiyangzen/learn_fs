# File Research: sources/block-storage/util-linux/libmount/meson.build

## Scope

Meson build definition for libmount, its generated public header, libraries, pkg-config metadata, tests, and Python subdirectory.

## Behavior

- Disables libmount dependencies and exits when `build_libmount` is false.
- Generates `libmount.h` with version macros.
- Defines core source list and adds Linux-only context/hook/monitor sources when building on Linux.
- Builds internal static `_mount`, static `mount_static`, and shared `mount` libraries with blkid/common dependencies.
- Applies linker version script when supported.
- Generates pkg-config metadata and Meson dependency override.
- Builds test executables when `program_tests` is enabled and symlinks them into the project build root.
- Enters `libmount/python`.

## Dependencies And Risks

- Requires either `dirfd` or `ddfd` when libmount is built.
- Optional dependencies include SELinux, cryptsetup/dlopen, realtime libs, systemd/udev support, and btrfs.
- Linux-only sources define most context and mount/umount behavior.
