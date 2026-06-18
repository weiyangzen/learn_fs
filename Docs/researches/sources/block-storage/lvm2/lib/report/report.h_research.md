# File Research: sources/block-storage/lvm2/lib/report/report.h

## Purpose

`report.h` declares public report types, selection state, command-log row shape, and reporting APIs used by LVM command and processing code.

## Main Definitions

Report type bit flags:

- `CMDLOG`, `FULL`
- LV reports: `LVS`, `LVSINFO`, `LVSSTATUS`, `LVSINFOSTATUS`
- PV/VG/segment reports: `PVS`, `VGS`, `SEGS`, `PVSEGS`, `LABEL`
- `DEVTYPES`

Heading modes:

- `REPORT_HEADINGS_UNKNOWN`
- `REPORT_HEADINGS_NONE`
- `REPORT_HEADINGS_ABBREV`
- `REPORT_HEADINGS_FULL`

`struct selection_handle` wraps a selection-only `dm_report`, preserves original/effective report type masks, and stores the selected result.

`struct cmd_log_item` is the row object for command-log reporting, including sequence number, type, context, object identity, group identity, message, errno, and return code.

## API Surface

Declared APIs include:

- Report format lifecycle: `report_format_init`, `report_format_destroy`
- Report creation: `report_init`, `report_init_for_selection`
- Selection helpers: `report_get_single_selection`, `report_for_selection`
- Metadata helpers: `report_headings_str_to_type`, `report_get_prefix_and_desc`
- Emission and cleanup: `report_object`, `report_devtypes`, `report_cmdlog`, `report_output`, `report_free`
- Command-log helpers: `report_reset_cmdlog_seqnum`, `report_current_object_cmdlog`
- Standard command-log constants for object name and success/failure strings.

## Dependencies

The header exposes metadata, label, and activation types by including `metadata-exported.h`, `label.h`, and `activate.h`.
