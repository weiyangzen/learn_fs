# File Research: sources/block-storage/lvm2/lib/device/dev-cache.h

## Purpose
Declares the public device-cache API and `struct dev_filter` interface.

## Public Surface
The header exposes:
- Device initialization and global cache lifecycle.
- Device scan, path/devno/PVID lookup, alias verification, preferred name selection, and iteration.
- VGID/LVID device-list lookup.
- Active DM device cache update/lookup/destruction.
- Sysfs value/binary readers.
- Devices-file and one-device setup routines.
- Open-device leak checking.

## Data Model
`struct dev_filter` defines the filtering contract used by cache lookup and iterators: `passes_filter`, `destroy`, `wipe`, private state, use count, and filter name.

## Integration
Included by command setup, label scanning, device filters, activation, and modules that need stable `struct device` lookup.

## Risk Notes
The header exposes a global cache model, so callers must respect lifecycle ordering: initialize before setup/scan, avoid closing paths behind the cache without invalidation, and call exit checks to catch leaked opens.
