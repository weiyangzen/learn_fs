# sources/cloud-native/overlaybd/src/tools/overlaybd-apply.cpp

Purpose: CLI that applies an OCI tar layer, optionally gzip/zstd-compressed, into an OverlayBD image or raw image file.

Important APIs/types/functions: defines `FIFOFile` for full-count FIFO reads and uses `create_overlaybd`, `create_ext4fs`, `UnTar`, `create_gz_index`, `open_gzfile_adaptor`, `open_zstdfile_adaptor`, `new_sha256_file`, and `ImageFile::get_base`.

Control flow: CLI parses raw/mkfs/service config/gzip index/checksum/input/image config options, initializes Photon, opens the destination image, creates an ext4 filesystem view, opens the layer, detects FIFO/gzip/zstd/plain tar input, optionally builds a gzip index for TurboOCI, wraps the stream in SHA256 tracking, then extracts all tar entries. After extraction it compares the calculated `sha256:` digest with the expected value when supplied.

State and persistence: writes filesystem mutations into the OverlayBD or raw image file, may create a gzip index file, and optionally formats the target filesystem. It reads base-layer state from `ImageFile::get_base` for overlay-aware extraction.

Dependencies/integration: integrates OCI tar parsing, gzip/zstd adaptors, OverlayBD image-service configs, extfs, and checksum validation.

Risks: checksum validation only covers bytes consumed through the wrapper; the wrapper drains trailing bytes during final digest calculation. FIFO reads require exact requested lengths and can block if producers stall. Errors terminate the process instead of returning structured status.

Test signals: apply integration should cover plain tar, gzip, zstd, FIFO input, checksum mismatch, raw mode, mkfs mode, and TurboOCI gzip-index generation.
