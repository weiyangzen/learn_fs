# sources/distributed-fs/openafs/src/vlserver/cnvldb.h

## Purpose

`cnvldb.h` defines legacy VLDB on-disk header and entry structures used by `cnvldb.c` to convert older VLDB formats. It captures versions 1, 2, and 3 layout differences around server address capacity, hash tables, SIT multihome pointers, and per-entry server arrays.

## Important APIs, Types, And Structures

- `vital_vlheader_1` and typedefs `vital_vlheader1`, `vital_vlheader2`, and `vital_vlheader3` describe shared vital header fields: version, header size, free/eof pointers, alloc/free counts, max volume id, and per-type totals.
- `vlheader_1` has 31 mapped addresses plus name/id hash tables.
- `vlheader_2` and `vlheader_3` expand mapped addresses to 255 and add `SIT`.
- `vlentry_1` and `vlentry_2` use fixed 8-element server arrays and include legacy spare fields.
- `vlentry_3` uses `MAXSERVERS` server arrays and removes most spare fields unless `obsolete_vldb_fields` is enabled.

## Control Flow

There is no executable control flow. Conversion code casts these layouts over database bytes, copies shared fields, and conditionally expands/shrinks headers and entries based on requested source/target version.

## State And Persistence Behavior

These structs are persistent ABI definitions for historical VLDB files. Their field order, sizes, and network-byte-order usage determine how conversion preserves volume ids, lock data, clone ids, hash links, names, server ids, partitions, and flags.

## Dependencies And Integration Points

The header relies on OpenAFS integer types, `MAXSERVERS`, and VL constants supplied by includers such as `vlserver.h`. It is installed by the vlserver makefile for tooling that needs legacy conversion layouts.

## Risks And Edge Cases

- No include guard is present in this file.
- The structs intentionally mirror old binary layouts; normal cleanup or padding changes would corrupt conversion.
- Version 1 has only 31 address slots and versions 1/2 have only 8 server slots per entry, so downgrade conversions can fail or lose unsupported topology.

## Test Signals

Compile tests should include this header through `cnvldb.c` and installed headers. Binary fixture tests should assert exact `sizeof` values and offsets for each legacy header/entry layout.
