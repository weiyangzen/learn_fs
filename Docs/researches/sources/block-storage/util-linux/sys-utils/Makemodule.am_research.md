# File Research: sources/block-storage/util-linux/sys-utils/Makemodule.am

## Scope

Automake module defining build targets, sources, manpages, installation hooks, conditional feature builds, static variants, and library dependencies for util-linux `sys-utils`.

## Build Targets Covered

- Memory/CPU tools: `lsmem`, `chmem`, `lscpu`, `chcpu`.
- IPC and scheduling tools: `ipcmk`, `ipcrm`, `ipcs`, `lsipc`, `renice`.
- Interrupt tools: `irqtop`, `lsirq`.
- Device/block tools: `fstrim`, `blkdiscard`, `blkzone`, `blkpr`, `losetup`, `zramctl`, `wdctl`.
- Mount/namespace tools: `mount`, `umount`, `mountpoint`, `unshare`, `nsenter`, `pivot_root`, `switch_root`.
- Misc system utilities: `flock`, `choom`, `rfkill`, `setpgid`, `setsid`, `readprofile`, `tunelp`, `ctrlaltdel`, `fsfreeze`, `ldattach`, `rtcwake`, `setarch`, `eject`, `prlimit`, `swapon`, `swapoff`, `fallocate`, `hwclock`, `setpriv`.

## Control Flow And Behavior

- Each `if BUILD_*` block adds programs to the relevant install class (`bin_PROGRAMS`, `sbin_PROGRAMS`, `usrbin_exec_PROGRAMS`, `usrsbin_exec_PROGRAMS`), adds manpages and `.adoc` sources, and sets source files plus `LDADD`/`CFLAGS`.
- `dmesg` adds a `test_dmesg` check program compiled with `-DTEST_DMESG`.
- `blkdiscard` conditionally links `libblkid.la` when libblkid is built.
- `irqtop` links either slang or ncurses depending on availability.
- `mount` and `umount` use SUID flags and install hooks to chown/chmod setuid root when configured.
- Static variants are conditionally defined for `losetup`, `mount`, `umount`, `unshare`, and `nsenter`.
- `setarch` generates architecture alias links and corresponding manpage symlinks.
- `fstrim` optionally installs systemd service/timer units.

## Dependencies

- Internal libraries: `libcommon.la`, `libmount.la`, `libblkid.la`, `libsmartcols.la`, `libtcolors.la`, `libcommon_logindefs.la`.
- Optional external libraries/macros: realtime, POSIX IPC, message queues, ncurses/slang, SELinux, systemd, RTAS, audit, math, cap-ng.
- Shared generated variables: `MANPAGES`, `dist_noinst_DATA`, `PATHFILES`, `EXTRA_DIST`, `INSTALL_EXEC_HOOKS`, `UNINSTALL_HOOKS`.

## Risks And Invariants

- Conditional blocks must match configure-time `BUILD_*` and `HAVE_*` definitions or installed utilities/manpages diverge from compiled features.
- SUID mount/umount installation behavior depends on `MAKEINSTALL_DO_CHOWN` and `MAKEINSTALL_DO_SETUID`.
- Generated `setarch` links are architecture-dependent and must be mirrored by uninstall hooks.
- Programs using internal library headers add the correct include directory flags, such as libmount/libsmartcols/libblkid include dirs.
