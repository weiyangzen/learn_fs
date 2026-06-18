# File Research: sources/block-storage/kvdo/vdo/dump.h

## Purpose
Declares VDO diagnostic dump entry points.

## API
- `vdo_dump()`: parse option arguments and dump selected VDO diagnostics.
- `vdo_dump_all()`: dump every supported diagnostic category.
- `dump_data_vio()`: callback-compatible dumper for individual data VIO objects.

## Integration
Used by DM messages and shutdown paths when `dump-on-shutdown` is enabled.
