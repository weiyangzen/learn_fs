# sources/compression/lz4/lib/Makefile

## Purpose
The library Makefile builds, installs, and uninstalls LZ4 static and shared libraries, generates pkg-config metadata, and handles platform-specific shared-library naming and Windows DLL resources.

## Important Targets and Variables
Version variables are extracted from `lz4.h` with `sed`. `BUILD_SHARED` and `BUILD_STATIC` gate library types. `SRCFILES`, `OBJFILES`, `LIBLZ4`, `LIBLZ4_EXP`, `SHARED_EXT`, `SHARED_EXT_MAJOR`, and `SHARED_EXT_VER` drive artifacts. Targets include `lib-release`, `lib`, `all`, `all32`, `liblz4.a`, `$(LIBLZ4)`, `liblz4`, `liblz4.pc`, `clean`, `install`, `uninstall`, and `listL120`.

## Control Flow
The default target is `lib-release`, which clears debug flags and builds libraries plus `liblz4.pc`. Shared library handling branches for Darwin, Windows-like environments, AIX, and POSIX. Windows builds generate `liblz4-dll.rc` from the template and compile it with `windres`; non-Windows builds use linker soname flags and symlinks. Install creates library, pkg-config, binary, and header directories and installs static/shared artifacts according to build flags.

## State and Persistence
Build outputs include objects, archives, shared libraries, symlinks, generated `.pc`, generated Windows `.rc`, import libraries, and temporary directories. Install/uninstall persist files under `DESTDIR` plus configured prefix paths.

## Dependencies and Integration Points
It includes `../build/make/lz4defs.make` and `../build/make/multiconf.make`, and relies on their platform variables and library helper macros. It integrates with pkg-config through `liblz4.pc.in` and Windows version resources through `liblz4-dll.rc.in`.

## Risks
Version extraction is duplicated with other build files and can drift if header formatting changes. The `uninstall` Windows conditional appears as `ifeq (WINBASED,yes)` rather than comparing `$(WINBASED)`, which may make that branch ineffective. Platform-specific soname and symlink behavior needs validation on each target OS.

## Test Signals
Run `make -C lib`, inspect produced static/shared artifacts and symlinks, run `make -C lib liblz4.pc`, build with `BUILD_SHARED=no` or `BUILD_STATIC=no`, and validate install paths under a temporary `DESTDIR`.
