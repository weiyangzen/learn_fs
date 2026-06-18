# sources/cloud-native/ostree/src/boot/dracut/module-setup.sh

Purpose: This dracut module installs OSTree's initramfs prepare-root integration so an OSTree deployment can become the real root during early boot.

Important APIs, types, and functions: Dracut hook functions include `installkernel`, `check`, `depends`, and `install`. `installkernel` requests `erofs` and `overlay` kernel modules. `check` returns `255` only when systemd and `/usr/lib/ostree/ostree-prepare-root` are executable, which tells dracut the module is usable. `install` copies `ostree-prepare-root`, optional `prepare-root.conf` from `/usr/lib/ostree` or `/etc/ostree`, optional `initramfs-root-binding.key`, and `ostree-prepare-root.service`, then links the service into `initrd-root-fs.target.wants`.

Control flow: Dracut calls these shell functions during initramfs generation. The script conditionally includes configs and always wires the systemd unit when installation proceeds.

State and persistence behavior: It writes files and symlinks into the generated initramfs image, not the live root at boot time. Including root-binding keys and prepare-root config affects how early boot later resolves and validates the OSTree root.

Dependencies and integration points: Depends on dracut helper functions (`instmods`, `dracut_install`, `inst_simple`, `ln_r`), systemd unit directories, the OSTree prepare-root binary, and optional config/key files. It pairs with `ostree-prepare-root.service`.

Risks: Missing modules or service links can make OSTree systems fail before root switch. Including host-specific keys/configs in initramfs needs packaging care. `check` excludes non-systemd initramfs environments.

Test signals: There are no direct tests in this subset. Practical validation comes from dracut image generation and boot tests where `ostree-prepare-root.service` runs in initramfs.
