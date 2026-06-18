<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/grub2-entries-crosscheck.py -->
## sources/cloud-native/ostree/tests/grub2-entries-crosscheck.py

Purpose: validates that generated GRUB2 menu entries match BootLoaderSpec loader entries for linux path, initrd path, and `ostree=` option.

Important APIs/functions: parses loader configs from `/boot/loader/entries` or argv paths, sorts by descending integer `version`, scans only the `15_ostree` block in `grub.cfg`, and compares with `assert_matches_key()`.

Control flow/state: read-only parser; constructs two entry lists and fails if counts or key values differ. Uses `get_ostree_option()` to compare only the OSTree deployment root option inside full kernel args.

Dependencies/integration: used after bootloader generation tests, including the shell `ostree-grub-generator`. Requires Python 3 and predictable GRUB2 stanza formatting.

Risks/test signals: parser assumes generated GRUB syntax starts `linux`/`initrd` at line start and ignores quoted menuentry details. Success text is `GRUB2 configuration validated`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/grub2-entries-crosscheck.py -->
