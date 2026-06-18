# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: tells kernel-install to generate ukify UKIs for unified-secureboot.

Important APIs/types/functions: `layout = uki`, `uki_generator = ukify`.

Control flow: kernel-install chooses UKI generation and consults `uki.conf` for signing.

State/persistence: persistent kernel-install policy in image.

Dependencies/integration: ukify, sbsign config, kernel-install.

Risks/test signals: incorrect generator bypasses Secure Boot signing path.
