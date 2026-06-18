# sources/compression/zstd/lib/Makefile

Purpose: primary make entry point for building, cleaning, installing, and uninstalling libzstd static/shared libraries. It composes source lists from `libzstd.mk`, supports optional modules, selects platform-specific shared-library naming/link flags, and uses flag-derived object cache directories.

Important variables/targets: module toggles `ZSTD_LIB_COMPRESSION`, `ZSTD_LIB_DECOMPRESSION`, `ZSTD_LIB_DICTBUILDER`, `ZSTD_LIB_DEPRECATED`; `ZSTD_FILES`, `ZSTD_LOCAL_OBJ`, `VERSION`; `CPPFLAGS_DYNLIB`, `CPPFLAGS_STATICLIB`, `LDFLAGS_DYNLIB`; `libzstd.a`, `libzstd`, `lib`, `%-mt`, `%-nomt`, `%-release`, object pattern rules, `clean`, `libzstd-nomt`, `libzstd.pc`, `install-*`, and `uninstall`.

Control flow: module toggles prune incompatible components, then `libzstd.mk` supplies file/version lists. Without `BUILD_DIR`, library targets reinvoke make with `BUILD_DIR=obj/$(HASH_DIR)` to separate artifacts by flags. With `BUILD_DIR`, static and dynamic object directories are created, sources compile with dependency files, archives or shared libraries are linked, and final artifacts are copied/symlinked into `lib/`. Pattern suffix targets adjust threading and debug flags.

State and persistence: persistent outputs include `libzstd.a`, versioned shared libraries or Windows DLL/import libraries, `obj/` cached objects/dependencies, symlinks, and generated `libzstd.pc`. Install targets write into `DESTDIR`/prefix library/include/pkgconfig paths.

Dependencies/integration: make, compiler, archiver, platform `install`, `sed`, symlink command, `libzstd.mk`, source tree layout, and platform variables from included makefiles. It integrates with examples/contrib via recursive `make -C lib`.

Risks: recursive rebuild logic can be hard to reason about. `clean` removes all `obj/*` and library artifacts. Platform-specific soname/install behavior must stay correct for Darwin, AIX, Windows, BSD, SunOS, and Linux. Module toggles can silently disable dictbuilder/deprecated when compression/decompression are disabled.

Test signals: build `lib`, `libzstd.a`, `libzstd-mt`, `libzstd-nomt`, `lib-release`; run examples; verify generated pkg-config fields; install/uninstall under `DESTDIR`; inspect shared-library soname/symlinks.
