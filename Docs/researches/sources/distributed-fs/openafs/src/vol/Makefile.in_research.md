## sources/distributed-fs/openafs/src/vol/Makefile.in

Purpose: Automake-style template for building and installing the OpenAFS volume package library and related utilities: `vlib.a`, salvager, `volinfo`, `volscan`, `vol-bless`, `fssync-debug`, optional `xfs_size_check`, headers, and support objects.

Important APIs/targets: variables include `LIBS`, `MODULE_CFLAGS` with `FSSYNC_BUILD_SERVER`/`FSSYNC_BUILD_CLIENT`, `PUBLICHEADERS`, `VLIBOBJS`, and `OBJECTS`. Major targets are `all`, top-level library/header install copies, `install`, `dest`, object dependencies, `vlib.a`, `salvager`, `volinfo`, `volscan`, `fssync-debug`, `vol-bless`, `xfs_size_check`, `clean`, `check-splint`, and helper `gi`/`namei_map`.

Control flow: `all` builds generated version info, libraries, binaries, optional platform tools, and exported headers. `vlib.a` archives core volume objects including `clone.o`, `common.o`, and `daemon_com.o`. Install/dest targets create server/library/include directories and copy programs and public headers into packaged locations. Program targets link specific main/object combinations with `LIBS`, roken, and platform libraries. `check-splint` runs static analysis over the volume source set.

State and persistence: build artifacts are object files, archives, generated `AFS_component_version_number.c`, server binaries, and installed headers/programs. No runtime state is handled here, but build flags determine whether daemon sync code compiles server/client features.

Dependencies: top-level config make fragments, LWP config, OpenAFS static libraries (`libcmd`, `util`, `libdir`, `librx`, crypto, `liblwp`, `libsys`, `libacl`, `libopr`), roken, platform C compiler/linker macros, and source headers.

Integration points: this template is consumed by the OpenAFS configure/build system. It exports headers under `afs/` for other components and packages volume tools used by fileserver, volserver, salvager, and diagnostics workflows. The `VLIBOBJS` list ties `clone.c`, `common.c`, and `daemon_com.c` into the shared volume library.

Risks: object/header dependency drift can cause stale or missing rebuilds. Platform-specific `listinodes.o` and `gi` cases are easy to break in cross-platform changes. Adding a new public header or vlib object requires updating multiple target lists and install/dest sections. `clean` must track generated binaries and version files. Link order matters because this is static-library-heavy legacy C.

Test signals: configure/build on Linux and at least one non-Linux path, `make all`, staged `install`/`dest`, exported header presence, archive contents containing expected `VLIBOBJS`, optional `xfs_size_check` behavior when enabled, `clean` removing generated artifacts, and `check-splint` command construction.
