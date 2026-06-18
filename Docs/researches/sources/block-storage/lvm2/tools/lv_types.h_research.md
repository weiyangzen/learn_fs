# File Research: sources/block-storage/lvm2/tools/lv_types.h

## Purpose
`lv_types.h` is a macro list of LV type names used by command definitions.

## Contents
It lists linear, striped, snapshot, cache, cachepool, integrity, mirror, RAID variants, thin/thinpool, VDO/vdopool, writecache, zero, and error types.

## Integration Notes
Callers define `lvt(name)` to generate enums and lookup tables. Type strings are used in command-definition suffixes such as `LV_type`. The file notes that `toollib.c:_lv_is_type()` must be updated when new types are added.
