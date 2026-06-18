# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmvdostats.c

Purpose: implements VDO statistics retrieval and formatting for `dmsetup vdostats`/`dmvdostats`, supporting legacy-style verbose output and `dm_report` tabular output.

Read coverage: complete file read, 639 lines.

Key responsibilities:
- Sends the `stats` message to a named VDO device with `DM_DEVICE_TARGET_MSG` and returns the kernel target response string.
- Parses VDO stats through `dm_vdo_stats_parse()` in libdevmapper, using full parsing for verbose output and basic parsing for tabular report output.
- Computes derived values: physical size, logical size, used size, available size, write amplification, used percentage, saving percentage, and 512-byte emulation state.
- Computes verbose-only journal backlog fields: entries batching/writing and blocks batching/writing.
- Applies legacy label fixups by stripping selected prefixes, renaming fields, hiding obsolete fields, and printing `N/A` for recovery/read-only/abnormal modes.
- Prints verbose key/value output with aligned labels and inserted derived fields at stable positions.
- Defines a VDO `dm_report` object type and fields for device name, physical size, used size, available size, used percent, and saving percent.
- Initializes VDO reports with default fields and optional user fields, sorting, separator, output flags, and selection expression.
- Emits one report row per VDO device.

Important entry points:
- `vdo_get_stats()` retrieves raw stats text from the device-mapper VDO target.
- `vdostats_print_verbose()` parses full stats and prints legacy verbose output.
- `vdostats_report_init()` creates the tabular report handle.
- `vdostats_report_device()` parses basic stats and submits one object to `dm_report`.

Dependencies:
- Includes `libdm/misc/dm-logging.h`, `libdm/libdevmapper.h`, and `dmvdostats.h`.
- Depends on libdevmapper VDO parsing structures: `dm_vdo_stats_full`, `dm_vdo_stats`, and `dm_vdo_stats_field`.
- Uses display-unit helpers exported from `dmsetup.c`: `get_disp_units()`, `get_disp_factor()`, and `show_units()`.

Risk and edge cases:
- Missing or unparsable stats strings return failure without partial output.
- Many derived values become `N/A` outside normal VDO operating mode, and negative sentinel values are used internally for unavailable sizes/percentages.
- Available size is guarded against used-size overflow beyond physical size.
- Percent calculations assume block counters fit into signed intermediate arithmetic.
- Label fixups mutate parsed field labels and values in place, so they depend on libdevmapper field buffer sizes and exact label names.
