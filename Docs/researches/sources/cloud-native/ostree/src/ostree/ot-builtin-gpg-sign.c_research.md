# sources/cloud-native/ostree/src/ostree/ot-builtin-gpg-sign.c

## Purpose
Implements legacy `ostree gpg-sign`, adding or deleting GPG signatures stored in commit detached metadata.

## Important APIs, Types, And Functions
`ostree_builtin_gpg_sign()` is the command entry. `usage_error()` prints help for argument failures. `delete_signatures()` reads detached metadata, looks up the private `_OSTREE_METADATA_GPGSIGS_NAME` signature array, verifies signatures to map key IDs to signature indexes, removes matching signatures, and writes updated detached metadata. Signing uses `ostree_repo_sign_commit()`.

## Control Flow
The command requires a commit and at least one GPG key ID, resolves the commit, and either deletes matching signatures or appends new signatures. Delete mode reads detached metadata, extracts signatures, verifies the commit to get an `OstreeGpgVerifyResult`, matches provided key IDs to signature indexes, removes unique matched entries, removes the metadata key if no signatures remain, writes the new detached metadata, and prints the count. Add mode loops over key IDs and signs the resolved commit using the optional GPG homedir.

## State And Persistence
The command persists changes only to detached metadata associated with the commit. Delete mode may remove the GPG signature metadata key entirely. Add mode appends GPG signatures. It does not update commit objects, refs, or summaries.

## Dependencies And Integration Points
It depends on GPGME-enabled libostree APIs, private core metadata names, `OstreeGpgVerifyResult`, detached metadata read/write APIs, and repository revision resolution. It is conditionally declared in `ot-builtins.h` when GPGME is enabled.

## Risks And Edge Cases
Delete mode is low-level and depends on the signature array ordering matching verify-result ordering. It rereads detached metadata indirectly through verification. If verification fails, deletion fails even if raw metadata exists. Missing signature metadata is treated as zero deletions. This command is GPG-specific, whereas newer signapi behavior is implemented in `ot-builtin-sign.c`.

## Test Signals
Tests should cover signing with one and multiple keys, deleting one signature among many, deleting absent key IDs, no-signature metadata, custom GPG homedir, invalid commit, verification failure during deletion, and metadata key removal when all signatures are deleted.
