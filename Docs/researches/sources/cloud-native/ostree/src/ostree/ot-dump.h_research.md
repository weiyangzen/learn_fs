# sources/cloud-native/ostree/src/ostree/ot-dump.h

## Purpose
Declares shared dump/formatting APIs used by OSTree CLI commands to render variants, objects, summaries, summary metadata, and GPG keys.

## Important APIs, Types, And Functions
`OstreeDumpFlags` defines `OSTREE_DUMP_NONE`, `OSTREE_DUMP_RAW`, and `OSTREE_DUMP_UNSWAPPED`. Declared functions are `ot_dump_variant()`, `ot_dump_object()`, `ot_dump_summary_bytes()`, `ot_dump_summary_metadata_keys()`, `ot_dump_summary_metadata_key()`, and `ot_dump_gpg_key()`.

## Control Flow
The header has no runtime control flow. It includes GIO and `ostree-core.h`, defines the flags enum, and exposes the formatter prototypes implemented in `ot-dump.c`.

## State And Persistence
No state is stored here. The flags influence output behavior in callers but do not imply persistence.

## Dependencies And Integration Points
Consumers include `ot-builtin-show.c`, `ot-builtin-log.c`, `ot-builtin-summary.c`, and remote key listing code. The header exposes `GVariant`, `GBytes`, `OstreeObjectType`, and GLib error conventions to callers.

## Risks And Edge Cases
`OSTREE_DUMP_NONE` is defined as `(1 << 0)` rather than zero, so code must not assume "none" means no bits set. Callers generally initialize flags to `OSTREE_DUMP_NONE` and OR additional bits, and implementations check only RAW/UNSWAPPED. Any future flag checks must account for this unusual value.

## Test Signals
Build and command tests should verify all dump consumers compile and that raw/unswapped flags behave as expected. Unit coverage around `OSTREE_DUMP_NONE` should prevent future bitmask assumptions from changing output unintentionally.
