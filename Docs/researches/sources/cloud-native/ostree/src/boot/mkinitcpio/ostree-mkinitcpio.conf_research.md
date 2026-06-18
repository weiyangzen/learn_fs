# sources/cloud-native/ostree/src/boot/mkinitcpio/ostree-mkinitcpio.conf

Purpose: This mkinitcpio configuration defines the hook order needed for OSTree systems.

Important APIs, types, and functions: It sets `HOOKS="base systemd ostree autodetect modconf block filesystems keyboard fsck"`.

Control flow: mkinitcpio reads the hook list in order when building an initramfs. The `ostree` hook is placed after `systemd` and before hardware/filesystem autodetection and mounting hooks.

State and persistence behavior: It controls generated initramfs composition only.

Dependencies and integration points: Integrates with the `src/boot/mkinitcpio/ostree` hook and standard mkinitcpio hooks.

Risks: Hook ordering is boot-critical; moving `ostree` can prevent prepare-root services from being present or correctly ordered. The single-line config is easy for packagers to override incorrectly.

Test signals: Indirect validation through mkinitcpio build output and OSTree boot tests.
