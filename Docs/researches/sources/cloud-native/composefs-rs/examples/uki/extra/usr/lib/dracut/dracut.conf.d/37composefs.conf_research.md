# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: makes UKI dracut output non-hostonly for portable example boot.

Important APIs/types/functions: `hostonly=no`.

Control flow: dracut includes generic drivers/modules rather than tailoring to build host.

State/persistence: affects generated UKI/initramfs.

Dependencies/integration: dracut and kernel-install/ukify.

Risks/test signals: broad inclusion increases size; insufficient inclusion breaks VM boot.
