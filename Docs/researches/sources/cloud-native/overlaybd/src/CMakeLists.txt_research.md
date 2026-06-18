<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/CMakeLists.txt

Purpose: Builds the image service library and the `overlaybd-tcmu` daemon.

APIs and control flow: Finds CURL, OpenSSL, aio, and RapidJSON, links common system libs, adds `overlaybd`, compiles `overlaybd_image_lib` from image file/service, background download, prefetch, switch file, API server, and tools, then builds `overlaybd-tcmu` from `main.cpp`.

State and persistence: Installs daemon to `/opt/overlaybd/bin`, service unit to `/opt/overlaybd`, default config to `/etc/overlaybd`, credentials example to `/opt/overlaybd`, and bundled ext2fs libs when applicable.

Dependencies and integration: Links Photon, overlaybd libraries, tcmu, curl, OpenSSL, and aio.

Risks and test signals: Library order and imported variables are sensitive. Build, install, systemd start, and CTest validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/CMakeLists.txt -->
