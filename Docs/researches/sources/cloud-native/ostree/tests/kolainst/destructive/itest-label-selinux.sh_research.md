<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-label-selinux.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/itest-label-selinux.sh

Purpose: broad SELinux labeling test for commit and checkout paths.

Important APIs/functions: exercises `ostree commit --selinux-policy`, `--selinux-labeling-epoch`, checkout `--selinux-policy`, `--subpath`, `--selinux-prefix`, `--skip-list`, `--selinux-policy-from-base`, and `--tree=tar`.

Control flow/state: checks out host commit, creates test binaries with altered labels and reflink behavior, commits and inspects `ostree ls -X`, verifies checkout relabeling for root and subpath layouts, tests prefix correction for nested trees, and verifies labels from base policy for new `/usr/bin`, `/usr/lib`, `/usr/etc` files.

Dependencies/integration: requires SELinux, xattrs, `chcon`, `filefrag`, tar, writable sysroot, and host policy.

Risks/test signals: strongly coupled to SELinux policy names (`bin_t`, `lib_t`, `etc_t`, `system_conf_t`) and reflink support. Signals are label comparisons and expected failure for `-H` with policy checkout.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-label-selinux.sh -->
