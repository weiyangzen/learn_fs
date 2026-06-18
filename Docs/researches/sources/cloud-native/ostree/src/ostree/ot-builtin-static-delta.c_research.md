# sources/cloud-native/ostree/src/ostree/ot-builtin-static-delta.c

## Purpose
Implements the `ostree static-delta` dispatcher and subcommands for listing, showing, deleting, generating, applying offline, verifying, indexing, and reindexing static deltas.

## Important APIs, Types, And Functions
`ostree_builtin_static_delta()` dispatches subcommands from `static_delta_subcommands[]`. Subcommand handlers include `ot_static_delta_builtin_list()`, `indexes()`, `reindex()`, `show()`, `delete()`, `generate()`, `apply_offline()`, and `verify()`. The file uses private command hooks for static delta dump/delete/query, public repo APIs for list/generate/reindex/apply/verify, and `OstreeSign` for signapi signatures.

## Control Flow
The dispatcher finds the first non-option command or help flag, prints top-level usage for help/missing/unknown commands, adjusts the program name, and invokes the handler with the original argc/argv. List and indexes parse options, list delta names or indexes, and print empty markers when none exist. Reindex calls `ostree_repo_static_delta_reindex()` with optional `--to`. Show and delete require a delta ID at `argv[2]` and call private dump/delete functions. Generate requires a `to` revision by option or positional argument, derives the from source from `--empty`, `--from`, or `to^`, resolves revisions, optionally skips existing deltas, computes metadata endianness, builds generation parameters for sizes, bsdiff, inline parts, output filename, signing keys from arguments and file, and sign type, then calls `ostree_repo_static_delta_generate()`. Apply-offline opens a writable repo, optionally builds a signature verifier from keys, prepares a transaction, executes the offline delta with signature verification, and commits. Verify builds a verifier and calls `ostree_repo_static_delta_verify_signature()`.

## State And Persistence
List, indexes, show, and verify are read-only. Delete removes delta files. Generate writes static delta metadata/parts to the repo or a target directory. Reindex updates static delta indexes. Apply-offline writes objects and metadata into the repo transactionally. Signature options persist on generated delta metadata.

## Dependencies And Integration Points
This file integrates static delta generation/application, private delta maintenance commands, repository transactions, object fetching workflows, signapi key loading, and CLI help conventions. Generated deltas are consumed by pull, create-usb, and mirror workflows.

## Risks And Edge Cases
Subhandlers expect the subcommand to remain at `argv[1]`, so required operands start at `argv[2]`. Numeric size options use `g_ascii_strtoull()` without explicit validation of trailing text. `--empty` conflicts with `--from`. Apply-offline clears the sign engine if no default public keys are available and no explicit key source was provided, allowing unsigned/offline behavior depending on API semantics. Generate key-file parsing treats each line as a key string and may add allocated strings to a non-freeing `GPtrArray`.

## Test Signals
Tests should cover top-level help and unknown commands, list/index empty and populated output, show/delete by delta ID, generate from parent/from/empty, if-not-exists skip, endian options, bsdiff/inline/size parameters, output directory generation, signing from args and file, offline apply with and without signature keys, verify success/failure, and reindex filtering by target revision.
