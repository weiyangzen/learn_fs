# Research: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-ru.c

## Purpose

This file registers KOI8-RU for Belarusian by wrapping the existing `koi8-u` NLS table and overriding the small set of bytes/code points that differ. It avoids duplicating a full generated mapping table.

## Important APIs, Types, and Functions

`static struct nls_table *p_nls` stores the loaded `koi8-u` table. `uni2char()` special-cases Unicode `U+040E` and `U+045E` to bytes `0xBE` and `0xAE`, while delegating most work to `p_nls->uni2char()`. `char2uni()` is intended to special-case the corresponding input bytes and otherwise delegate. The registered table is `.charset = "koi8-ru"` and borrows `charset2upper`/`charset2lower` from KOI8-U during init.

## Control Flow

Initialization loads `koi8-u`, installs its case tables, and registers KOI8-RU. Exit unregisters and unloads KOI8-U. Encoding checks output capacity, handles the two Belarusian short-U code points, suppresses two KOI8-U box-drawing mappings by returning 0, and delegates other values. Decoding reads a byte and either maps a special byte to `U+040E`/`U+045E` or delegates to KOI8-U.

## State and Persistence Behavior

The module holds a runtime reference to KOI8-U in `p_nls`. There are no generated local tables and no per-consumer state. Persistent filename interpretation depends on both this adapter and the loaded KOI8-U table.

## Dependencies and Integration Points

The file depends on another NLS module (`koi8-u`) and on the NLS registry. Filesystems see a normal `struct nls_table` for `koi8-ru`.

## Risks

The `char2uni()` condition is a high-risk area: the code checks `((*rawstring & 0xef) != 0xae)` before mapping to the two special Unicode values, which is counterintuitive for a two-byte override pattern where only `0xAE` and `0xBE` should be special. Regression tests should pin this behavior or detect it as a bug against the intended KOI8-RU mapping. Returning `0` from `uni2char()` for selected box-drawing code points is also unusual because NLS callbacks normally return a byte count or negative errno.

## Test Signals

Load KOI8-U and KOI8-RU together, test `U+040E`/`U+045E` to `0xBE`/`0xAE`, test decode of `0xAE` and `0xBE`, test ordinary KOI8-U delegated bytes, test the suppressed `U+255D`/`U+256C` behavior, and verify unload releases the dependent NLS table.
