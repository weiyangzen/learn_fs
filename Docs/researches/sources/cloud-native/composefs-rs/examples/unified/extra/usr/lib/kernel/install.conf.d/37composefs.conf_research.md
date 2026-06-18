# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: selects ukify UKI generation for unified images.

Important APIs/types/functions: `layout = uki`, `uki_generator = ukify`.

Control flow: consumed by kernel-install during `add-all`.

State/persistence: kernel-install policy file.

Dependencies/integration: systemd ukify package.

Risks/test signals: wrong layout breaks expected image boot path.
