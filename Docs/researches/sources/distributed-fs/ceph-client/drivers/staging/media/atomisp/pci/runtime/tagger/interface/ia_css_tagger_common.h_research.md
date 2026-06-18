# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/tagger/interface/ia_css_tagger_common.h

## Purpose

`ia_css_tagger_common.h` defines the shared host/SP data shape for AtomISP tagger circular-buffer elements. The tagger tracks frame/parameter associations and small per-element status flags used by the CSS continuous-frame pipeline.

## Important APIs, Types, and Functions

`MAX_CB_ELEMS_FOR_TAGGER` is defined as 14 and documented as one less than `NUM_CONTINUOUS_FRAMES` in `sh_css_internal.h`, where the local value is 15. `ia_css_tagger_buf_sp_elem_t` contains a `u32 frame`, `u32 param`, `u8 mark`, `u8 lock`, and `u8 exp_id`; `exp_id` is noted as debugging-only.

The file declares no functions. It is an ABI header for code that needs to allocate, share, or interpret tagger circular-buffer entries.

## Control Flow

Control flow is external to this header. Producer code writes frame and parameter identifiers into circular-buffer entries, marks or locks entries as ownership changes, and firmware/host consumers read those fields while coordinating continuous capture. The constant establishes the ring capacity expected by tagger code.

## State and Persistence Behavior

The header owns no storage. State exists wherever arrays of `ia_css_tagger_buf_sp_elem_t` are allocated, typically in CSS/SP communication memory. The fields are transient runtime metadata for frame processing and do not persist across driver reset or firmware restart.

## Dependencies and Integration Points

The header depends on `system_local.h` and `type_support.h` for shared AtomISP scalar types. Its capacity contract is explicitly coupled to `NUM_CONTINUOUS_FRAMES` in `sh_css_internal.h` and to the SP tagger implementation mentioned in comments. Host and SP code must agree on field layout and ring size.

## Risks and Edge Cases

There is no compile-time assertion tying `MAX_CB_ELEMS_FOR_TAGGER` to `NUM_CONTINUOUS_FRAMES - 1`, so drift can silently break circular-buffer behavior. The struct has three trailing byte fields after two 32-bit values; padding and total size must match firmware expectations even though this header does not assert the size. The `mark` and `lock` fields are plain bytes, not atomic synchronization primitives, so correctness depends on the surrounding host/SP communication protocol.

## Test Signals

ABI tests should verify `MAX_CB_ELEMS_FOR_TAGGER == NUM_CONTINUOUS_FRAMES - 1`, check `sizeof` and field offsets of `ia_css_tagger_buf_sp_elem_t` against firmware expectations, and exercise tagger wraparound with 14 usable entries. Pipeline tests should watch for stale locks, overwritten marks, and correct `exp_id` propagation in continuous-frame debugging traces.
