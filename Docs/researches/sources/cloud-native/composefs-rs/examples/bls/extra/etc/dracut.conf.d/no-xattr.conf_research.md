# sources/cloud-native/composefs-rs/examples/bls/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables xattr preservation in dracut for the BLS example by exporting `DRACUT_NO_XATTR=1`.

Important APIs/types/functions: one dracut environment assignment.

Control flow: read by dracut configuration loading before initramfs generation.

State/persistence: persists as a config file inside the image and affects generated initramfs content.

Dependencies/integration: integrates with dracut and the example image build.

Risks/test signals: minimal logic; risk is loss of required xattrs in future images. Covered only indirectly by boot tests.
