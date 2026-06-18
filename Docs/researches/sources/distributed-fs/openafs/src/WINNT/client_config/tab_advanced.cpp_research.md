# sources/distributed-fs/openafs/src/WINNT/client_config/tab_advanced.cpp

## Purpose
`tab_advanced.cpp` implements the Advanced property-sheet tab for cache size/path, chunk size, stat entries, and access to advanced subdialogs for misc, binding, logon, automap, and diagnostics.

## Important APIs, Types, and Functions
Exports are `AdvancedTab_DlgProc` and `AdvancedTab_CommitChanges`. Internal routines include `AdvancedTab_OnInitDialog`, `AdvancedTab_OnApply`, `AdvancedTab_OnRefresh`, and a local `log2`. It calls many `Config_*` getters/setters and subdialog apply functions.

## Control Flow
Initialization reads cache/path/chunk/stat settings, creates spinners, sets cache path text, and refreshes cache-in-use display. Commands open subdialogs or handle spinner power-of-two adjustment for chunk size. Apply persists changed top-level values, then calls `Misc_OnApply`, `Binding_OnApply`, `Logon_OnApply`, and `Diag_OnApply`.

## State and Persistence Behavior
The tab stores current values in `g.Configuration`; setters write registry values and usually mark `g.fNeedRestart`. Cache-in-use is live service state read by pioctl and displayed as informational text.

## Dependencies and Integration Points
It integrates with `config.cpp`, `pagesize.h`, and all advanced subdialogs. The General tab calls `AdvancedTab_CommitChanges` before service start/restart decisions.

## Risks and Edge Cases
Subdialog state is applied only when the Advanced tab applies, so users can OK a subdialog and then cancel the main sheet without persistence. The top-level sysname control is initialized but not applied here, likely legacy or mismatched resource usage. Chunk size normalization assumes powers of two and may behave unexpectedly for zero.

## Test Signals
Tests should cover spinner bounds, chunk power-of-two normalization, cache-in-use display with stopped service, subdialog staged apply behavior, and restart prompting after cache/chunk/stat/path changes.
