# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/kernel/uki.conf

Purpose: ukify Secure Boot signing configuration for the unified-secureboot example.

Important APIs/types/functions: `[UKI]`, `SecureBootSigningTool=sbsign`, `SecureBootPrivateKey=/run/secrets/key`, and `SecureBootCertificate=/run/secrets/cert`.

Control flow: kernel-install/ukify reads this during UKI generation and signs using BuildKit-mounted secrets.

State/persistence: config persists in image; private key/cert paths are ephemeral build secrets.

Dependencies/integration: depends on systemd-ukify, sbsign, and `Containerfile` secret mounts.

Risks/test signals: missing or mismatched secrets fail UKI signing. Runtime validation is through Secure Boot QEMU run.
