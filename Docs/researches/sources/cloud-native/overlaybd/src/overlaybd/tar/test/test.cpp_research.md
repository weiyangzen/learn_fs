# sources/cloud-native/overlaybd/src/overlaybd/tar/test/test.cpp

Purpose: integration tests for `UnTar`, tar metadata-only extraction, gzip stream indexing, tar wrapper adaptation, and path normalization.

Important APIs/types/functions: `TarTest` provides Photon FS setup, network download helpers, file writing, LSMT device creation, and bytewise device verification. Tests are `untar`, `tar_meta`, `stream`, `gz_tarmeta_e2e`, `tar_header_check`, and `CleanNameTest.clean_name`.

Control flow: tests download or stream public tar/gzip fixtures, use `UnTar::extract_all` for full extraction, use `UnTar::dump_tar_headers` to create tar metadata streams, replay metadata into LSMT-backed extfs images, compare resulting virtual devices, and check deterministic SHA256 of metadata/index outputs. `tar_header_check` writes a generated payload through `new_tar_fs_adaptor`, closes it to finalize tar headers, detects it with `is_tar_file`, and reopens it logically.

State and persistence: uses `/tmp/tar_test`, creates downloaded archives, generated `.idx`, `.meta`, `.tar.meta`, extfs images, and checksum inputs. Fixture teardown unlinks only files listed in `filelist`; downloaded files and rootfs may remain.

Dependencies/integration: depends on gtest, Photon runtime/local/sub/ext filesystems, gzip/gzindex adapters, LSMT, libtar, tar_file implementation included directly, SHA256 file helper, and network access for several tests.

Risks: network downloads make tests flaky and slow outside controlled CI caches. The `download_decomp` output name is fixed as `latest.tar`, so tests share mutable state. Direct inclusion of `tar_file.cpp` risks duplicate definitions if linked differently. SHA256 expectations are brittle if upstream fixture contents change.

Test signals: strong end-to-end signal for tar extraction, turboOCI metadata equivalence, gzip stream index stability, single-file tar wrapper logic, and `clean_name` behavior for redundant separators, dot, dot-dot, root, empty, and trailing slash cases.
