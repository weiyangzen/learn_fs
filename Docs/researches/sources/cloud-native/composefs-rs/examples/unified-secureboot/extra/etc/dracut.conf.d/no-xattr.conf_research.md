# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables dracut xattr preservation for unified-secureboot example.

Important APIs/types/functions: `export DRACUT_NO_XATTR=1`.

Control flow: read by dracut during initramfs/UKI generation.

State/persistence: persistent config affecting generated UKI.

Dependencies/integration: dracut and secureboot Containerfile.

Risks/test signals: xattr suppression may hide future metadata requirements.
