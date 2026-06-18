# sources/cloud-native/ostree/rust-bindings/src/auto/remote.rs

Purpose: Generated shared wrapper for `OstreeRemote`, representing a configured remote repository.

Important APIs: `name()` returns the remote name, `url()` returns an optional URL, and `Display` prints the name. Ownership uses `ostree_remote_ref`/`ostree_remote_unref`.

Control flow and state: The wrapper is read-only in this file. Remote configuration is persisted elsewhere in repository config or remotes.d files; this type provides a referenced view of that configuration.

Dependencies and integration points: Feature-gated by `v2018_6`. Integrates with repo remote listing/configuration APIs and the repo-config manpage concepts for remote URL/content URL and verification settings.

Risks: `url()` can return `None`, so callers must handle remotes without a direct URL or with custom backends. Displaying only the name is convenient but can hide URL/config distinctions in logs.

Test signals: Remote listing tests should verify name/display behavior, URL presence/absence, and reference ownership across cloned/shared handles.
