# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/privileged.rs

Purpose: privileged integration tests for root, fs-verity, kernel mounts, overlay upper layers, bootable OCI mounts, read-only repositories, and filesystem-specific containers-storage zero-copy behavior.

Important APIs/types/functions: environment gates are `require_privileged`, `require_privileged_with_memory`, `require_userns`, and `userns_works`. Filesystem fixtures are `VerityTempDir` for ext4+verity and `LoopTempDir` for ext4/XFS loop mounts. Test helpers include `create_oci_layout_with_large_files`, `copy_oci_to_cstor`, `init_insecure_repo_at`, `cstor_pull`, and `cstor_pull_with_algorithm`.

Control flow: non-root tests re-exec inside a bcvk VM when `COMPOSEFS_TEST_IMAGE` is set; otherwise they fail with setup guidance. Tests initialize secure or insecure repositories on loop-mounted filesystems, run `cfsctl` mount/init/pull commands, inspect mounted content, unmount resources, and assert import stats. The cstor filesystem tests iterate SHA-256/SHA-512 and local-fetch auto/zerocopy across ext4 hardlink and XFS reflink expectations.

State and persistence: creates sparse filesystem images, formats/mounts loop devices, initializes repositories, creates OCI test images, creates overlay stores, performs kernel mounts and bind mounts, writes through overlay upperdirs, and unmounts in `Drop` or explicit cleanup.

Dependencies and integration points: requires root or VM, ext4 verity, optional XFS reflink tools, podman, skopeo, unshare, mount/umount, `composefs_oci::test_util`, and `cfsctl`. It validates integration between repository verity policy, OCI boot transforms, mount plumbing, overlayfs, containers-storage local fetch, hardlinks, and reflinks.

Risks: tests are resource- and privilege-heavy. Cleanup relies on successful unmounts; failures can leave mounts behind until process exit or manual cleanup. XFS coverage skips when `mkfs.xfs` is missing. Read-only bind-mount tests must unmount before assertions to avoid leaked read-only state. The VM path depends on `BCVK_PATH`, `COMPOSEFS_TEST_IMAGE`, and memory sizing. Assertions on import stats assume filesystem/link behavior remains stable.

Test signals: strongest coverage for production-like behavior: secure repo without `--insecure`, verity-required metadata, insecure metadata rejection under `--require-verity`, bootable OCI mount content differences, upperdir read-only/read-write semantics, read-only repo error clarity, ext4 hardlink fallback, XFS reflink use, and both hash algorithms under local-fetch modes.
