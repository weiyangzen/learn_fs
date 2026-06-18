# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/digest_stability.rs

Purpose: table-driven digest stability suite for OCI-to-composefs conversion across pinned real container images, EROFS writer versions, and bootable transformations.

Important APIs/types/functions: `ContainerImage` records labels, mirror/upstream refs, expected V2/V1 plain IDs, and optional V2/V1 bootable IDs. Constants cover UBI10, centos-bootc, debian-bootc, and Ubuntu resolute. Helpers include `skip_network`, `pull_image`, `try_pull_image`, `compute_id`, `compute_id_v1`, `try_expand_var`, and `check_digest_equivalence`.

Control flow: `test_oci_container_digest_stability` skips if `COMPOSEFS_SKIP_NETWORK` is set, then for each image initializes a V2 insecure repo, pulls from GHCR mirror with upstream fallback, computes V2 plain/bootable IDs and V1 plain/bootable IDs, and asserts exact expected hashes plus plain-vs-bootable/V1-vs-V2 differences. `check_digest_equivalence` pulls an image into podman, imports from containers-storage, mounts/examines an on-disk container root, compares bootable digests, and emits dumpfile diffs on mismatch.

State and persistence: creates temp repositories, pulls registry images, creates podman containers, mounts containers, writes temporary dumpfiles on mismatch, and may remount `/var` tmpfs larger in VM environments.

Dependencies and integration points: requires network unless skipped, `cfsctl`, podman, registry mirrors/upstreams, privileged VM support for equivalence tests, and digest behavior from OCI import, EROFS V1/V2 writers, boot transforms, and on-disk rootfs reading.

Risks: exact digest pins are intentionally brittle: any legitimate format, metadata, tar-split, boot transform, or fixture image change requires updating expected values. Network/mirror availability can make tests flaky, though upstream fallback helps. The centos bootc equivalence path is intentionally skipped due to known directory mtime divergence tracked upstream.

Test signals: very high-value regression coverage for reproducibility. It catches silent EROFS writer output changes, OCI metadata reconstruction changes, bootable transform differences, and mismatch between containers-storage and on-disk digest paths. Dumpfile diff capture is a strong diagnostic signal.
