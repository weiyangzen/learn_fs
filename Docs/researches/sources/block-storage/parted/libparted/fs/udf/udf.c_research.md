# File Research: sources/block-storage/parted/libparted/fs/udf/udf.c

Purpose: Detection-only UDF filesystem backend.

Main interfaces: `udf_probe()` returns a duplicate of the input geometry when UDF is detected. `ped_file_system_udf_init()` and `_done()` register/unregister the `udf` type.

Control flow: `detect_udf()` requires both a Volume Recognition Sequence with `NSR02` or `NSR03` and a valid Anchor Volume Descriptor Pointer. It checks VRS descriptors beginning at byte offset 32768, first using 2048-byte VSD units for block sizes up to 2048, then larger block sizes through 32768. AVDP locations are tried at block 256, block -257, last block, and block 512.

Dependencies: Uses only libparted geometry reads plus stack scratch buffers through `alloca`.

Important details and risks: The probe intentionally returns the whole input geometry rather than deriving a smaller filesystem span. `read_bytes()` handles unaligned byte reads through sector-aligned `ped_geometry_read()`. Tests should include optical-style 2048-byte media, 512-byte block UDF, larger-block UDF, missing VRS, missing anchor, and anchors near small-device boundaries.
