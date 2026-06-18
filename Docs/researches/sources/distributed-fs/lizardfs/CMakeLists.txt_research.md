# sources/distributed-fs/lizardfs/CMakeLists.txt

## Purpose
This is the top-level LizardFS CMake build definition. It establishes build policy, install paths, feature toggles, package versioning, compiler flags, platform definitions, dependency/environment checks, generated config header output, and the project subdirectory graph.

## Important APIs, Types, and Functions
The file defines many CMake options, including tests, docs, client library, NFS-Ganesha, crc, tracing, allocators, polonaise, ccache, official build suffixes, and warning behavior. It sets install subdirectories via `GNUInstallDirs`, default runtime values such as user/group/master host, package version variables, C/C++ flags, and preprocessor definitions. It includes `EnvTests`, `Libraries`, `CollectSources`, and `CreateUnitTest`, then calls `configure_file(config.h.in config.h)`.

## Control Flow and State
Configuration starts by rejecting in-source builds. It optionally enables ccache, sets install path aliases, logs option values, and derives `PACKAGE_VERSION_SUFFIX` from Git SHA, official build state, or RC number. Enabling tests forces `THROW_INSTEAD_OF_ABORT`, `ENABLE_CLIENT_LIB`, `BUILD_TESTS`, `BUILD_UTILS`, and debug logging. `ENABLE_CLIENT_LIB` enables PIC targets. Build type defaults to Debug. After environment and library detection, it adds subsystem directories conditionally: common mount components always, non-MinGW daemons/tools/docs/FUSE mount conditionally, tests when enabled, and uraft when enabled.

## Dependencies and Integration Points
The file integrates with local CMake modules in `cmake/`, generated `config.h`, external bundled libraries, source subtrees under `src/`, docs, tests, utilities, and platform-specific flags for SunOS and MinGW. It relies on `git rev-parse HEAD` when available for development version suffixes.

## Risks and Edge Cases
Although `ENABLE_WERROR` defaults off, the file unconditionally adds `-Werror`, so warning sensitivity may be higher than the option name implies. Dependency discovery must run before checking `Boost_INCLUDE_DIRS`; missing Boost headers are fatal. Tests silently force other options, which can surprise package builds. In-source build protection is strong but requires cleanup after failed attempts. CMake minimum version is old (`2.8`), constraining available constructs.

## Test Signals
Configuration-time signals include fatal errors for in-source builds, missing Boost, missing FUSE on non-MinGW, incompatible allocator options, and missing request-log dependencies. Build/test signal comes from enabling `BUILD_TESTS` and adding `src/unittests` and `tests`.
