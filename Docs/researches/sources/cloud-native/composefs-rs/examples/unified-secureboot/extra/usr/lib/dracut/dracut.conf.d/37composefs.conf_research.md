# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: non-hostonly dracut config for unified-secureboot composefs images.

Important APIs/types/functions: `hostonly=no`.

Control flow: read during UKI generation to avoid host-specific initramfs.

State/persistence: affects generated signed UKI.

Dependencies/integration: dracut and ukify.

Risks/test signals: size vs portability tradeoff; boot test validates inclusion.
