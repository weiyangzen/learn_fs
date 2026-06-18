# sources/distributed-fs/ceph-client/include/pcmcia/device_id.h

## Purpose

`device_id.h` provides initializer macros for PCMCIA driver device ID tables. The macros populate match flags, manufacturer/card IDs, product strings and hashes, function numbers, pseudo-function device numbers, and fake CIS override file names.

## Important APIs, types, and functions

Macros include `PCMCIA_DEVICE_MANF_CARD()`, `PCMCIA_DEVICE_FUNC_ID()`, product ID variants from `PCMCIA_DEVICE_PROD_ID1()` through `PCMCIA_DEVICE_PROD_ID1234()`, combined manufacturer/card/product macros, multifunction `PCMCIA_MFC_DEVICE_*` variants, pseudo multifunction `PCMCIA_PFC_DEVICE_*` variants, fake CIS override macros `PCMCIA_DEVICE_CIS_*`, `PCMCIA_MFC_DEVICE_CIS_*`, `PCMCIA_PFC_DEVICE_CIS_*`, and `PCMCIA_DEVICE_NULL`.

## Control flow

Drivers declare static PCMCIA ID tables with these macros. The PCMCIA core compares a device's parsed CIS fields against each entry's `match_flags`, IDs, hashes, function number, device number, and optional fake CIS requirement. Matching entries drive module autoloading and driver binding.

## State and persistence behavior

The header owns no mutable state. Macro output becomes static driver match-table data, and fake CIS file names persist as pointers in those entries.

## Dependencies and integration points

It is active only under `__KERNEL__` and depends on PCMCIA match flag and ID table structure definitions supplied by surrounding headers. It integrates with module alias generation, PCMCIA core matching, multifunction card handling, pseudo-function matching, and CIS override loading.

## Risks and test signals

Risks include passing incorrect product string hashes, missing terminators, choosing function vs device number matching incorrectly, stale fake CIS file names, and match flags that are too broad. Tests should cover module alias generation, table matching for manufacturer/card/product combinations, multifunction and pseudo-function devices, fake CIS override lookup, and null terminator handling.
