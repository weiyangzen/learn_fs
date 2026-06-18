# sources/cloud-native/ostree/src/libotutil/ot-gio-utils.h

## Purpose
Declares GIO helper APIs and common fast query-info attribute strings.

## Important APIs, Types, And Functions
Defines `OSTREE_GIO_FAST_QUERYINFO`, declares path formatting, fsync replace, unlink-ignore-missing, enumerator iteration compatibility wrapper, `ot_file_get_path_cached`, alias `gs_file_get_path_cached`, and `ot_format_human_duration`.

## Control Flow
The GLib 2.44+ inline wrapper delegates to GLib's `g_file_enumerator_iterate` while suppressing deprecation warnings, then redefines `g_file_enumerator_iterate` to the local wrapper name.

## State And Persistence Behavior
No global state in the header. Declared functions may cache paths or write files.

## Dependencies And Integration Points
Depends on GIO and GLib version macros. The fast query string is used anywhere OSTree needs cheap metadata without opening files.

## Risks
The macro redefinition of `g_file_enumerator_iterate` can surprise code that expects the raw GLib symbol. The fast query string must remain synchronized with metadata needs.

## Test Signals
Compile coverage across GLib versions and metadata-query tests using `OSTREE_GIO_FAST_QUERYINFO` are useful.
