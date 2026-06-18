# sources/cloud-native/ostree/src/ostree/ot-dump.c

## Purpose
Provides shared formatting helpers for OSTree CLI commands that dump variants, commit objects, summary files, summary metadata keys, and GPG key variants.

## Important APIs, Types, And Functions
Public functions are `ot_dump_variant()`, `ot_dump_object()`, `ot_dump_summary_bytes()`, `ot_dump_summary_metadata_keys()`, `ot_dump_summary_metadata_key()`, and `ot_dump_gpg_key()`. Internal helpers include `format_timestamp()`, `uint64_secs_to_iso8601()`, `dump_indented_lines()`, `dump_commit()`, `dump_summary_ref()`, `dump_summary_refs()`, `strptr_cmp()`, and `dump_gpg_subkey()`.

## Control Flow
`ot_dump_variant()` byte-swaps variants on little-endian systems before printing, matching OSTree's big-endian serialized metadata convention. `ot_dump_object()` prints object type/checksum, optionally prints unswapped or raw variants, and pretty-prints commit objects. Commit dumping extracts subject, body, timestamp, parent, content checksum, and optional version. Summary dumping parses `OSTREE_SUMMARY_GVARIANT_FORMAT`, optionally raw-dumps, prints refs under the main collection ID and collection map, then prints recognized metadata keys with friendly labels and timestamps. Metadata key listing sorts keys before printing. Metadata key printing looks up a key and dumps its value. GPG key dumping validates the variant type, prints primary key/subkeys with timestamps and status flags, and prints UIDs plus update URLs.

## State And Persistence
All functions are read-only formatters. They allocate transient variants/strings and write to stdout. `dump_commit()` calls `errx(1)` on invalid timestamps, which exits the process rather than returning an error.

## Dependencies And Integration Points
The file depends on OSTree core variant formats, repo private summary constants, static delta summary keys, admin checksum version extraction, GLib date/time/variant APIs, and CLI commands such as `show`, `log`, `summary`, and remote GPG key listing.

## Risks And Edge Cases
Endianness handling is central: default output byte-swaps for readability, while callers can request unswapped/raw output through flags. Invalid summary checksum bytes are printed as error text rather than failing the whole dump. Recognized summary keys are pretty-printed; unknown keys use generic `g_variant_print()`. Process exit from `dump_commit()` is harsher than GLib error propagation and should be considered before reusing it in library-like contexts.

## Test Signals
Tests should cover variant byte-swapping, commit pretty output, raw and unswapped object output, summary refs with and without collection maps, pretty labels for last-modified/expires/mode/tombstones/static-deltas, sorted metadata key listing, missing metadata key errors, valid and invalid checksum bytes, and GPG key formatting for revoked/expired/invalid keys and UIDs.
