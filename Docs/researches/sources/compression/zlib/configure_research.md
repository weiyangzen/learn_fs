# sources/compression/zlib/configure

Purpose: portable shell configure script for the traditional zlib make build. It detects compilers, platform linker flags, library naming, feature macros, optional sanitizer/coverage settings, and s390x vector CRC support, then generates `Makefile`, `zlib.pc`, and `zconf.h`.

Important functions/variables: shell helpers `leave`, `show`, `try`, and `tryboth`; command-line options such as `--prefix`, `--static`, `--shared`, `--solo`, `--cover`, `--zprefix`, `--64`, `--archs`, `--const`, `--warn`, sanitizer flags, `--insecure`, and `--disable-crcvx`. Key outputs include `CC`, `CFLAGS`, `SFLAGS`, `LDSHARED`, `SHAREDLIB*`, `OBJC`, `PIC_OBJC`, `VGFMAFLAG`, `ALL`, and `TEST`.

Control flow: logs invocation to `configure.log`, determines source directory and cross-prefix from `CHOST`, parses options, detects GCC/Clang, assembles flags by platform, probes shared-library support, checks `size_t`, large-file support, `fseeko`, `strerror`, `unistd.h`, `stdarg.h`, printf variants, hidden visibility, s390x, and s390x VX intrinsics. It edits `zconf.h`, substitutes variables into `Makefile.in` and `zlib.pc.in`, and cleans temporary probes through `leave`.

State and persistence: appends `configure.log`; writes `zconf.h`, `Makefile`, and `zlib.pc`; creates temporary `ztest$$` files removed on exit.

Dependencies and integration: pairs with `Makefile.in`, `zconf.h.in`, `zlib.pc.in`, system shell tools, C compiler, archiver, ranlib, nm, and optional cross tools. CI `configure.yml` exercises this path extensively.

Risks: shell substitution writes unescaped user-provided paths/flags into sed replacements, so unusual characters can break generation. Cross builds cannot run probe executables for some checks. Security-related printf fallback requires `--insecure` but the script records warnings rather than universally aborting.

Test signals: generated `make test`, `make test64`, configure CI cross-builds, and `configure.log` probe output provide diagnostics.
