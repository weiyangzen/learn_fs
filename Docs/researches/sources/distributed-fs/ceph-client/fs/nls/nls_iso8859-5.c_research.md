# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-5.c

## Purpose

This generated NLS module registers ISO 8859-5 for Cyrillic. It maps one-byte Cyrillic charset values to Unicode Cyrillic code points and provides exact reverse conversion for filesystem names.

## Important APIs, Types, and Functions

`charset2uni[256]` is the decode table. Reverse pages `page00`, `page04`, and `page21` map common symbols, Cyrillic characters, and one symbol page entry back to bytes. `charset2lower` and `charset2upper` perform byte-level folding for Cyrillic upper/lower pairs. The registered table uses `.charset = "iso8859-5"`.

## Control Flow

The generated `uni2char()` and `char2uni()` callbacks use one-byte table lookup and standard NLS errno returns. No multibyte logic or allocation exists.

## State and Persistence Behavior

Tables are immutable and shared. Module persistence is only the NLS registry entry. Charset table values define persistent filename interpretation for ISO 8859-5 mounts.

## Dependencies and Integration Points

The module integrates with Linux filesystems through the NLS registry and depends only on core kernel module/NLS headers.

## Risks

Cyrillic mappings around `U+0400..U+045F` and byte-level case-folding offsets must remain exact. Using zero as the invalid sentinel means `U+0000` cannot be encoded or decoded.

## Test Signals

Round-trip Russian and broader Cyrillic letters, validate Cyrillic case folding, test unmapped Unicode pages, and check module registration lifecycle.
