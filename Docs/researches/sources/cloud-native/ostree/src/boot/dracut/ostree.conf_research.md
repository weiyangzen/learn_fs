# sources/cloud-native/ostree/src/boot/dracut/ostree.conf

Purpose: This dracut configuration requests the OSTree and systemd modules and enables reproducible image generation.

Important APIs, types, and functions: It appends `ostree systemd` to `add_dracutmodules` and sets `reproducible=yes`.

Control flow: Dracut sources this config while building an initramfs. There is no custom shell function.

State and persistence behavior: It influences generated initramfs contents and reproducibility. It does not run during boot.

Dependencies and integration points: Integrates with dracut's config parser and the `module-setup.sh` OSTree module.

Risks: If this config is not installed or sourced, required OSTree/systemd initramfs pieces may be absent. Reproducibility depends on dracut support and broader image inputs.

Test signals: Indirect signal is successful dracut image construction containing the OSTree module and systemd boot path.
