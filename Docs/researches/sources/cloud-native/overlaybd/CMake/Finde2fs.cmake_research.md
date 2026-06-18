<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Finde2fs.cmake -->
# sources/cloud-native/overlaybd/CMake/Finde2fs.cmake

Purpose: Resolves ext2fs either from the system or from a pinned fork build.

APIs and control flow: If `ORIGIN_EXT2FS` is false, FetchContent clones `data-accelerator/e2fsprogs`, runs its `build.sh`, creates target `libext2fs_build`, and imports `${LIBEXT2FS_INSTALL_DIR}/lib/libext2fs.so`. Otherwise it finds `ext2fs/ext2fs.h` and library `ext2fs`.

State and persistence: Bundled builds create an installed lib/include tree under the e2fsprogs source build directory and later install lib files into `/opt/overlaybd`.

Dependencies and integration: `Findphoton.cmake` adds `photon_obj` dependency on `libext2fs` when bundled.

Risks and test signals: The custom build script and shared library path are fragile. Ext4 base layer and mkfs/apply workflows validate this dependency.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Finde2fs.cmake -->
