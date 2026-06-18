# sources/cloud-native/ostree/src/rofiles-fuse/Makefile-inc.am

Purpose: automake fragment building the `rofiles-fuse` helper binary.

Important build entries: adds `rofiles-fuse` to `bin_PROGRAMS`, sets `rofiles_fuse_SOURCES` to `src/rofiles-fuse/main.c`, supplies `_GNU_SOURCE`, `_FILE_OFFSET_BITS=64`, FUSE, internal GIO Unix, libostree, and libglnx include flags, and links `libglnx.la`, FUSE libs, GIO Unix libs, and `libostree-1.la`.

Control flow/state: build metadata only; no runtime flow.

Dependencies/integration: ties `main.c` to configured FUSE version and libostree internals. The include paths allow use of private libostree headers.

Risks: build correctness depends on `BUILDOPT_FUSE_CFLAGS/LIBS` and `FUSE_USE_VERSION` being defined through `config.h`. Linkage against libostree means the helper must track ABI/build changes.

Test signals: build/test jobs compiling `rofiles-fuse`; runtime behavior needs FUSE-capable integration tests.
