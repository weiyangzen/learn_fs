# File Research: sources/block-storage/lvm2/lib/report/columns-devtypes.h

This header defines report columns for the `devtypes` reporting command via `FIELD(...)` macros.

Columns:
- `devtype_name`: device type name as it appears in `/proc/devices`.
- `devtype_max_partitions`: maximum partitions/minors reserved for each device.
- `devtype_description`: device type description.

Role:
- Include-time column definition consumed by LVM report infrastructure.

Risks:
- Like other column headers, it depends on an includer-provided `FIELD` macro and matching display functions/types.
