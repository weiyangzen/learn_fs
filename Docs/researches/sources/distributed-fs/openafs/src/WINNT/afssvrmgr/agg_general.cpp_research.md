<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.cpp

## Purpose
Provides aggregate preference load/save and focused/selected aggregate helpers.

## Important APIs, Types, And Functions
`Aggregates_LoadPreferences`, `Aggregates_SavePreferences`, `Aggregates_GetFocused`, and `Aggregates_GetSelected`.

## Control Flow
Load allocates an `AGGREGATE_PREF`, restores persisted bytes or applies defaults, then initializes alert runtime state. Save writes the attached user param. Selection helpers read FastList data from `IDC_AGG_LIST`.

## State And Persistence
Preferences persist via `RestorePreferences`/`StorePreferences`; alert counters/timers are reset at load.

## Dependencies And Integration Points
Uses aggregate prefs, alert defaults, and FastList selection APIs; dispatch attaches these prefs on aggregate creation.

## Risks And Edge Cases
Allocation failure is not guarded. Raw struct persistence is sensitive to layout/version changes.

## Test Signals
Preference default/restore/save and list focus/selection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_general.cpp -->
