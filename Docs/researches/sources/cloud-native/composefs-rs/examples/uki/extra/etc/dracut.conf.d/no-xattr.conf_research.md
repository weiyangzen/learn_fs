# sources/cloud-native/composefs-rs/examples/uki/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables dracut xattr handling for UKI example initramfs generation.

Important APIs/types/functions: `export DRACUT_NO_XATTR=1`.

Control flow: consumed by dracut at build time.

State/persistence: persists in image config and affects generated UKI initramfs.

Dependencies/integration: dracut and UKI Containerfile.

Risks/test signals: same as BLS copy; future xattr-dependent boot content could be omitted.
