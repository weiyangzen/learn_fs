# sources/cloud-native/overlaybd/src/tools/CMakeLists.txt

Purpose: defines the OverlayBD command-line tool build targets for creating, applying, committing, merging, and zfile-processing OverlayBD layers.

Important APIs/types/functions: creates executables `overlaybd-commit`, `overlaybd-merge`, `overlaybd-create`, `overlaybd-zfile`, `overlaybd-apply`, and `turboOCI-apply`; creates `checksum_lib` from `sha256file.cpp`; attaches Photon include paths and links `photon_static`, `overlaybd_lib`, `overlaybd_image_lib`, and `checksum_lib` where needed.

Control flow: each CLI source is mapped directly to one executable target. Apply and TurboOCI tools receive RapidJSON includes, image-service linkage, and install RPATH. `checksum_lib` is linked only into `overlaybd-apply` because that tool can validate an uncompressed layer checksum while streaming extraction.

State and persistence: no runtime state; it controls install persistence by placing tool binaries under `/opt/overlaybd/bin` and setting RPATH to `/opt/overlaybd/lib` for binaries that load image libraries.

Dependencies/integration: integrates the tools with the broader OverlayBD CMake build, Photon runtime, image service library, zfile/tar/LSMT code, and optional checksum library.

Risks: target linkage is manually maintained, so missing library dependencies will surface as link or runtime loader failures. `overlaybd-zfile` and `overlaybd-commit` do not get install RPATH here, unlike image-service tools.

Test signals: build success verifies target composition. Runtime coverage is expected through the individual tool tests or integration scripts that call installed binaries.
