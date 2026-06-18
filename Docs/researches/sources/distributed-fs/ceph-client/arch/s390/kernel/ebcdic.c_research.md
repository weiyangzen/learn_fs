# sources/distributed-fs/ceph-client/arch/s390/kernel/ebcdic.c

## Purpose
Provides exported lookup tables for ASCII/EBCDIC conversion and EBCDIC case folding on s390. These tables support firmware, z/VM, DASD, and certificate-store paths that exchange EBCDIC text.

## Important APIs, Types, And Functions
Exports `_ascebc`, `_ebcasc`, `_ascebc_500`, `_ebcasc_500`, `_ebc_tolower`, and `_ebc_toupper`. The first pair maps ASCII IBM PC 437 to/from EBCDIC 037; the second pair maps to/from EBCDIC 500. Case tables map EBCDIC upper/lower bytes.

## Control Flow
No functions execute in this file. Inline/macros from `asm/ebcdic.h` index these arrays to convert buffers in place or byte by byte.

## State And Persistence
The conversion tables are global exported data and read-only by convention. No runtime state changes.

## Dependencies And Integration Points
Depends on Linux integer/export support and `asm/ebcdic.h`. Used by cpcmd, early machine strings, cert_store, DASD label tools, and other s390 firmware interfaces.

## Risks And Edge Cases
The tables encode codepage-specific behavior. Unsupported high ASCII bytes often map to `0x3f`, losing information. Case folding only makes sense for EBCDIC bytes and should not be applied to ASCII text.

## Test Signals
Signals include round-trip conversion tests for known strings, CP 037 vs CP 500 punctuation differences, cpcmd response conversion, certificate-name display, and exported symbol availability for modules.
