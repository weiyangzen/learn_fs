# File Research: sources/block-storage/kvdo/vdo/messageStats.h

## Purpose
Declares the public stats serialization entry point.

## API
- `int vdo_write_stats(struct vdo *vdo, char *buf, unsigned int maxlen);`

## Integration Notes
Includes `types.h` for the opaque VDO type definitions. The implementation lives in `messageStats.c`.
