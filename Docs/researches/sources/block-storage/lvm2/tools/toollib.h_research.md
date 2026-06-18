# File Research: sources/block-storage/lvm2/tools/toollib.h

## Purpose
`toollib.h` declares the shared processing interface used by LVM2 command implementations.

## Main Types
It defines `struct processing_handle`, which carries parent processing context, selection-report state, historical-LV inclusion, and caller-specific `custom_handle` data.

It also defines callback typedefs for processing one VG, PV, label, LV, LV segment, and PV segment, plus a `check_single_lv_fn_t` pre-check callback.

## Main API Surface
The header declares object iterators:
- `process_each_vg()`
- `process_each_pv()`
- `process_each_label()`
- `process_each_lv()`
- `process_each_lv_in_vg()`
- `process_each_pv_in_vg()`
- segment iteration helpers for LVs and PVs

It also declares selection helpers, name parsing, option-list helpers, PV/VG creation parameter helpers, activation and refresh helpers, pool/cache/VDO/writecache/integrity option parsers, tag mutation, persistent major/minor validation, LV name validation, LV removal, LV type lookup, root VG UUID discovery, and persistent-reservation start inclusion.

## Selection Contract
The header documents why reporting commands disable `internal_report_for_select`: their normal report path already performs selection and output together, while non-reporting commands need hidden internal reports to evaluate `--select`.

## Integration Notes
This is the public contract between individual command files and `toollib.c`. The callbacks and `processing_handle` state define how commands participate in shared traversal, selection, reporting, and cleanup.
