<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/privileged.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/tests/privileged.rs

Purpose: defines root/booted-system integration checks for OSTree under bootc-style VM/container execution.

Important APIs/functions: `booted_test!` and `privileged_test!` create fallible functions and register them. Tests verify `/run/ostree-booted`, `/sysroot`, `/ostree/repo`, composefs overlay and `/run/ostree/.private`, `ostree --version`, `/sysroot` read-only options, `/run/ostree` permissions, immutable-bit behavior, `ostree admin os-init`, FIFO commit rejection, repo mtime updates, `repo/extensions`, and SELinux label of `/etc`.

Control flow/state: tests use `xshell` commands, temporary directories for repo-only tests, and direct host filesystem assertions for booted tests. Some checks are conditional, e.g. immutable-bit skipped on composefs and SELinux skipped if labels are absent.

Dependencies/integration: requires root, `ostree`, `systemd/findmnt/lsattr/ls -Z`, composefs when relevant, and booted OSTree layout. External VM deployment is assumed.

Risks/test signals: assertions depend on exact mount types and labels. Strong signals are `ensure!` failures with descriptive messages and command failures propagated through `anyhow`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/privileged.rs -->
