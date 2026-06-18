# sources/compression/zlib/contrib/zlib1-dll/CMakeLists.txt

Purpose: CMake build, install, and test definition for legacy Windows `zlib1.dll` and `zlibwapi.dll` binaries containing zlib plus minizip.

Important APIs, types, and functions: Requires Windows, defines options for bzip2, install, and testing, includes CMake feature-check and package helper modules, generates a configured `zconf.h`, defines public/private header and source lists, creates shared libraries `zlib1` and `zlibwapi`, and exports aliases `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.

Control flow: The script aborts on non-Windows. If embedded in zlib, options mirror top-level settings. It optionally finds BZip2, checks platform functions/types/headers, configures `zconf.h`, builds both DLL variants from zlib and minizip sources, applies compile definitions and include paths, installs targets/config files/headers/license, and optionally adds the test subdirectory.

State and persistence: Writes `zconf.h.cmakein`, `zconf.h`, installed CMake package files, exported target files, headers, DLL import artifacts, and optional PDB files. It also uses cache/internal variables such as `ZLIB_CONF_WRITTEN` and `ZCONF_IN_ZLIB1`.

Dependencies and integration points: Depends on core zlib sources, minizip sources, Windows resource files, CPack, GNUInstallDirs, CMakePackageConfigHelpers, and optional BZip2. It is consumed by its test templates and by downstream `find_package(ZLIB1DLL)`.

Risks: The `foreach(item IN LISTS ${ZCONF_CONTENT})` pattern is suspicious because file content is not a list variable name. Installation config uses `INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/zlib` while install files go to `cmake/zlib1dll`, which may affect relocatability metadata. Non-Windows builds hard fail by design. Exported package naming uses hyphenated project variables, which CMake supports but is easy to mishandle.

Test signals: Test subdirectory validates install/package import and add-subdirectory consumption. Build success also compiles the combined zlib/minizip DLL sources and generated config.
