# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: makes unified example dracut output non-hostonly.

Important APIs/types/functions: `hostonly=no`.

Control flow: applied during initramfs/UKI build.

State/persistence: affects generated boot artifacts.

Dependencies/integration: dracut and kernel-install.

Risks/test signals: portability/size tradeoff; validated by VM boot.
