<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot-upgrader.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sysroot-upgrader.h

## Purpose
`ostree-sysroot-upgrader.h` declares the public `OstreeSysrootUpgrader` type and its simple upgrade API for libostree consumers. It exposes constructors, origin accessors/mutators, timestamp checking, pull operations, and deployment for systems that track upgrades through a deployment origin refspec.

## Important APIs, Types, And Functions
The header defines `OSTREE_TYPE_SYSROOT_UPGRADER`, `OSTREE_SYSROOT_UPGRADER`, and `OSTREE_IS_SYSROOT_UPGRADER` macros. `OstreeSysrootUpgraderFlags` includes `NONE`, `IGNORE_UNCONFIGURED`, `STAGE`, and `KEXEC`. Public constructors are `ostree_sysroot_upgrader_new`, `ostree_sysroot_upgrader_new_for_os`, and `ostree_sysroot_upgrader_new_for_os_with_flags`. Origin APIs are `ostree_sysroot_upgrader_get_origin`, `ostree_sysroot_upgrader_dup_origin`, `ostree_sysroot_upgrader_set_origin`, and `ostree_sysroot_upgrader_get_origin_description`. Upgrade helpers include `ostree_sysroot_upgrader_check_timestamps`, `ostree_sysroot_upgrader_pull`, `ostree_sysroot_upgrader_pull_one_dir`, and `ostree_sysroot_upgrader_deploy`. `OstreeSysrootUpgraderPullFlags` exposes `NONE`, `ALLOW_OLDER`, and `SYNTHETIC`.

## Control Flow
The declared intended flow is construct an upgrader for the booted or named OS, inspect or replace its origin if desired, call `pull` or `pull_one_dir` to fetch/resolve the next revision and learn whether it changed, then call `deploy` to stage or immediately write the new deployment. `check_timestamps` is exposed separately for callers needing explicit rollback checks between two revisions.

## State And Persistence
The header itself stores no state, but it defines APIs whose implementation persists repository objects and refs during pull and deployment/origin files during deploy. `get_origin` returns borrowed mutable `GKeyFile` state owned by the upgrader, while `dup_origin` returns a full copy. Flags shape persistence: `STAGE` writes transient staged deployment state for later finalization, and `KEXEC` loads the target kernel after a non-staged deploy.

## Dependencies And Integration Points
The API includes `ostree-sysroot.h`, uses `OstreeSysroot`, `OstreeRepo`, `OstreeRepoPullFlags`, `OstreeAsyncProgress`, `GCancellable`, `GError`, and `GKeyFile`, and is marked with `_OSTREE_PUBLIC` for exported libostree ABI. It is implemented by `ostree-sysroot-upgrader.c` and ultimately integrates with sysroot deployment code in `ostree-sysroot-deploy.c`.

## Risks
Flag values are public ABI and should not be reordered or repurposed. `OSTREE_SYSROOT_UPGRADER_FLAGS_NONE` is defined as `(1 << 0)` rather than zero, which is unusual for flags APIs and must be preserved for compatibility. `ALLOW_OLDER` weakens rollback protection. `SYNTHETIC` skips remote pulling and assumes the commit/ref state already exists locally. `STAGE` changes when failures surface because finalization happens at shutdown, while `KEXEC` requires kernel support and privilege.

## Test Signals
Header-level signals are ABI/API compilation tests, introspection or symbol export checks for the `_OSTREE_PUBLIC` functions, GType and flags registration checks, and integration tests that compile callers using each constructor, flag, pull variant, origin accessor, and deploy path. Runtime behavior is validated through the implementation tests described for `ostree-sysroot-upgrader.c`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot-upgrader.h -->
