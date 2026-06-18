# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: dracut configuration for BLS images to force a non-hostonly initramfs and include drivers needed under virtualization.

Important APIs/types/functions: `hostonly=no` and `force_drivers+=" virtio_net vfat "`.

Control flow: dracut reads it during initramfs creation, making the image less tied to the build host and including network/VFAT support.

State/persistence: persists in the image and changes generated initramfs contents.

Dependencies/integration: integrates with dracut, virtio, VFAT ESP handling, and composefs boot examples.

Risks/test signals: over-inclusion increases initramfs size; under-inclusion breaks boot on virtual hardware. Tested via example VM boot.
