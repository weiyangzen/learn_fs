# File Research: sources/cow-pools/nilfs-utils/include/util.h

General utility macros. It defines `likely`, `unlikely`, `BUG`, `BUG_ON`, compile-time assertion, git revision embedding macro, `ARRAY_SIZE`, type-safe `min/max`, `container_of`, `roundup`, `div64`, and 64-bit wraparound comparison helpers.

These macros are used across command and library code for branch prediction, bounds checks, build metadata, and sequence-number comparisons.
