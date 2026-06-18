# sources/distributed-fs/lizardfs/cmake/DownloadExternal.cmake

## Purpose
This helper downloads, verifies, extracts, and optionally patches bundled external dependencies when they are not already present under `external/`.

## Important APIs, Types, and Functions
`download_external(PCKG_NAME PCKG_DIR_NAME PCKG_URL [md5] [patch_name])` caches the package directory name, downloads a zip to the binary directory with optional expected MD5, unzips it into the source `external` directory, verifies the expected directory exists, and optionally applies a patch from `external/<patch_name>.patch`.

## Control Flow and State
The function is a configure-time side-effect tool. If the target source directory exists, it just reports the package as found. Otherwise it performs network download, unzip, and patch commands, failing configuration with `FATAL_ERROR` on any problem.

## Dependencies and Integration Points
`Libraries.cmake` uses it for NFS-Ganesha and ntirpc when `ENABLE_NFS_GANESHA` is enabled. It depends on CMake `file(DOWNLOAD)`, an `unzip` executable, and a `patch` executable when patching.

## Risks and Edge Cases
The function writes into the source tree during configure, which can dirty checkouts and break read-only source builds. It has network and tool availability risks. The unzip error message references `${ARCHIVE_NAME}`, which is not defined. Patch paths are hard-coded relative to `external`.

## Test Signals
Configure output reports download, unpack, patch, or found status. Fatal configure errors are the main failure signal.
