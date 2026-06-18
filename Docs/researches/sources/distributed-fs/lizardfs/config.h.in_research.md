# sources/distributed-fs/lizardfs/config.h.in

## Purpose
This template becomes generated `config.h`, collecting package version constants, install paths, defaults, chunk geometry, portability macros, optional dependency macros, and compiler compatibility fixes for LizardFS C/C++ code.

## Important APIs, Types, and Functions
It defines static macros such as `LIZARDFS_HAVE_PWD_H`, `LIZARDFS_HAVE_STRERROR_R`, and `MASTERINFO_WITH_VERSION`; substitutes package version fields and `LIZARDFS_VERSHEX`; substitutes protocol base, block counts/sizes, install paths, and default daemon/user settings; defines a GCC 4.6 workaround for `override`; and contains many `#cmakedefine` entries for includes, structs, functions, libraries, endianness, debug, CRC, allocator, CPU, and standard-library features.

## Control Flow and State
CMake `configure_file(config.h.in config.h)` performs variable substitution and emits defines for variables set during `EnvTests.cmake`, `Libraries.cmake`, and top-level configuration. The generated header is included from the binary directory and used at compile time only.

## Dependencies and Integration Points
This template is the destination for top-level CMake variables, dependency discovery variables, and environment test outputs. It is included by source files guarded by `LIZARDFS_HAVE_CONFIG_H`.

## Risks and Edge Cases
Hard-coded "extra definitions" bypass actual checks and may become stale. Any mismatch between variable names in CMake probes and `#cmakedefine` entries silently disables expected macros. Install-path substitutions embed absolute paths into binaries/config behavior.

## Test Signals
Generated `config.h` content is the main signal. Cross-platform builds validate conditional macro coverage. Missing macros surface as compile failures or disabled optional code paths.
