# File Research: sources/block-storage/lvm2/tools/lv_props.h

## Purpose
`lv_props.h` is a macro list of LV property predicates used in command-definition rules.

## Contents
It lists LV state, visibility, sub-LV role, snapshot/origin, cache, COW, historical, RAID tracking, and RAID integrity properties.

## Integration Notes
Callers define `lvp(name)` to generate enums and lookup tables. The file notes that `toollib.c:_lv_is_prop()` must be updated when new properties are added.
