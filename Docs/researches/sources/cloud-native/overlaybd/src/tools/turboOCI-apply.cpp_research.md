# sources/cloud-native/overlaybd/src/tools/turboOCI-apply.cpp

Purpose: CLI specialized for applying OCI tar or tar.gz layers into OverlayBD TurboOCI v1 images, with optional EROFS output and tar-header import/export modes.

Important APIs/types/functions: `dump_tar_headers`, `UnTar::dump_tar_headers`, `UnTar::extract_all`, `LibErofs::extract_tar`, `create_gz_index`, `ZFile::zfile_open_ro`, `create_overlaybd`, `create_ext4fs`, and `ImageConfigNS::ImageConfig`.

Control flow: parses filesystem type, mkfs, service config, gzip index path, import/export flags, input path, and image config path. It opens input, unwraps zfile if present, detects gzip and builds a gzip index, optionally exports tar headers and exits, validates image config existence, creates an OverlayBD image file, then either extracts through `LibErofs` or ext4 `UnTar` with TurboOCI metadata generation.

State and persistence: writes image filesystem data, gzip metadata, and optionally tar-header output. EROFS import uses lower-layer count from image config to decide root behavior.

Dependencies/integration: integrates zfile, gzip index, tar metadata, EROFS, extfs, image-service config, and TurboOCI extraction.

Risks: `raw` variable exists but is never exposed as a CLI option, so base-file selection always follows image-file mode. `image_config_path` is optional in CLI but required for most paths. Input zfile wrapping changes `tarf` ownership assumptions.

Test signals: cover gzip index generation, zfile input, ext4 and EROFS targets, tar-header export/import, missing config, and mkfs behavior.
