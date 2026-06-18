# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/hooks/composefs

Purpose: UKI mkinitcpio late hook for composefs root setup.

Important APIs/types/functions: `run_latehook`, `getarg composefs`, `/usr/bin/composefs-setup-root --sysroot /new_root`.

Control flow: no-ops without composefs cmdline; otherwise sets up root late in initcpio.

State/persistence: runtime mount mutation only.

Dependencies/integration: mkinitcpio runtime and setup binary.

Risks/test signals: boot-critical path for mkinitcpio-based UKI examples.
