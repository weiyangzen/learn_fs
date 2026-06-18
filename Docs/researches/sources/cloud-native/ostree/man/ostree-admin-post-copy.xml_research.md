# sources/cloud-native/ostree/man/ostree-admin-post-copy.xml

Purpose: documents `ostree admin post-copy`, which repairs a sysroot after file-based copying.

Important APIs/types: option `--sysroot="PATH"`; description calls out enabling fs-verity on copied files that lack it.

Control flow: command scans/fixes a copied sysroot to restore properties lost by file copies.

State and persistence: mutates copied sysroot metadata, especially fs-verity state.

Dependencies and integration: used by migration/install workflows that copy OSTree sysroots outside native deployment tooling.

Risks and test signals: docs contain typo "copyed"; semantic risk is under-documenting what repair actions are performed. Signals are copied-sysroot tests and fs-verity verification after repair.
