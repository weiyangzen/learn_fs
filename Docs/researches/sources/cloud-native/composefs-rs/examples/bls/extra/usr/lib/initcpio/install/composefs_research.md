# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/install/composefs

Purpose: mkinitcpio install script for adding composefs setup support.

Important APIs/types/functions: `build`, `add_binary`, and `add_runscript`.

Control flow: copies the dracut module's `composefs-setup-root` helper to `/usr/bin/composefs-setup-root` in the initramfs and registers the hook script.

State/persistence: affects generated initramfs contents.

Dependencies/integration: depends on mkinitcpio install API and the composefs setup helper path.

Risks/test signals: path coupling to dracut module layout is fragile. Boot tests reveal missing helper or hook registration.
