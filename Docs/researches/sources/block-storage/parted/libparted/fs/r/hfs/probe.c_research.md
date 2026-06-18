# File Research: sources/block-storage/parted/libparted/fs/r/hfs/probe.c

HFS geometry validation and wrapper probing.

Key behavior:
- `hfsc_can_use_geom()` rejects devices whose sector size is not 512 bytes.
- `hfs_and_wrapper_probe()` reads the classic HFS MDB at sector 2, validates HFS signature, computes the expected end of the HFS allocation area, and searches one allocation block past it for an alternate MDB signature.
- Returns a geometry covering the HFS or HFS wrapper length when detected.

Important dependencies:
- HFS MDB structure from `hfs.h`.
- Libparted geometry and exception APIs.

Role:
- Used by HFS/HFS+ open and probing to detect HFS wrappers around embedded HFS+ volumes.
