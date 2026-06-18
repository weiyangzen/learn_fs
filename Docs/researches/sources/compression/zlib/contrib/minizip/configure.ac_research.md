# sources/compression/zlib/contrib/minizip/configure.ac

Purpose: supplies the Autoconf entry point for the minizip Automake/libtool build.

Important APIs/types/functions: `AC_INIT`, `AC_CONFIG_SRCDIR`, `AM_INIT_AUTOMAKE`, `LT_INIT`, `AC_ARG_ENABLE([demos])`, `AM_CONDITIONAL([COND_DEMOS])`, host case for `WIN32`, `AC_CHECK_HEADER([unistd.h])`, `AC_CONFIG_FILES`, and `AC_OUTPUT`.

Control flow: configure initializes package metadata, enables libtool, checks whether demo programs should be built, detects MinGW-like hosts, sets the `WIN32` conditional, probes `unistd.h`, and generates `Makefile` and `minizip.pc`.

State and persistence: generates the configure-time Makefile and pkg-config output; substitutes `HAVE_UNISTD_H`.

Dependencies/integration: pairs with `Makefile.am` and the minizip source tree. Bug report metadata points at Red Hat Bugzilla.

Risks: feature detection is minimal compared with CMake, with no explicit large-file or BZip2 checks. Demo option defaults to disabled. Host detection is narrow.

Test signals: successful autoreconf/configure and build; no runtime tests are declared here.
