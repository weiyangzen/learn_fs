# sources/compression/zlib/Makefile.in

Purpose: template Makefile for zlib's traditional configure/make build, tests, install, coverage, and cleanup.

Important targets/variables: variables for compiler, flags, library names, install prefixes, object lists, PIC objects, QEMU runner, and s390x vector flags. Targets include `all`, `static`, `shared`, `test`, `teststatic`, `testshared`, `test64`, `cover`, `libz.a`, shared library, examples, install/uninstall, docs, zconf, minizip-test, clean, distclean, and tags.

Control flow: `configure` rewrites variables and target prerequisites. Static builds create `libz.a`, `example`, and `minigzip`; shared builds create versioned shared library symlinks plus shared examples. Tests pipe “hello world” through minigzip and run example programs, optionally via `QEMU_RUN`. Install copies libraries, symlinks, man page, pkg-config file, and headers under `DESTDIR`.

State and persistence: creates object files, PIC `.lo` files, `objs/`, libraries, symlinks, examples, coverage files, docs, installed files, and generated placeholder Makefile on `distclean`.

Dependencies and integration: driven by `configure`, uses core zlib sources, optional `contrib/crc32vx`, test sources, `zlib.map`, `zlib.pc`, system `ar`, `ranlib`, `ldconfig`, `tar`, `groff`, `ps2pdf`, and shell utilities.

Risks: manual dependency lists must stay synchronized with source headers. Shared library symlink handling assumes Unix-like semantics. Test temporary cleanup uses shell PID suffixes and can leave files after interrupted runs. `LLVM_GCOV_FLAG` default has a spelling placeholder that configure is expected to replace for coverage.

Test signals: `make test`, `make test64`, minigzip pipe tests, example programs, and `cover`/`infcover` provide runtime and coverage signals for the configure path.
