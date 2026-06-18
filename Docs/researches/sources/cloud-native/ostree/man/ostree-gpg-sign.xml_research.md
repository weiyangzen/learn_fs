# sources/cloud-native/ostree/man/ostree-gpg-sign.xml

Purpose: documents `ostree gpg-sign`, which adds GPG signatures to commits.

Important APIs/types: command accepts commit and GPG key IDs; options include GPG homedir and related signature controls.

Control flow: resolves commits, loads GPG keys through GPGME, creates detached or embedded signature metadata, and writes it to the repository.

State and persistence: mutates repository signature metadata associated with commits.

Dependencies and integration: depends on `--with-gpgme` configure support, GPG keyrings, commit objects, and verification paths used by pull/status/show.

Risks and test signals: risks include missing GPGME builds, keyring selection, and signing wrong commit. Signals are GPG signing/verification tests and behavior when GPGME is disabled.
