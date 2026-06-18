# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-parser.c

## Purpose
This file parses Avahi/DNS-SD TXT records for OSTree repository discovery. It converts an `AvahiStringList` into a normalized `GHashTable` mapping lowercase TXT keys to optional `GBytes` values.

## Important APIs, Types, And Functions
The internal parser helper `parse_txt_record()` validates and splits one TXT item according to RFC 6763 section 6 constraints. The exported internal function `_ostree_txt_records_parse()` walks an `AvahiStringList`, parses each record, lowercases keys with `g_ascii_strdown()`, stores values as `GBytes`, and skips invalid or duplicate records with debug logging.

## Control Flow
For each TXT record, `_ostree_txt_records_parse()` gets text bytes and length from Avahi, calls `parse_txt_record()`, ignores invalid records, lowercases the key, ignores duplicate keys, and inserts the key/value pair into a hash table. `parse_txt_record()` rejects records over 8900 bytes, accepts printable ASCII key characters except `=`, treats the first `=` after a non-empty key as the key/value separator, distinguishes absent values from empty values, and requires a non-empty key.

## State And Persistence
The returned hash table owns allocated lowercase key strings and `GBytes` value objects. Values are created with `g_bytes_new_static()` and are only valid because the parser contract says the returned table is valid as long as the original Avahi TXT storage remains valid. There is no persistent repository state.

## Dependencies And Integration Points
The file depends on Avahi string-list APIs, GLib/GObject, libglnx, and the private Avahi finder header. It integrates with `ostree-repo-finder-avahi` discovery code, which can consume normalized TXT keys such as repo metadata advertised over DNS-SD.

## Risks And Edge Cases
The lifetime of `GBytes` values is tied to Avahi-provided memory because `g_bytes_new_static()` does not copy. Consumers must not outlive the `AvahiStringList`. Duplicate keys are ignored after the first parsed occurrence, so record ordering can affect which value is retained. The parser lowercases keys and accepts key-only records by storing a null value, distinct from `key=` which stores an empty `GBytes`.

## Test Signals
Tests should cover valid key/value, key-only, empty-value, uppercase key normalization, duplicate suppression, invalid characters, empty keys, oversized records, records with multiple `=` characters, binary values after the separator, and lifetime expectations when consuming returned `GBytes`.
