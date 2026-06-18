# File Research: sources/block-storage/lvm2/lib/metadata/takeover_matrix.h

This header defines the RAID takeover dispatch matrix used by LVM metadata code to choose a conversion function between segment layouts.

Core content:
- Maps short macro names such as `lin_r0`, `r0__r1`, `r45_r6`, and `str_r10` to `_takeover_from_*` functions.
- Defines `_segtype_index[]`, translating segment flags into matrix columns for linear, striped, mirror, raid0, raid0_meta, raid1, raid4/5, raid6, raid10, raid01, and other.
- Defines `_takeover_fns[][11]`, where rows are current segment type and columns are requested segment type.
- Uses `N` for `_takeover_noop` and `X` for `_takeover_unsupported`.

Dependencies:
- Expects `takeover_fn_t` and all `_takeover_from_*` functions to be declared in the including translation unit.
- Uses segment flag constants such as `SEG_MIRROR`, `SEG_RAID0`, `SEG_RAID5_LS`, `SEG_RAID6_NC`.

Notable behavior:
- `raid01` handling is effectively disabled/commented out in the table, so raid01 conversions fall through to unsupported “other” behavior.
- Linear-to-striped is unsupported while linear-to-raid0 is supported, reflecting LVM’s explicit raid takeover model.

Risks:
- This file is macro-heavy and intentionally included into another source. Adding or reordering segment categories requires synchronized changes to `_segtype_index[]`, `_takeover_fns`, and the takeover function set.
