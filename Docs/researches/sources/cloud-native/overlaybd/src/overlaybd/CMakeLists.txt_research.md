<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/CMakeLists.txt

Purpose: Aggregates OverlayBD sublibraries into an interface target.

APIs and control flow: Adds registryfs, lsmt, zfile, zstd, cache, tar, gzip, gzindex, and optional stream convertor subdirectories, then defines `overlaybd_lib` as an interface library with Photon include dirs and links to all component libs.

State and persistence: No runtime state; establishes build graph.

Dependencies and integration: Consumed by `overlaybd_image_lib`, daemon, tools, and tests.

Risks and test signals: Interface target hides link ordering complexity. Full build and tool linking validate component coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/CMakeLists.txt -->
