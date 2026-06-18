<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/ocf_perf_test.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/ocf_perf_test.cpp

## Purpose
Implements a manual benchmark and correctness harness comparing OCF cache and full-file cache behavior for single-file and multi-file read workloads.

## Important APIs, Types, And Functions
Defines gflags for cache type, page size, media file, IO engine, concurrency, prefetch, source/destination, total requests, and multi-file generation. Core helpers include `random_read`, `sequential_read`, `work`, `single_file_ocf_cache`, `single_file_file_cache`, `prepare_copied_fs`, `crc_read`, and `multiple_files_test`.

## Control Flow
`main` parses flags, optionally exits on `ut_pass`, initializes Photon, creates a pooled allocator, and runs single- or multi-file mode. Single-file mode opens the selected cache filesystem and launches concurrent read loops with QPS reporting. Multi-file mode creates random data files, copies them to source, builds an OCF cache filesystem, opens all cached and reference files, then repeatedly compares CRC32C per random page.

## State And Persistence
Creates source, copied, namespace, destination, and media files under the selected root. Reuses existing media and copied files when present. Can drop host page cache through `system("echo 3 > /proc/sys/vm/drop_caches")`.

## Dependencies And Integration Points
Uses gflags, Photon threading/filesystems/net curl init paths, OverlayBD full-file and OCF cache factories, CRC32C, and global Photon allocator conventions.

## Risks And Test Signals
This is not a hermetic unit test: it depends on host paths, privileges, `/dev/urandom`, shell commands, large files, and manual stop/limits. It is valuable for throughput and data-integrity signals, especially OCF random/multi-file CRC checks. Source size reviewed: 508 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/ocf_perf_test.cpp -->
