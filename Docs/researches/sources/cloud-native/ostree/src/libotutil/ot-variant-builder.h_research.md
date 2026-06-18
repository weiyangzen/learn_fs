<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.h -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-builder.h

## Purpose
Declares the public `OtVariantBuilder` streaming GVariant builder interface used by libotutil clients.

## Important APIs and Types
The header forward-declares `struct _OtVariantBuilder` and exposes constructors, ref/unref, `end`, nested `open`/`close`, value addition from an fd or `GVariant`, varargs addition, and a parsed-add declaration. It also registers `G_DEFINE_AUTOPTR_CLEANUP_FUNC` for automatic cleanup.

## Control Flow
The header defines no executable logic, but its API implies the required sequence: create a builder for a container type, add values or open/close nested containers, end the active container, and unref the builder.

## State and Persistence
State is opaque to callers. Persistence occurs through the fd supplied to `ot_variant_builder_new`; callers own opening and eventual closing of that fd.

## Dependencies and Integration Points
Includes `gio/gio.h` and `libglnx.h`; consumed through `otutil.h` and direct includes by code writing serialized GVariant metadata.

## Risks
The declaration of `ot_variant_builder_add_parsed` has no implementation in the paired source in this subset, so build coverage must verify whether it is implemented elsewhere or stale. Callers must pass container types and manage fd lifetime correctly.

## Test Signals
Compile/link tests are important for the full declared API. API-level tests should use autoptr cleanup and nested builder sequencing from external translation units.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.h -->
