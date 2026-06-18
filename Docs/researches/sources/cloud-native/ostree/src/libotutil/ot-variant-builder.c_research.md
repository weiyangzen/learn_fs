<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.c -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-builder.c

## Purpose
Implements `OtVariantBuilder`, a streaming serializer for container `GVariant` values into an existing file descriptor. It exists for cases where OSTree needs to construct serialized variants without first materializing the whole value in memory, while staying byte-compatible with GLib's GVariant layout.

## Important APIs and Types
The public functions are `ot_variant_builder_new`, `ot_variant_builder_ref`, `ot_variant_builder_unref`, `ot_variant_builder_open`, `ot_variant_builder_close`, `ot_variant_builder_end`, `ot_variant_builder_add_from_fd`, `ot_variant_builder_add_value`, and `ot_variant_builder_add`. Internal types include copied GLib-style `GVariantTypeInfo`, `ArrayInfo`, `TupleInfo`, `GVariantMemberInfo`, `OtVariantBuilderInfo`, and `OtVariantBuilder`. The helper code computes fixed sizes, alignments, tuple member offset formulas, and serialized offset-table widths.

## Control Flow
Construction creates a top-level `OtVariantBuilderInfo` for a container type and links it as `builder->head`. Adding a value validates child count and type constraints, writes alignment padding to the target fd, copies child bytes from a `GVariant` or source fd, then updates offsets and offset-table bookkeeping. Opening a nested container pushes a new info frame; closing finalizes the child, posts it into the parent, and pops the stack. `ot_variant_builder_end` writes offset tables for tuples, dict entries, and variable-size arrays.

## State and Persistence
Persistent output is the serialized GVariant byte stream written to `builder->fd`. In-memory state tracks nested containers, child end offsets, expected type progression, previous item type for homogeneous containers, and min/max child counts. Global cached `GVariantTypeInfo` data is shared through a recursive mutex and hash table with manual refcounts.

## Dependencies and Integration Points
Depends on GLib/GIO `GVariant`, `GVariantType`, `GArray`, atomics, slices, and libglnx helpers such as `glnx_loop_write`, `glnx_regfile_copy_bytes`, and `glnx_throw_errno`. It integrates with OSTree metadata and summary-writing code that needs deterministic serialized variants.

## Risks
The highest risk is layout compatibility with GLib: padding, offset-table order, offset width calculation, variant type suffixes, and tuple fixed-size rules must match exactly. Assertions guard many type-state errors, so invalid caller sequencing can abort rather than return a `GError`. Large offsets depend on correct `gsize`/`guint64` handling. The type-info cache is global and must remain refcount-safe under concurrent builders.

## Test Signals
Useful signals are byte-for-byte comparisons against `g_variant_get_data()` for nested arrays, tuples, dict entries, maybes, variants, empty containers, and large offset tables; fd-copy tests for `ot_variant_builder_add_from_fd`; malformed sequence tests for open/close/end; and sanitizer or valgrind runs for type-info cache lifetimes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.c -->
