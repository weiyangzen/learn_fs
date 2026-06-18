# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_simple.cpp

Purpose: GoogleTest coverage for EROFS tar ingestion, tar metadata replay, PAX path handling, the internal EROFS sector cache helpers, and clean versus incremental layer image construction.

Important APIs/types/functions: `ErofsTest` provides gzip inflation, Photon local/sub filesystem setup, download helpers, LSMT warp-file device creation, and blockwise verification. `ErofsPax` builds a PAX fixture and hashes the mounted EROFS tree traversal. The local `ErofsCache` declaration mirrors the internal liberofs cache contract used by `erofs_read_photon_file` and `erofs_write_photon_file`. `ErofsCacheTest` checks sector cache write/read/flush behavior. `ErofsTestCleanIncremental` provides `traverse_fs` and drives two embedded layer tarballs through clean and incremental `LibErofs::extract_tar` modes.

Control flow: tests inflate embedded gzip byte arrays into temporary tar files, wrap the tar source in an LSMT virtual device, build EROFS images with `LibErofs`, optionally dump tar headers with `UnTar::dump_tar_headers`, rebuild from metadata, mount through `create_erofs_fs`, and compare either device bytes or deterministic SHA256 traversal output. The cache test writes overlapping aligned and unaligned sectors, flushes, then reads through both cache and backing Photon file.

State and persistence: all test state is under `/tmp/tar_test`, `/tmp/pax_test`, `/tmp/erofs_cache_test`, or `/tmp/erofs_clean_incrementtal`, plus temporary `.idx`, `.meta`, image, tar, content, and checksum files. Image persistence flows through LSMT warp files and Photon local files. Cleanup is attempted in fixture teardown, but some conditions appear inverted in the clean/incremental fixture, so stale files may survive failed or skipped cases.

Dependencies/integration: depends on zlib, gtest, Photon FS, Photon extfs, gzindex/gzip adapters, LSMT warp/stack files, `LibErofs`, `create_erofs_fs`, `UnTar`, `new_sha256_file`, and `tar_file.cpp` included directly for the tar adaptor. It is an integration test rather than a pure unit test.

Risks: embedded fixture arrays make failures hard to diagnose without recreating the tar contents. Several tests use large sparse offsets and backing files, so filesystem behavior matters. Direct inclusion of `tar_file.cpp` bypasses normal library boundaries. The clean/incremental teardown uses `access(...) != 0` before unlink/rmdir in several places, which is likely wrong and can hide cleanup bugs. Hash-based traversal tests are sensitive to directory iteration ordering.

Test signals: covers tar metadata equivalence, PAX long path traversal identity, EROFS cache coherency under one-sector capacity, offsets beyond 2^32, and expected final tree/content for clean plus incremental layers including whiteout behavior.
