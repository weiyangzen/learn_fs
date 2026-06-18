# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/install/composefs

Purpose: UKI mkinitcpio install script for composefs setup support.

Important APIs/types/functions: `build`, `add_binary`, and `add_runscript`.

Control flow: copies helper binary into initramfs and registers hook script.

State/persistence: generated initramfs content.

Dependencies/integration: mkinitcpio API and dracut module helper path.

Risks/test signals: path coupling and missing binary risk; VM boot reveals failures.
