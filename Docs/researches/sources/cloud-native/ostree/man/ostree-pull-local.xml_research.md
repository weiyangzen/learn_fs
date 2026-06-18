# sources/cloud-native/ostree/man/ostree-pull-local.xml

Purpose: documents `ostree pull-local`, which copies data from another repository on the same system.

Important APIs/types: required `SOURCE_REPO`, optional refs; options `--remote`, `--disable-fsync`, `--untrusted`, and `--disable-verify-bindings`.

Control flow: scans source objects/refs, copies or hardlinks eligible objects into the destination, writes refs with optional remote prefix, verifies checksums when untrusted, and can skip fsync/binding checks.

State and persistence: writes destination repository objects and refs.

Dependencies and integration: local migration/mirroring path tied to repo storage modes, refs, fsync policy, and commit binding verification.

Risks and test signals: risks include trusting local hardlinks, disabled fsync durability, and binding verification bypass. Signals are local pull tests across repo modes, untrusted verification tests, and fsck after copy.
