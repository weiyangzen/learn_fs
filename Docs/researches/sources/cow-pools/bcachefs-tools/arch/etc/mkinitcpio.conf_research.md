# File Research: sources/cow-pools/bcachefs-tools/arch/etc/mkinitcpio.conf

- Example mkinitcpio configuration for booting bcachefs.
- Preloads `bcachefs` module and binary.
- Hook sequence includes `bcachefs` after filesystems and before keyboard/fsck.
- Otherwise mirrors standard Arch mkinitcpio commented guidance for modules, binaries, hooks, and compression.
