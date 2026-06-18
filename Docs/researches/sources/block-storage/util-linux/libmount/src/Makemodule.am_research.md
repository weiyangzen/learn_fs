# File Research: sources/block-storage/util-linux/libmount/src/Makemodule.am

Main Automake build fragment for libmount.

Key responsibilities:
- Defines generated/public libmount include installation.
- Builds `libmount.la` from core table, fs, parser, option, lock, cache, update, diff, listmount/statmount, utility, test, init, and version sources.
- Adds Linux-only context, hook, monitor, and optional Btrfs sources.
- Defines libmount link dependencies and compile flags.
- Defines static check binaries for libmount unit/smoke tests.
- Installs hooks to move shared objects from `usrlib_execdir` to `libdir` when needed.

Important behavior:
- `btrfs.c` is included only when both Linux and `HAVE_BTRFS` are true.
- Tests are gated by `BUILD_LIBMOUNT_TESTS`; monitor/context tests are Linux-only.
- Fuzz target is conditional on `FUZZING_ENGINE`.
- Shared library versioning uses `LIBMOUNT_VERSION_INFO` and optional version scripts.

Dependencies:
- Depends on libcommon, libblkid, optional SELinux, cryptsetup, systemd/udev, realtime libs, and many project configuration variables.

Notable risks:
- Build surface is highly conditional; source availability differs by platform and configure options.
- Install hook performs manual shared-library relocation and symlink recreation.
