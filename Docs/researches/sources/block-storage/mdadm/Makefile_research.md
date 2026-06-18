# File Research: sources/block-storage/mdadm/Makefile

This Makefile builds, tests, installs, and packages the mdadm userspace tools. It covers the main `mdadm` binary, `mdmon`, static/optimized variants, manpage generation, udev rules, systemd units, helper test binaries, and distribution hooks.

Build configuration:
- `CC` defaults to `$(CROSS_COMPILE)gcc` when not explicitly set.
- `CXFLAGS` defaults to optimized fortified builds; `CWFLAGS` enables strict warnings, format security, stack protector, PIE, and selected compiler-specific warning/optimizer flags.
- Feature probes add flags for implicit fallthrough, format overflow, stringop overflow, no strict overflow, no delete-null-pointer checks, and signed overflow wrapping when the compiler supports them.
- `DEFAULT_OLD_METADATA` selects default metadata `0.90`; otherwise default metadata is `1.2`.
- Paths such as `SYSCONFDIR`, `CONFFILE`, `RUN_DIR`, `MAP_DIR`, `MDMON_DIR`, `FAILED_SLOTS_DIR`, `SYSTEMD_DIR`, `LIB_DIR`, `BINDIR`, `MANDIR`, and `MISCDIR` are configurable.
- Corosync and libdlm availability are detected through `pkg-config`; missing packages add `-DNO_COROSYNC` or `-DNO_DLM`.
- libudev is linked unless `-DNO_LIBUDEV` appears in `CXFLAGS`.
- Version and release-date defines are generated from git when `.git` is present.
- `USE_PTHREADS=1` is enabled by default for glibc TLS ABI safety around clone-like behavior in mdmon.

Object groups:
- `OBJS` defines the main `mdadm` binary objects, including command modules (`Manage.o`, `Assemble.o`, `Build.o`, `Create.o`, `Detail.o`, `Examine.o`, `Grow.o`, `Kill.o`, `Query.o`, `Incremental.o`, `Dump.o`) plus metadata backends, sysfs, maps, platform, bitmap, checksums, and utility code.
- `MON_OBJS` defines the `mdmon` build and includes monitor/managemon code plus shared metadata and utility objects.
- `CHECK_OBJS` is used by `raid6check`.
- `STATICSRC`/`STATICOBJS` add `pwgr.o` for the static mdadm build.
- `SRCS` and `MON_SRCS` are derived from object lists.

Main targets:
- `all` builds `mdadm` and `mdmon`.
- `man` builds rendered manpage text outputs.
- `everything` and `everything-test` build normal tools, helper tools, optimized binaries, and manpages.
- `mdadm`, `mdadm.static`, `mdadm.Os`, `mdadm.O2`, `mdmon`, and `mdmon.O2` link the respective binaries.
- The generic `%.o: %.c` rule compiles with configured CFLAGS/CPPFLAGS/Coverity flags.
- `sha1.o` has a special compile rule adding `-DHAVE_STDINT_H`.
- `test_stripe`, `raid6check`, and `swap_super` are auxiliary/test tools.
- `check_rundir` verifies the parent of `RUN_DIR` exists unless `CHECK_RUN_DIR=0`.

Generated files:
- `mdadm.8` and `mdadm.conf.5` are generated from `.in` files by substituting default metadata, map path, and config paths.
- `.man` targets render manpages through `man -l`.

Install/uninstall:
- `install` runs `install-bin`, `install-man`, and `install-udev`.
- `install-static` installs the static binary and manpages.
- `install-bin` installs `mdadm` and `mdmon` into `$(DESTDIR)$(BINDIR)`.
- `install-man` installs mdadm, mdmon, md, and mdadm.conf manpages.
- `install-udev` installs md RAID udev rules after substituting `BINDIR`.
- `install-systemd` installs systemd units, shutdown hook, and the `mdcheck` helper after substituting configured paths.
- `uninstall` removes installed binaries, manpages, udev rules, systemd units, shutdown hook, and mdcheck helper.

Maintenance targets:
- `test` builds required tools and instructs the user to run `./test` as root.
- `clean` removes built binaries, objects, generated manpages, optimized/static variants, test tools, coverage output, and temporary merge/patch files.
- `dist` and `testdist` run `./makedist` after clean or full test-build preparation.
- `TAGS` generates Emacs tags for headers and C files.
- If `distropkg/Makefile` exists, it is included for distribution-specific packaging rules.

Important implementation notes:
- `Grow.o`, `Incremental.o`, and `Kill.o` are all part of the main `mdadm` binary; `Kill.o` is also part of `mdmon`.
- The build is intentionally security-hardened by default: PIE, immediate binding/noexecstack linker flags, stack protector, fortify defines, and format-security errors.
- Installation rules transform templates into temporary files before install, but echo the final install action depending on make’s silent flag.
- The Makefile is project-specific and does not use autotools here; compiler and feature detection are done inline with make shell probes.
