# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cstor.rs

Purpose: containers-storage import tests. They verify that `composefs_oci` and `cfsctl oci pull --local-fetch` correctly import podman/containers-storage images, preserve content equivalence, and use caching/zero-copy paths.

Important APIs/types/functions: `copy_image_to_separate_store` copies a podman image to a standalone overlay store using skopeo and optional `podman unshare`. Tests include cstor-vs-skopeo equivalence, idempotent import, import with reference, additional image store, and bootable containers-storage pull.

Control flow: tests use `require_privileged` or `require_userns` to run locally when possible or dispatch to a VM. They build a synthetic image via `build_test_image`, create temp repositories, pull through `composefs_oci::pull` or external `cfsctl`, and compare config digests, layer refs, import stats, OCI refs, inspect fields, and CLI output.

State and persistence: creates podman images, separate overlay stores, temp repositories, OCI directory copies, and `STORAGE_OPTS`-scoped pulls. Cleanup is explicit for some images via `cleanup_test_image`, while tempdirs handle repositories/stores.

Dependencies and integration points: requires podman, skopeo, containers-storage, user namespaces, and sometimes the VM path from `privileged.rs`. It exercises `LocalFetchOpt::IfPossible`, OCI tagging/ref layout under `streams/refs/oci`, additional image store handling, and boot image generation.

Risks: environment-dependent and slower than host tests. Skopeo/containers-storage behavior may differ by version. A documented TODO notes cstor vs skopeo config verity can differ due to layer ref ordering even when content is equivalent. Additional image store testing mutates the default store by removing the original image, so cleanup/order matters.

Test signals: validates critical import invariants: matching config digests/layer refs across cstor and skopeo paths, second import copying zero objects, reference names appearing in OCI refs, `STORAGE_OPTS=additionalimagestore=...` support, and bootable pull producing `composefs_boot_erofs`.
