# File Research: sources/block-storage/lvm2/lib/device/device-types.h

## Purpose
Declares the static known-device-type table format used by `dev-type.c` to interpret `/proc/devices` block major names.

## Main Contents
- `DEV_KNOWN_NAME_LEN` is 15, bounding the embedded name field.
- `dev_known_type_t` contains a block-device major name prefix, max partition count/granularity, and a description string.
- `extern const dev_known_type_t dev_known_types[]` declares the table defined in `dev-type.c`.

## Dependencies
Only requires `<stdint.h>`.

## Risk Notes
Names are stored in a fixed-size array. New built-in names must fit `DEV_KNOWN_NAME_LEN`, and ordering matters for prefix cases such as `mdp` before `md`.
