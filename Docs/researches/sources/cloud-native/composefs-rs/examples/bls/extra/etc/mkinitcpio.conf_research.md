# sources/cloud-native/composefs-rs/examples/bls/extra/etc/mkinitcpio.conf

Purpose: mkinitcpio configuration for the BLS example, selecting modules, binaries, and hooks needed for composefs boot.

Important APIs/types/functions: `MODULES=(overlay erofs)`, `BINARIES=(strace)`, and `HOOKS=(base udev composefs autodetect microcode modconf kms keyboard keymap block filesystems)`.

Control flow: mkinitcpio consumes these arrays when building an initramfs, including the custom composefs hook before normal filesystem handling.

State/persistence: persists kernel image generation policy in the image.

Dependencies/integration: depends on mkinitcpio, overlay, EROFS, strace, and the installed composefs hook/install scripts.

Risks/test signals: hook ordering is sensitive; missing modules prevent root setup. Boot tests are the main signal.
