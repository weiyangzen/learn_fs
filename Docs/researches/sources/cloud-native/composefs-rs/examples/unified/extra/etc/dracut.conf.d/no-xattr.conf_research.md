# sources/cloud-native/composefs-rs/examples/unified/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables dracut xattr preservation for unified example images.

Important APIs/types/functions: `export DRACUT_NO_XATTR=1`.

Control flow: dracut reads during UKI initramfs generation.

State/persistence: persistent build config.

Dependencies/integration: dracut and unified Containerfile.

Risks/test signals: can hide future xattr requirements; boot tests are indirect signal.
