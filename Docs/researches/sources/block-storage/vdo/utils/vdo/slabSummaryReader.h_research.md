# File Research: sources/block-storage/vdo/utils/vdo/slabSummaryReader.h

Declares slab-summary loading support.

Key details:
- Exposes `readSlabSummary(UserVDO *vdo, struct slab_summary_entry **entriesPtr)`.
- Includes `encodings.h`, `types.h`, and `userVDO.h`.

Minor note:
- The closing include-guard comment says `SLAB_SUMMARY_UTILS_H`, while the actual guard is `SLAB_SUMMARY_READER_H`.
