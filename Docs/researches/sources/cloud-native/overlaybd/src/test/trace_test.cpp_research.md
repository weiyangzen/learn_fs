## sources/cloud-native/overlaybd/src/test/trace_test.cpp

Purpose: integration tests for dynamic prefetch trace generation and replay over ext4/tar and erofs images, verifying prefetched physical extents reconstruct expected file checksums.

Important components: `MockFile` wraps an `IFile` and supports `pread(nullptr, ...)` by reading into an internal buffer, matching zfile/prefetch no-copy read behavior. `download` and `download_erofs_img` fetch external fixtures. `case0` builds an ext4 image from a tarball but immediately returns, so it is disabled. `case1` downloads an erofs image, writes a file list, creates an erofs fs, runs `new_dynamic_prefetcher(...)->replay(dst)`, then checks file contents by reading fiemap physical extents from the image and hashing reconstructed output.

Control flow: active case downloads `alpine.img`, opens it through `MockFile`, writes list entries including `/etc/`, builds an erofs filesystem view, invokes dynamic prefetch, then for each expected file maps extents with `fiemap`, reads physical ranges from the raw image file, writes them to a temp check file, and compares SHA256.

State/persistence: uses `/tmp/trace_test`, downloaded images/tarballs, list/check files, and network access to GitHub URLs. Dependencies include Photon, extfs/erofs, gzip/tar helpers, prefetch implementation included directly, sha256file, and system `curl`/`wget`.

Integration points: directly validates `DynamicPrefetcher::generate_trace`, file-list parsing, erofs detection, fiemap extent handling, and replay worker reads. Risks: network and external fixture dependency, hardcoded checksums, disabled ext4 case, fixed workdir reuse, and worker completion relies on destructor/replay synchronization. Test signal is strong for erofs dynamic prefetch but weak for static trace record/replay.
