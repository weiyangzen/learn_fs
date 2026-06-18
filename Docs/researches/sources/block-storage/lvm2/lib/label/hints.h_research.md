# File Research: sources/block-storage/lvm2/lib/label/hints.h

## Summary
Declares the hint-file data structure and public hint cache APIs.

## Main Contents
`struct hint` stores list linkage, device number, path name, VG name, PVID, and a `chosen` bit indicating that the hint’s device was selected for scanning.

## API Surface
Declares hint list freeing, hint writing, clearing, invalidation, loading/applying, validation, shutdown cleanup, `pvscan --cache` recreation setup, and single-VG command-argument extraction.

## Risks And Invariants
Fixed-size aligned string buffers use `PATH_MAX`, `NAME_LEN`, and `ID_LEN + 1`; producers must keep parsed names bounded and null-terminated.
