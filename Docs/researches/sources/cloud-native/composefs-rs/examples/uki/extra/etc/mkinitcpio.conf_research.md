# sources/cloud-native/composefs-rs/examples/uki/extra/etc/mkinitcpio.conf

Purpose: mkinitcpio composefs boot configuration for UKI example variants.

Important APIs/types/functions: `MODULES=(overlay erofs)`, `BINARIES=(strace)`, and hook order with `composefs` before filesystem discovery.

Control flow: used by mkinitcpio when building initramfs content.

State/persistence: persistent initramfs generation config.

Dependencies/integration: mkinitcpio hooks/install scripts and composefs setup binary.

Risks/test signals: hook order and module inclusion are boot-critical.
