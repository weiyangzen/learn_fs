# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: dracut installer for composefs setup in unified-secureboot images.

Important APIs/types/functions: `check`, `depends`, `install`, `inst`, and `$SYSTEMCTL add-wants`.

Control flow: installs setup binary/service and registers service with `initrd-root-fs.target`.

State/persistence: generated initramfs/UKI content.

Dependencies/integration: dracut and systemd initrd.

Risks/test signals: signing can make post-build fixes impossible, so missing content must be caught during build/boot.
