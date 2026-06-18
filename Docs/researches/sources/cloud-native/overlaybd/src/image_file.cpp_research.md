<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.cpp -->
# sources/cloud-native/overlaybd/src/image_file.cpp

Purpose: Builds the per-device image file by opening remote/local lower layers, optional writable upper layer, gzip target data, prefetch traces, and background download.

APIs and control flow: Local lower paths prefer explicit `file`, then downloaded `overlaybd.commit`, then `overlaybd.sealed`; otherwise remote URLs are opened through `global_fs.remote_fs`. Remote layers set local dir and size via ioctl for download cache, wrap blob streams as tar, then as switch files. `open_lower_layer` optionally adds prefetch, target file/digest, gzip index, gzip cache, and LSMT warp. `open_lowers` opens layers in parallel Photon threads and stacks them with `LSMT::open_files_ro`. `open_upper` opens LSMT RW files or turboOCI target data. `init_image_file` handles acceleration layers, trace record/replay, read-only or RW stacking, and starts background download. `create_snapshot` opens a new upper, restacks the live RW file, moves the old upper into lowers, updates combo indices, and renames the new config over the active config.

State and persistence: Uses layer dirs, commit/sealed files, upper index/data/target files, trace files, and active config rename. `m_status` controls lifecycle and download cancellation.

Dependencies and integration: Heavy use of Photon FS, registry/cache fs, LSMT, gzip/gzindex, tar adaptor, prefetcher, switch file, and `ImageService`.

Risks and test signals: ParallelOpenTask increments without locking, so real concurrency depends on Photon scheduling safety. Snapshot index manipulation is delicate. Tests should cover RO mount, RW writes, gzip target layers, failed auth, background download, prefetch, and snapshot restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/image_file.cpp -->
