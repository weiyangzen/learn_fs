<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/deployment-lint -->
## sources/cloud-native/ostree/tests/kolainst/destructive/deployment-lint

Purpose: validates deployment linting around commits containing `/var` content.

Important APIs/functions: uses `ostree commit --selinux-policy-from-base --tree=ref --tree=dir`, `ostree admin deploy`, `ostree admin stateroot-init`, and assertion helpers.

Control flow/state: creates a commit `testlint` adding `rootfs/var/testcontent`, deploys it into the current stateroot and verifies `/var/testcontent` is not materialized there, then initializes `newstatedir` and verifies the same content exists under the new stateroot deployment var.

Dependencies/integration: requires writable sysroot, host commit info, and installed OSTree.

Risks/test signals: expected warning text is asserted absent, so behavior changes in lint reporting may matter. Signals are filesystem existence checks in current `/var` versus new stateroot var.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/deployment-lint -->
