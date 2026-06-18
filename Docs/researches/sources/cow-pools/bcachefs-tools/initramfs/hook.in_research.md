# File Research: sources/cow-pools/bcachefs-tools/initramfs/hook.in

Initramfs-tools hook script. It declares no prerequisites, sources hook-functions, adds the `bcachefs` kernel module, includes loaded `chacha20` and `poly1305` modules for encrypted filesystems, and copies `bcachefs` plus `mount.bcachefs` into `/sbin` inside the initramfs.
