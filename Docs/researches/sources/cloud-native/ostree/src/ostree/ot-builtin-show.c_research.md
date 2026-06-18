# sources/cloud-native/ostree/src/ostree/ot-builtin-show.c

## Purpose
Implements `ostree show`, a multipurpose inspection command for commit/object variants, metadata keys, related commits, commit size metadata, arbitrary GVariant files, and commit GPG signatures.

## Important APIs, Types, And Functions
`ostree_builtin_show()` dispatches option-specific behavior. Helpers include `do_print_variant_generic()`, `do_print_related()`, `get_metadata()`, `do_list_metadata_keys()`, `do_print_metadata_key()`, `do_print_sizes()`, `print_object()`, and `print_if_found()`. It uses `ot_dump_object()`, `ot_dump_variant()`, commit metadata APIs, object-size metadata APIs, GPG verification APIs, and `ostree_repo_load_file()` for file objects.

## Control Flow
The command requires one object argument. Metadata key modes resolve the revision and print or list normal/detached metadata. Related mode loads the commit and prints related commit names/checksums. Variant type mode reads an arbitrary file descriptor as the requested GVariant type. Size mode resolves the commit and totals archived/unpacked sizes from commit object-size metadata, separating missing local objects as needed. Default mode treats non-checksum inputs as revisions and prints the commit; checksum inputs are searched as commit, dir-meta, and dir-tree objects, and if none are found, loaded as a file object and formatted with type, size/target, mode, uid/gid, and xattrs. Commit printing may also verify and describe GPG signatures unless no signature exists.

## State And Persistence
The command is read-only. It maps/loads variants, file metadata, xattrs, and GPG verification results, and writes formatted data to stdout/stderr.

## Dependencies And Integration Points
This file is the main consumer of `ot-dump.c` helpers. It integrates repository object loading, revision resolution, detached metadata, object-size metadata, GPG homedir and remote verification settings, and file object inspection. It complements `log`, `summary`, `ls`, and `fsck`.

## Risks And Edge Cases
Option modes are mutually exclusive by if/else order rather than explicit validation, so if multiple options are passed only the first matching branch runs. `--print-hex` only changes byte-array metadata output. `--no-byteswap` affects variant formatting. GPG no-signature is ignored, while other verification errors are fatal. File-object fallback only happens for checksum-looking inputs.

## Test Signals
Tests should cover commit display by ref and checksum, object type search order, file object fallback for regular files and symlinks, metadata list/print for normal and detached metadata, byte-array hex output, related commits, variant file printing, sizes metadata, raw/no-byteswap behavior, and GPG verification output/errors.
