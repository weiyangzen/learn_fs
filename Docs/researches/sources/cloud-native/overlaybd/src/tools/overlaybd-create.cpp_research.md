# sources/cloud-native/overlaybd/src/tools/overlaybd-create.cpp

Purpose: CLI that creates OverlayBD data/index files or a raw sparse image with a requested virtual size.

Important APIs/types/functions: local `open_file`, LSMT `LayerInfo`, `create_file_rw`, `WarpFileArgs`, `create_warpfile`, Photon localfile adaptors, UUID parsing, and extfs `make_extfs`.

Control flow: parses options for parent UUID, sparse RW, TurboOCI/fastoci, raw image, mkfs, data/index paths, and virtual size in GB. It opens new data/index files with exclusive create, converts size to bytes, then either truncates raw data file, creates a TurboOCI warp file, or creates a normal LSMT RW layer. Optional `--mkfs` formats the resulting file as extfs.

State and persistence: creates data and index files, stores LSMT metadata, optional parent UUID, sparse mode flag, virtual size, and optional filesystem structures.

Dependencies/integration: produces layer files later consumed by `overlaybd-apply` and `overlaybd-commit`; depends on Photon, LSMT, CLI11, and extfs.

Risks: virtual size multiplication can overflow for very large GB input. Raw mode still opens and later deletes/closes an index file even though it is unused. All errors are process-fatal.

Test signals: should cover raw, normal, sparse, TurboOCI, parent UUID, mkfs, pre-existing output failure, and invalid size.
