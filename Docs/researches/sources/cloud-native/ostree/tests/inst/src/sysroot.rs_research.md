<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/sysroot.rs -->
## sources/cloud-native/ostree/tests/inst/src/sysroot.rs

Purpose: non-destructive checks against the booted sysroot when running on an OSTree host.

Important APIs/functions: `skip_non_ostree_host()` gates tests; `itest_sysroot_ro()` loads the default `ostree::Sysroot`, verifies booted deployment, and reads its commit; `itest_immutable_bit()` checks `lsattr -d /` unless composefs overlay is active; `itest_tmpfiles()` checks `/run/ostree` mode; `itest_osinit_unshare()` runs `ostree admin os-init` and rechecks permissions.

Control flow/state: read-only for most checks, except `os-init` creates a test stateroot. Non-OSTree hosts return success without assertions.

Dependencies/integration: uses `ostree-ext` bindings, `xshell`, system utilities, and helper output assertions.

Risks/test signals: skip-by-return can hide coverage on non-OSTree hosts. Signals are API load success, commit read success, permission values, and command output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/sysroot.rs -->
