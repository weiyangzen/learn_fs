# sources/distributed-fs/ceph-client/mm/kasan/report_sw_tags.c

## Purpose

`report_sw_tags.c` provides software tag-based KASAN report helpers. It uses shadow memory as a tag store, compares pointer tags against shadow tags, and exposes minimal stack-address description support for stack-tag reports.

## Important APIs, Types, and Functions

The helper API consists of `kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_metadata_fetch_row()`, `kasan_print_tags()`, and optional `kasan_print_address_stack_frame()`. It relies on `get_tag()`, `kasan_reset_tag()`, `kasan_mem_to_shadow()`, `addr_has_metadata()`, and `KASAN_TAG_INVALID`.

## Control Flow

The first-bad-address helper strips the pointer tag, then walks shadow granules until the stored tag differs from the pointer tag. Allocation-size discovery walks the object's shadow tags until it sees `KASAN_TAG_INVALID`. Metadata rows are copied directly from shadow memory. Tag printing reports the pointer tag and current shadow tag. The stack-frame printer only identifies that the buggy address belongs to the current task stack and does not decode frame objects like generic KASAN.

## State and Persistence Behavior

The file owns no persistent state. It reads per-granule software tags stored in KASAN shadow memory and object/cache metadata supplied by slab code.

## Dependencies and Integration Points

It integrates with common reporting and the shared tag-mode classifier in `report_tags.c`. It also pairs with `sw_tags.c`, which performs runtime checks and writes software tags via `kasan_poison()`.

## Risks and Edge Cases

Like hardware tags, software tags are probabilistic and can miss bugs when an invalid access happens to carry a matching tag. Stale or overwritten shadow tags can make allocation-size and first-bad-address discovery imprecise. Stack reporting is less detailed than generic mode.

## Test Signals

Signals include SW_TAGS KASAN reports that show mismatched pointer and memory tags, first-bad-address movement across valid tagged granules, invalid-tag allocation-size fallback, and compiler HWASAN report callback coverage.
