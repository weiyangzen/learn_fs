<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-utils.h

## Purpose
Declares libotutil helpers for creating, reading, copying, searching, and safely accessing `GVariant` data.

## Important APIs and Types
The header exposes byte-array constructors, empty `a{sv}` creation, `ot_variant_read_fd`, `ot_util_variant_builder_from_variant`, `ot_variant_bsearch_str`, and `ot_variant_get_data`.

## Control Flow
No control flow is implemented. The declarations define a utility API that returns newly allocated/refcounted GLib objects or boolean success with `GError`.

## State and Persistence
The API works with serialized variant data from file descriptors and refcounted memory buffers, but the header stores no state.

## Dependencies and Integration Points
Includes `gio/gio.h` and is pulled into the broad `otutil.h` umbrella. It is part of the internal utility surface shared by command and library code.

## Risks
Callers must respect transfer ownership and the sorted-array precondition for `ot_variant_bsearch_str`. Mismatched trusted flags in `ot_variant_read_fd` can shift validation responsibility to callers.

## Test Signals
Compile-time API consumers, ownership/leak tests, and negative tests for corrupt serialized data exercise the contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.h -->
