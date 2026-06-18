# sources/distributed-fs/openafs/src/config/shlib-install.in

This companion script installs shared libraries and creates conventional unversioned and major-version symlinks. It parses `-d <dest>`, `-l <library>`, optional `-M <major>`, and `-m <minor>`, computes the built filename from `@SHLIB_SUFFIX@`, and runs `@INSTALL_DATA@` plus `ln -s -f`.

Control flow is platform-specific: AIX installs a `.shared` file, HP-UX installs either unversioned or major-only names, and the default path installs the full `lib.suffix.major.minor` and symlinks both `lib.suffix` and `lib.suffix.major` to it. The script persists files and symlinks under the destination tree.

Dependencies are autoconf substitutions, `INSTALL_DATA`, `ln`, and the calling Makefile having already built the expected filename. Integration is with the custom shared library build pipeline. Risks include missing quoting in one install line, platform symlink conventions that do not include minor versions, and no rpath handling. Test signals are package staging checks that all expected library names resolve and that repeated installs update symlinks idempotently.
