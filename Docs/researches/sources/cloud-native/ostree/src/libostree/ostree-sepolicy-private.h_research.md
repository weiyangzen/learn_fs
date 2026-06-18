# sources/cloud-native/ostree/src/libostree/ostree-sepolicy-private.h

Purpose: private SELinux helper declarations used by commit/checkout code for automatic filesystem create contexts and xattr filtering without exposing those details as stable public API.

Important APIs/types/functions: `OstreeSepolicyFsCreatecon` tracks whether fscreatecon was initialized. `_ostree_sepolicy_fscreatecon_clear` resets a prepared context and is registered as an automatic clear function. `_ostree_sepolicy_preparefscreatecon` computes and sets the SELinux create context for a path/mode when a policy is active. `_ostree_filter_selinux_xattr` removes `security.selinux` from an xattr variant. `_ostree_sepolicy_host_enabled` reports host SELinux status.

Control flow: users can declare `g_auto(OstreeSepolicyFsCreatecon)` and call `_ostree_sepolicy_preparefscreatecon`; cleanup clears the context only if initialization occurred. Xattr filtering is a pure transform returning a rebuilt variant or `NULL`.

State/persistence: `OstreeSepolicyFsCreatecon` is local state. The implementation can mutate process SELinux fscreate context temporarily through libselinux.

Dependencies/integration: depends on `ostree-types.h` and `OstreeSePolicy`. Integrated by commit and checkout writers to avoid persisting source SELinux labels when target policy should compute labels.

Risks: create-context state is process-global in libselinux; failure to clear it can label subsequent files incorrectly. The `initialized` bit guards against leaking or over-clearing state. Xattr variant type expectations must match OSTree xattr serialization.

Test signals: SELinux-sensitive tests in `basic-test.sh`, `test-libarchive-import.c`, and installed payload label tests exercise commit modifier SELinux behavior and xattr handling. Direct unit coverage for this private cleanup helper is not apparent.
