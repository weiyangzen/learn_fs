# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: dracut module installer for composefs setup in the BLS example.

Important APIs/types/functions: dracut callbacks `check`, `depends`, and `install`; installs `strace`, `composefs-setup-root`, the systemd service, and adds a wants link from `initrd-root-fs.target`.

Control flow: dracut calls `check` and `depends`, then `install` copies files into the initramfs and registers the service.

State/persistence: persists binaries and unit wants inside the generated initramfs.

Dependencies/integration: depends on dracut helper functions `inst`, `$SYSTEMCTL`, `${moddir}`, `${initdir}`, and `${systemdsystemunitdir}`.

Risks/test signals: path mismatches or missing helpers break initramfs generation. BLS copy includes `strace`, unlike UKI/unified variants, which may affect debugging and size.
