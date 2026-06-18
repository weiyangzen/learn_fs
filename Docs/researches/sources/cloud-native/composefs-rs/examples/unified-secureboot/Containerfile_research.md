# sources/cloud-native/composefs-rs/examples/unified-secureboot/Containerfile

Purpose: Fedora multi-stage Containerfile for a unified composefs UKI image with Secure Boot signing support.

Important APIs/types/functions: base/kernel/bootable stages; installs `mokutil`, `sbsigntools`, `systemd-ukify`, composefs, SELinux tools, SSH; computes `COMPOSEFS_FSVERITY` with `cfsctl compute-id --bootable /mnt/base`; writes `/etc/kernel/cmdline`; runs `kernel-install add-all` with BuildKit secrets `key` and `cert`.

Control flow: base root is prepared, kernel stage binds base to compute its digest, writes composefs cmdline, then signs/generated UKIs using configured secrets and `uki.conf`; final bootable stage copies `/boot`.

State/persistence: generated signed UKI artifacts and Secure Boot policy references are persisted in `/boot`; secrets are build-time only.

Dependencies/integration: depends on cfsctl, systemd ukify, sbsign, BuildKit secrets, dracut snippets, and Secure Boot test runner.

Risks/test signals: strongest risk is digest/signing mismatch if base changes after compute-id or secrets are unavailable. Secure Boot runtime coverage comes from `run`.
