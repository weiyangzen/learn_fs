# sources/distributed-fs/lizardfs/src/mount/client/CMakeLists.txt

## Purpose
This CMake file builds and installs the LizardFS client libraries: C API, C++ wrapper, shared dynamic-mount shim, and headers.

## Important APIs, Types, And Functions
- `shared_add_library(lizardfs-client client.cc lizardfs_c_api.cc client_error_code.cc)` builds the C API library.
- `shared_add_library(lizardfs-client-cpp client.cc client_error_code.cc)` builds the C++ wrapper without C API implementation.
- `add_library(lizardfs-client_shared SHARED ...)` creates an installed shared object named `liblizardfs-client`.
- `add_library(lizardfsmount_shared SHARED ${MOUNT_SOURCES} lizard_client_c_linkage.cc)` creates the dynamic shim loaded by `Client`.
- `install(FILES lizardfs_c_api.h ... lizardfs_error_codes.h ...)` installs public headers.

## Control Flow
The script collects client sources, defines shared/PIC target variants, links against `mount` or `mount_pic`, links C dynamic-loader libraries where needed, and installs targets to library/include subdirectories.

## State And Persistence
It affects build/install artifacts only. The produced `lizardfsmount_shared` is loaded at runtime by `client.cc`.

## Dependencies And Integration Points
It relies on parent `MOUNT_SOURCES`, project shared-library macros, `${CMAKE_DL_LIBS}`, `mount_pic`, and install directory variables.

## Risks
- `lizardfsmount_shared` embeds all mount sources plus linkage wrappers; ABI drift between exported wrappers and `client.cc` dlsym list will fail at runtime.
- Multiple targets compile overlapping source files, so compile definitions and PIC settings must remain consistent.

## Test Signals
Build tests should verify all targets build with `ENABLE_CLIENT_LIB`, installed headers compile from C and C++, and `Client::linkLibrary` can load `liblizardfsmount_shared.so`.
