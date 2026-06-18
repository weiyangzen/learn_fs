<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findphoton.cmake -->
# sources/cloud-native/overlaybd/CMake/Findphoton.cmake

Purpose: Fetches PhotonLibOS and wires it into OverlayBD.

APIs and control flow: Sets `PHOTON_ENABLE_EXTFS ON`, fetches PhotonLibOS `v0.6.17`, temporarily disables `BUILD_TESTING` while bringing Photon in, then records `PHOTON_INCLUDE_DIR`. It adds dependency edges from `photon_obj` to bundled CURL/OpenSSL and ext2fs targets when those options are active.

State and persistence: Photon is built as a CMake dependency and later linked as `photon_static`.

Dependencies and integration: Nearly all runtime code uses Photon filesystems, threads, HTTP, curl, metrics, and event loops.

Risks and test signals: Global `BUILD_TESTING` mutation is order-sensitive. Compile/link of all runtime targets is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findphoton.cmake -->
