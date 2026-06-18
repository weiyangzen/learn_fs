<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/overlay-initrds.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/overlay-initrds.sh

Purpose: multi-boot test for `ostree admin deploy --overlay-initrd`, including staging, cleanup, comparison, and multiple overlay initrds.

Important APIs/functions: `create_initrd_with_dracut_karg()` builds reproducible cpio initrds containing `/etc/cmdline.d`; `check_for_dracut_karg()` greps `dracut-cmdline` journal output; deploy phases use `--overlay-initrd` and `--stage`.

Control flow/state: phase 1 deploys overlay initrd `ostree.test1`; phase 2 verifies it and stages `ostree.test2`; phase 3 verifies replacement, checks overlay files by sha256 under `/boot/ostree/initramfs-overlays`, tests GC of old overlays and no bootconfig swap for identical overlay, then stages two overlays; phase 4 verifies both kargs and files.

Dependencies/integration: requires dracut journal behavior, cpio, sha256sum, OSTree boot overlays, writable boot, and reboot harness.

Risks/test signals: journal grep is dracut-specific; boot overlay GC depends on BLS references. Signals are kargs in boot journal, overlay image existence, and `bootconfig swap: no`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/overlay-initrds.sh -->
