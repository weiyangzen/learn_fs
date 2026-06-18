# File Research: sources/cow-pools/nilfs-utils/bin/lssu.c

Implements `lssu`, the segment usage lister. It supports hiding or showing clean segments, starting index, line limit, latest-usage assessment, and protection period parsing.

Normal mode opens NILFS read-only and pages `nilfs_suinfo` entries with `nilfs_get_suinfo()`. Latest-usage mode also opens raw storage and the cleaner lock, maps a protection period to a checkpoint with `nilfs_cnormap_track_back()`, and assesses live blocks with `nilfs_assess_segment()`.

Output marks segment state flags: active, dirty, error, and in latest mode protected. Latest mode prints live block counts and usage percentages, treating protected segments as fully live.
