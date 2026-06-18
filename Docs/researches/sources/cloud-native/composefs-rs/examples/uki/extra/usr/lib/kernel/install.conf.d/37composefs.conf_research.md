# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: selects UKI generation through `ukify` for the UKI example.

Important APIs/types/functions: `layout = uki` and `uki_generator = ukify`.

Control flow: kernel-install uses ukify rather than BLS entries.

State/persistence: persistent kernel-install policy.

Dependencies/integration: systemd kernel-install and systemd-ukify package.

Risks/test signals: wrong generator/layout would prevent UKI boot artifacts. Validated by example build/boot.
