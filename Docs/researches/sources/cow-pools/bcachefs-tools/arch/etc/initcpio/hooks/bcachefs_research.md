# File Research: sources/cow-pools/bcachefs-tools/arch/etc/initcpio/hooks/bcachefs

- Arch mkinitcpio runtime hook for encrypted bcachefs root devices.
- Resolves `$root`, probes with `bcachefs unlock -c`, and prompts either through Plymouth or terminal `bcachefs unlock`.
