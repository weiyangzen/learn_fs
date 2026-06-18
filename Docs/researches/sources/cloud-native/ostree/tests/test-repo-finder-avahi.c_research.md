# sources/cloud-native/ostree/tests/test-repo-finder-avahi.c

## Purpose
This C unit test validates basic construction of `OstreeRepoFinderAvahi` and private Avahi TXT-record parsing used for peer repository discovery.

## Important APIs, Types, And Functions
The file includes `ostree-repo-finder-avahi-private.h` and tests `ostree_repo_finder_avahi_new()` and `_ostree_txt_records_parse()`. It uses `AvahiStringList`, `GHashTable`, `GBytes`, GLib test APIs, and autoptr cleanup for `AvahiStringList`.

## Control Flow
`test_repo_finder_avahi_init()` constructs the finder with default and explicit `GMainContext`. TXT record tests build Avahi string lists from byte vectors, call `_ostree_txt_records_parse()`, and verify accepted keys, binary values, empty values, missing values, duplicate-first behavior, and case-insensitive key normalization.

## State And Persistence
There is no persistent state. All data is in-memory Avahi TXT lists and hash tables. The finder constructor may hold a main context but no network discovery is exercised.

## Dependencies And Integration Points
This integrates GLib, GObject, Avahi TXT string structures, and private OSTree Avahi repo-finder parsing. It is a unit-level guard for DNS-SD service metadata consumed by broader repo discovery.

## Risks
TXT parsing must reject malformed records, lowercase keys consistently, preserve first duplicate values per RFC 6763, and distinguish missing values from empty byte strings. The test explicitly notes that service processing itself still lacks coverage.

## Test Signals
GLib test paths include `/repo-finder-avahi/init`, `/txt-records/parse`, `/duplicates`, `/case-sensitivity`, and `/empty-and-missing`.
