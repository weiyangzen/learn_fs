# sources/cloud-native/ostree/rust-bindings/src/auto/se_policy.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/se_policy.rs

Generated GObject binding for `OstreeSePolicy`, exposing SELinux policy lookup and relabeling helpers. Constructors include `new`, `new_at`, and `from_commit`; accessors include `csum`, `label`, `name`, `path`, and `rootfs_dfd`; mutating helpers include `restorecon`, `setfscreatecon`, and the version-gated global `set_null_log`.

Control flow follows the generated GError pattern and converts `gio::File`, modes, labels, and variants through GLib. Persistence is external: policy is loaded from a root filesystem or commit, while `restorecon` and `setfscreatecon` influence filesystem labels or process filesystem-creation context through libostree/SELinux APIs.

Integration points are `Repo`, `gio::FileInfo`, `gio::File`, `SePolicyRestoreconFlags`, and commit/write paths that install policies on `RepoCommitModifier`. Risks include rootfs file-descriptor validity, SELinux availability, global process context side effects, and platform/version gating. Test signals are indirect; handwritten `se_policy.rs` adds cleanup but this generated file has no tests.
