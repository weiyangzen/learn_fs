# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set.h

## Purpose
Provides generated-style conversion helpers between tracked VF adverse-event threshold KLV keys and driver enum indexes.

## Important APIs, Types, And Functions
Defines `MAKE_GUC_KLV_VF_CFG_THRESHOLD_KEY`, `MAKE_GUC_KLV_VF_CFG_THRESHOLD_LEN`, `xe_guc_klv_threshold_key_to_index`, and `xe_guc_klv_threshold_index_to_key`. Both conversion functions expand `MAKE_XE_GUC_KLV_THRESHOLDS_SET`.

## Control Flow
Key-to-index switches over ABI-derived threshold keys and returns `-1` for untracked keys. Index-to-key switches over generated enum values and returns zero for malformed indexes.

## State And Persistence
No runtime state is held; the source of truth is the threshold set macro in the companion types header.

## Dependencies And Integration Points
Depends on GuC KLV ABI definitions, generic KLV helper macros, and threshold index definitions. Used by code that stores threshold values by compact driver index while exchanging ABI keys with GuC.

## Risks And Test Signals
The generated conversions must stay in lockstep with the threshold set macro and firmware ABI. Tests should check every threshold key round-trips key to index to key and that unknown keys fail cleanly.
