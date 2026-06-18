<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/composefs.rs -->
## sources/cloud-native/ostree/tests/inst/src/composefs.rs

Purpose: destructive multi-boot test for composefs enablement, signed composefs verification, and composefs disablement through kernel args.

Important APIs/functions: `generate_raw_ed25519_keypair()` extracts raw public/private signing material via OpenSSL; `read_booted_metadata()` parses `/run/ostree-booted` as a GLib variant dict; `verify_composefs_sanity()`, `prepare_composefs_signed()`, `verify_composefs_signed()`, and `verify_disable_composefs()` implement the phases; `itest_composefs()` dispatches by reboot mark.

Control flow/state: on first boot, enables `ex-integrity.composefs`, stages a kargs change, and reboots. Later phases sign the pending commit, track config/key files through `rpm-ostree initramfs-etc`, verify journal messages, then append a disable karg and verify non-overlay root.

Dependencies/integration: requires root, rpm-ostree, OpenSSL, OSTree signing, composefs support, non-XFS root for fsverity, systemd journal, and autopkgtest reboot helpers.

Risks/test signals: destructive and stateful; failures can leave staged deployments or modified `/etc/ostree`. Signals include metadata keys, overlay mount type, private-dir mode, signature verification, and journal grep.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/composefs.rs -->
