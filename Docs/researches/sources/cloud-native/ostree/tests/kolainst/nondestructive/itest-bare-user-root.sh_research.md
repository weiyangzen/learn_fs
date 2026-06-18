<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-user-root.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-user-root.sh

Purpose: tests bare-user repository composition with link-checkout-speedup, ownership preservation, and SELinux relabeling.

Important APIs/functions: initializes a bare-user repo, commits component trees with different owner gid values and no xattrs, union-checkouts components with `-U -H`, commits the combined rootfs with `--selinux-policy / --link-checkout-speedup`, and inspects `ostree ls`/`ls -X`.

Control flow/state: all content is synthetic in a tempdir. It creates dbus/systemd component trees, combines them into `rootfs`, and validates output metadata.

Dependencies/integration: requires host SELinux policy, root, bare-user mode, and assertion helpers.

Risks/test signals: expected gid `81` is Fedora/dbus-specific. Signals are uid/gid/mode in `ostree ls`, SELinux xattr presence, and absence of `user.ostreemeta`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-bare-user-root.sh -->
