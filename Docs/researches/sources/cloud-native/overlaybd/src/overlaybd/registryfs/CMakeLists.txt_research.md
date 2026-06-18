# sources/cloud-native/overlaybd/src/overlaybd/registryfs/CMakeLists.txt

## Purpose
Builds the static `registryfs_lib` target from all registryfs C++ sources.

## Important APIs and Types
Uses `file(GLOB SOURCE_REGISTRYFS "*.cpp")`, requires CURL, and adds CURL, RapidJSON, and Photon include directories to the target.

## Control Flow
CMake discovers local `.cpp` files, creates a static library, and publishes include paths needed by consumers.

## State and Persistence
No runtime state is defined. Build output is the static registry filesystem library.

## Dependencies and Integration Points
Integrates registry filesystem v1/v2 and uploader code into OverlayBD consumers that need remote OCI registry blob access.

## Risks
The glob includes every `.cpp` in the directory, so adding experimental files automatically changes the library. The target does not explicitly link CURL here, so linkage must be satisfied by consumers or other parent targets.

## Test Signals
Build success with CURL/RapidJSON/Photon configured and successful linkage by downstream OverlayBD binaries are the relevant signals.
