<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.cpp

## Purpose
Implements aggregate Properties UI, including status and warning thresholds.

## Important APIs, Types, And Functions
`Aggregates_ShowProperties` opens/focuses the property sheet. `Aggregates_General_DlgProc` and helpers initialize, apply, toggle warning controls, and process `taskAGG_PROP_INIT`/`taskAGG_PROP_APPLY` completions.

## Control Flow
Existing property sheets are focused via `PropCache`; new sheets add Problems and General tabs. Init starts a background status task; apply packages warning-control state into `AGG_PROP_APPLY_PACKET` and starts an apply task. End-task handlers populate fields or show errors.

## State And Persistence
Dialog identity is stored in `DWLP_USER`; property cache prevents duplicates. Warning changes persist through background tasks/preferences.

## Dependencies And Integration Points
Uses property sheets/cache, task framework, alert/problem tabs, aggregate/server prefs, spinner/progress controls, and resource formatting.

## Risks And Edge Cases
Warning semantics use zero/off, -1/default, or custom percent. Failed init leaves unknown values. Task packet/control ID coupling is strong.

## Test Signals
Open/focus/jump, init success/failure, usage formatting, warning default/custom/off, apply success/failure, and cache cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.cpp -->
