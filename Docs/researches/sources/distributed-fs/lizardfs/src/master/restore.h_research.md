# sources/distributed-fs/lizardfs/src/master/restore.h

## Purpose

`restore.h` declares the public changelog restore API. The source was read as a complete 29-line header.

## Important APIs, Types, and Functions

It defines `enum class RestoreRigor { kIgnoreParseErrors, kDontIgnoreAnyErrors }` and declares `restore_reset`, `restore`, and `restore_setverblevel`.

## Control Flow

The header has no executable flow. Callers reset restore state, pass changelog entries and versions to `restore`, and optionally set verbosity.

## State and Persistence Behavior

Restore state is implementation-global and reset by `restore_reset`. Persistent effects occur through filesystem apply functions in `restore.cc`.

## Dependencies and Integration Points

It depends on platform/inttypes and is included by metarestore/master code that replays changelogs.

## Risks and Edge Cases

Because restore state is global, multiple concurrent restore streams are not supported. Callers must pass entries in changelog order with correct version values.

## Test Signals

Compile coverage and end-to-end restore tests that call the public API with ordered, duplicate, missing, and malformed entries.
