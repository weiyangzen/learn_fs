<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-utils.c

## Purpose
Provides small GLib `GVariant` convenience helpers for byte arrays, empty string-to-variant dictionaries, fd-backed variant reads, mutable-builder creation from immutable variants, sorted-array lookup, and safe data access.

## Important APIs and Types
Exports `ot_gvariant_new_empty_string_dict`, `ot_gvariant_new_bytearray`, `ot_gvariant_new_ay_bytes`, `ot_variant_read_fd`, `ot_util_variant_builder_from_variant`, `ot_variant_bsearch_str`, and `ot_variant_get_data`.

## Control Flow
The constructors wrap GLib builders or `g_variant_new_from_data`. `ot_variant_read_fd` reads or mmaps an fd from a given offset via `ot_fd_readall_or_mmap`, then creates a `GVariant` from the resulting bytes. The builder-copy helper iterates children and adds each to a new `GVariantBuilder`. The binary search performs index comparisons against the first string child of each array element.

## State and Persistence
No durable state is stored here. The functions create refcounted GLib objects, sometimes sharing immutable backing storage with `GBytes`. `ot_variant_read_fd` maps persisted serialized data into process memory.

## Dependencies and Integration Points
Uses GLib/GIO, `otutil.h`, and lower-level fd utilities. Callers include OSTree metadata, summary, commit, and config code that frequently stores dictionaries and byte arrays in `GVariant` form.

## Risks
`ot_variant_bsearch_str` assumes the array is sorted and each child starts with a string; violating that contract can produce wrong lookup results or GLib warnings. `ot_gvariant_new_ay_bytes` trusts immutable `GBytes` lifetime. `ot_variant_get_data` turns GLib's nullable data result into a hard error and should be used where corrupted serialized variants are possible.

## Test Signals
Round-trip byte-array tests, fd/mmap read tests for trusted and untrusted variants, binary-search hit/miss/bounds tests, and corrupted-variant tests for `ot_variant_get_data` are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.c -->
