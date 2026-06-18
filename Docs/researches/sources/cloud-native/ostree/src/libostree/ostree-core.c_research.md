<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core.c -->
# sources/cloud-native/ostree/src/libostree/ostree-core.c

## Purpose
Implements repository-independent OSTree core data-format helpers: ref/checksum validation, file object stream creation/parsing, checksum calculation, object name/path conversion, metadata schema validation, commit metadata helpers, static delta path helpers, and default sysroot/version utilities.

## Important APIs and Types
Major exported or internal APIs include `ostree_parse_refspec()`, ref/remote/collection/checksum validators, `_ostree_file_header_new()`, `_ostree_zlib_file_header_new()`, `ostree_raw_file_to_content_stream()`, archive-z2 stream conversion functions, `ostree_content_stream_parse()`, content file parse wrappers, `ostree_break_hardlink()`, xattr retrieval, checksum file APIs including async variants, object type/name serialization helpers, checksum hex/base64 conversion helpers, `_ostree_loose_path()`, relative object/static-delta paths, `_ostree_parse_delta_name()`, metadata validators, commit getters, `OstreeCommitSizesEntry`, `_ostree_compare_timestamps()`, optional GPG signature append, `_ostree_get_default_sysroot_path()`, and `ostree_check_version()`.

## Control Flow
The file first validates ABI enum values, builds cached regexes for refs/remotes, canonicalizes xattrs by sorting, serializes file headers as 4-byte big-endian length plus 4-byte padding plus big-endian `GVariant`, chains headers with content streams, and parses streams by reading the header, validating size, decoding metadata, and optionally wrapping compressed content in a zlib decompressor. Checksum functions hash metadata headers and regular-file streams according to object type. Metadata verification hashes the normalized variant bytes, compares the expected checksum, then validates commit/dirtree/dirmeta structure.

## State and Persistence
Persistent formats include loose object paths, static delta paths, commit/dirtree/dirmeta variants, dirmeta xattrs, file object headers, and commit `ostree.sizes` entries. Runtime cached state is limited to regex singletons and a default sysroot `GFile` initialized from `OSTREE_SYSROOT`.

## Dependencies and Integration Points
Depends on libglnx, `ostree-chain-input-stream`, varint helpers, checksum utilities from `otutil`, GIO Unix streams, zlib converters, GLib variants, stat/xattr APIs, and many public `ostree-core.h` type definitions. It is central to repo commit, pull, checkout, fsck, static deltas, and deployment downgrade protection.

## Risks
This file is format-critical: endian conversions, header length/padding, xattr sorting, and checksum semantics must remain stable. `trusted` parsing affects `GVariant` validation assumptions. `_ostree_validate_structureof_xattrs()` increments the loop index inside the loop as well as in the `for`, which can skip entries and deserves scrutiny. Ref/checksum validation rejects uppercase hex and leading punctuation by design, which can affect compatibility.

## Test Signals
Strong signals include golden object checksum tests, file header parse/serialize round trips for regular files and symlinks, compressed archive stream tests, xattr ordering/duplicate validation, dirtree path traversal rejection, static delta path fixtures, async checksum parity, hardlink break behavior, commit size metadata parsing, timestamp downgrade checks, and fsck/pull metadata verification integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core.c -->
