# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: UKI dracut module installer for composefs setup.

Important APIs/types/functions: `check`, `depends`, `install`; copies composefs setup binary and service, and adds service to `initrd-root-fs.target`.

Control flow: dracut invokes installer during initramfs creation.

State/persistence: generated initramfs includes binary, unit, and wants link.

Dependencies/integration: dracut module variables and `$SYSTEMCTL`.

Risks/test signals: unlike BLS version, it does not install `strace`, so debug expectations differ. Boot tests catch missing files.
