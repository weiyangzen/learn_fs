# sources/cloud-native/ostree/rust-bindings/src/auto/flags.rs

Purpose: Generated bitflag mappings for libostree flag types.

Important APIs: Flags include `ChecksumFlags`, `DiffFlags`, `GpgSignatureFormatFlags`, `RepoCommitModifierFlags`, `RepoCommitState`, `RepoCommitTraverseFlags`, `RepoListObjectsFlags`, `RepoListRefsExtFlags`, `RepoPruneFlags`, `RepoPullFlags`, `RepoResolveRevExtFlags`, `RepoVerifyFlags`, `SePolicyRestoreconFlags`, `SysrootSimpleWriteDeploymentFlags`, `SysrootUpgraderFlags`, and `SysrootUpgraderPullFlags`. `SysrootUpgraderFlags` additionally implements GLib value/param-spec traits.

Control flow and state: Each bitflags type converts to/from its raw C bitmask. `from_bits_truncate` drops unknown bits on inbound conversion, unlike enums that preserve unknown values.

Dependencies and integration points: Used throughout repo traversal, pruning, pulling, checkout, commit modification, verification, SELinux relabeling, sysroot deployment writes, and upgrader behavior. Depends on `glib::bitflags`, GLib value traits, and FFI constants.

Risks: Unknown future bits are truncated, so newer libostree flags can be silently lost when round-tripped through older bindings. Security-sensitive flags such as `UNTRUSTED`, `TRUSTED_HTTP`, `NO_GPG`, and `NO_SIGNAPI` require careful downstream use. Feature gates must match installed library support.

Test signals: Bitmask round-trip tests for known combinations, GLib `Value` tests for `SysrootUpgraderFlags`, and compile tests for feature-gated flags.
