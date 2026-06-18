# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/old_format.rs

Purpose: backward-compatibility test for reading and auto-upgrading old-format composefs-rs repositories created by an older `cfsctl`.

Important APIs/types/functions: `cfsctl_old` reads `CFSCTL_PATH_OLD`; `have_skopeo` checks skopeo availability; `test_read_old_format_repo` performs the compatibility scenario.

Control flow: skip if the old binary path or skopeo is absent. Otherwise copy busybox into an OCI layout, use old `cfsctl` to pull into a repo without modern metadata, assert new `cfsctl --no-upgrade` rejects it, then run new `cfsctl` without `--no-upgrade` and verify auto-upgrade writes `meta.json`, lists the image, dumps `/bin/sh`, runs GC, and passes `oci fsck --json`.

State and persistence: creates a temp OCI layout and old-format temp repository; auto-upgrade mutates the repository by adding modern metadata.

Dependencies and integration points: requires an externally built old binary from a documented revision, skopeo, Docker Hub access for busybox, and current `cfsctl`. It validates splitstream compatibility and metadata migration.

Risks: optional by environment, so it may not run in normal CI. It pulls `busybox:latest`, which is less reproducible than digest-pinned fixtures. Auto-upgrade behavior must be coordinated with `--no-upgrade` guarantees.

Test signals: high signal for migration: old repo rejection under `--no-upgrade`, successful default auto-upgrade, dump compatibility, GC preservation, and OCI fsck integrity.
