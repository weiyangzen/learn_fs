# sources/distributed-fs/ceph-client/tools/usb/usbip/configure.ac

Purpose: `configure.ac` defines the usbip-utils Autoconf configuration. It prepares package metadata, libtool versioning, compiler flags, feature checks, library checks, and generated Makefiles for the usbip userspace tools.

Important macros and settings: `AC_INIT` declares `usbip-utils` version `2.0`; `AC_DEFINE([USBIP_VERSION], [0x00000111])` defines protocol/tool version; `LIBUSBIP_VERSION` is `0:1:0`; `LT_INIT` enables libtool. `EXTRA_CFLAGS` enforces `-Wall -Werror -Wextra -std=gnu99`. Header/type/function checks validate common POSIX networking support. The libudev check is mandatory. Optional TCP wrappers are enabled if requested or auto-detected. `--with-usbids-dir` sets `USBIDS_DIR`, and `--with-fortify` can add `_FORTIFY_SOURCE=2`.

Control flow and integration: after checks, `AC_CONFIG_FILES` emits `Makefile`, `libsrc/Makefile`, and `src/Makefile`. The substitutions are consumed by Automake files for include paths, `USBIDS_FILE`, compiler flags, and library versioning.

State, dependencies, risks, and tests: generated state includes `config.h`, Makefiles, and configure cache/logs. Dependencies are Autoconf 2.59+, Automake, Libtool, a C compiler, libudev headers/library, and optionally libwrap. Risks include `-Werror` breaking builds on newer compilers, default usb.ids path mismatch across distributions, and deprecated `AC_TRY_LINK`. Test signals are successful `./configure`, correct `config.h` defines, and compile/link of `libusbip`, `usbip`, and `usbipd`.
