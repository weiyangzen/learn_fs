# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/CMakeLists.txt

## Purpose
Fetches, configures, builds, and links the external `erofs-utils` library, then builds OverlayBD's `erofs_lib` wrapper sources.

## Important APIs and Types
Uses `FetchContent_Declare` pinned to erofs-utils commit `eec6f7a2755dfccc8f655aa37cf6f26db9164e60`, runs `autogen.sh`, `configure`, and `make`, caches include/config/static-library paths, builds local `erofs_lib`, force-includes erofs-utils `config.h`, and links against `liberofs.a`.

## Control Flow
Configure-time `execute_process` builds the third-party C library before compiling local C++ wrapper code. Tests are added when `BUILD_TESTING` is enabled.

## State and Persistence
FetchContent populates and builds erofs-utils under the CMake build tree. No application runtime state is defined.

## Dependencies and Integration Points
Requires network/source availability at configure time unless FetchContent is cached, autotools, make, and a toolchain compatible with erofs-utils.

## Risks
Running build commands during CMake configure can make configuration slow and fragile. The configuration disables compression and multithreading features, so wrapper behavior depends on those chosen options. Network fetches reduce reproducibility without a populated cache.

## Test Signals
Successful FetchContent population, autotools configure/make, local `erofs_lib` compilation, and downstream EROFS tests are the main signals.
