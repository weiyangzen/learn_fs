# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: dracut module installer for unified composefs setup.

Important APIs/types/functions: `check`, `depends`, `install`, `inst`, and `$SYSTEMCTL add-wants`.

Control flow: installs setup binary/service and links service into initrd target.

State/persistence: generated UKI/initramfs content.

Dependencies/integration: dracut and systemd initrd.

Risks/test signals: path and unit registration errors break boot.
