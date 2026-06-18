# File Research: sources/block-storage/cryptsetup/lib/integrity/integrity.h

Defines dm-integrity superblock layout, flags, and helper prototypes.

Key points:
- Superblock magic is `"integrt"` and supported versions are 1 through 6.
- Flags describe journal MAC, recalculation, dirty bitmap, fixed padding, fixed HMAC, and inline mode.
- Packed `struct superblock` matches kernel dm-integrity on-disk metadata, including tag size, journal sections, data sectors, flags, sector/block log fields, recalc sector, and salt.
- Declares superblock read/dump/data-sector helpers, key/tag-size helpers, format, activation, dmd creation, and dmd activation.

Storage relevance:
- Internal ABI between cryptsetup integrity code and the on-disk/kernel dm-integrity metadata format.
