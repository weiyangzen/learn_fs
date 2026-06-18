<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/baselayers/CMakeLists.txt -->
# sources/cloud-native/overlaybd/baselayers/CMakeLists.txt

Purpose: Builds and installs the bundled ext4 base layer artifact.

APIs and control flow: A custom command extracts `ext4_64.tar.gz` into `${EXECUTABLE_OUTPUT_PATH}` as `ext4_64`; target `baselayer` is built by default and installs the file to `/opt/overlaybd/baselayers`.

State and persistence: Produces `build/output/ext4_64` and package/install content.

Dependencies and integration: Used by image creation/apply paths that need a filesystem base layer.

Risks and test signals: Tarball integrity and extraction destination are the critical risks. CI `overlaybd-apply --mkfs` exercises this asset indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/baselayers/CMakeLists.txt -->
