<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findtcmu.cmake -->
# sources/cloud-native/overlaybd/CMake/Findtcmu.cmake

Purpose: Fetches the Photon-adapted libtcmu fork used by `overlaybd-tcmu`.

APIs and control flow: FetchContent clones `data-accelerator/photon-libtcmu` at a pinned commit and temporarily disables nested testing. It exposes `TCMU_INCLUDE_DIR`.

State and persistence: Builds a CMake subdependency consumed as `tcmu_static`.

Dependencies and integration: `src/main.cpp` includes libtcmu and SCSI headers to register the `overlaybd` TCMU subtype.

Risks and test signals: Kernel/user ABI mismatches appear at daemon startup or configfs device creation. CI E2E configfs tests validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findtcmu.cmake -->
