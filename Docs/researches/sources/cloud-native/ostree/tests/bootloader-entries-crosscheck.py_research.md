<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootloader-entries-crosscheck.py -->
## sources/cloud-native/ostree/tests/bootloader-entries-crosscheck.py

Purpose: validates generated bootloader configuration against BootLoaderSpec loader entries, currently implementing SYSLINUX validation and explicitly skipping GRUB2 here.

Important APIs/functions: `main(argv)` dispatches by bootloader argument; `parse_loader_configs()` reads `/boot/loader/entries/*.conf`; `validate_syslinux()` parses `syslinux.cfg`; `get_ostree_option()` extracts the `ostree=` kernel option; `assert_key_same_file()` compares kernel/initrd stat results through `/boot` and root-relative paths.

Control flow/state: reads sysroot files only, builds sorted in-memory dictionaries by version, compares entry counts and per-entry linux/initrd/ostree options, and exits nonzero via `fatal()`.

Dependencies/integration: used by bootloader tests after `ostree admin` writes boot entries. Requires Python 3 and a synthetic or mounted sysroot with loader and syslinux config.

Risks/test signals: parser is simple and assumes single-space key/value records and integer `version`. Good signals are mismatch-specific fatal messages and success text `SYSLINUX configuration validated`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootloader-entries-crosscheck.py -->
