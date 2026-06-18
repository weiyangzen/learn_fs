# File Research: sources/block-storage/lvm2/lib/misc/lvm-percent.h

This header defines percentage-related enums and helper declaration.

Content:
- `sign_t`: none, plus, minus.
- `percent_type_t`: none, VG, free, LV, PVs, origin.
- `LVM_PERCENT_MERGE_FAILED` aliases `DM_PERCENT_FAILED`.
- Declares `percent_of_extents()`.

Role:
- Shared parsing/reporting vocabulary for percentage-sized LVM operations.
