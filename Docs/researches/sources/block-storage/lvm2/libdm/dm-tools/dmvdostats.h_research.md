# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.h

Purpose: declares the VDO stats helper API shared between `dmsetup.c` and `dmvdostats.c`.

Read coverage: complete file read, 39 lines.

Key contents:
- Includes `libdm/libdevmapper.h` for `struct dm_report`, `uint32_t`, and libdm allocation conventions.
- Declares display-unit accessors implemented by `dmsetup.c`: `get_disp_factor()`, `get_disp_units()`, and `show_units()`.
- Declares `vdo_get_stats()` for retrieving raw VDO stats text; the caller must release the returned string with `dm_free()`.
- Declares verbose output and report-mode functions: `vdostats_print_verbose()`, `vdostats_report_init()`, and `vdostats_report_device()`.

Dependencies:
- Coupled to `dmsetup.c` for unit-display state and to `dmvdostats.c` for implementation.
- Uses libdevmapper report types rather than defining a separate reporting abstraction.

Risk and edge cases:
- Ownership of `vdo_get_stats()` output is part of the API contract; callers must use `dm_free()`, not plain `free()`.
- The display-unit functions expose process-global CLI state, so VDO report formatting follows the active `dmsetup` option state.
