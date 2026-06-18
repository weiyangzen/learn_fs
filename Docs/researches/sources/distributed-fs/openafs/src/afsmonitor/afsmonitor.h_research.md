# sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.h

## Purpose

`afsmonitor.h` is the shared interface for the `afsmonitor` program. It defines host-name and result-size constants, threshold and display data structures, UI update constants, display category counts, and cross-file function prototypes used by `afsmonitor.c`, `afsmon-win.c`, and `afsmon-output.c`.

## Important APIs, types, and constants

`HOST_NAME_LEN` fixes monitored FS/CM names at 80 bytes. `XSTAT_FS_FULLPERF_RESULTS_LEN`, `XSTAT_FS_CBSTATS_RESULTS_LEN`, and `XSTAT_CM_FULLPERF_RESULTS_LEN` encode expected xstat result payload lengths before any xstat calls have returned. The header comments explicitly warn that these constants must track xstat structure layout changes.

`struct Threshold` stores one threshold definition: variable name, positional display index, string threshold value, and optional handler command. `struct afsmon_hostEntry` is a linked-list node for monitored hosts and owns the per-host threshold array.

`struct fs_Display_Data` and `struct cm_Display_Data` are display snapshots. Each stores a host name, a `probeOK` flag where zero means failed, a two-dimensional array of fixed-width string values, a parallel threshold-overflow flag array, and an overflow count.

Display sizing and indexing constants include `NUM_FS_FULLPERF_ENTRIES`, `NUM_FS_CB_ENTRIES`, `NUM_FS_STAT_ENTRIES`, `FS_STAT_STRING_LEN`, `NUM_CM_STAT_ENTRIES`, `CM_STAT_STRING_LEN`, and collection range markers such as `FS_FULLPERF_ENTRY_START` and `FS_CB_ENTRY_START`. UI update constants `OVW_UPDATE_FS`, `OVW_UPDATE_CM`, and `OVW_UPDATE_BOTH` control which overview columns refresh after independent probe cycles.

The prototypes expose file output functions, UI refresh/initialization functions, and `afsmon_Exit`.

## Control flow and integration

The header is not executable, but it is the contract that lets the xstat/control file and GTX UI file share data layouts without duplicating definitions. `afsmonitor.c` allocates and fills `fs_Display_Data` and `cm_Display_Data`; `afsmon-win.c` reads those arrays to render overview and detail frames. The output module receives filenames and detail flags through the declared `afsmon_*Output` APIs. `afsmon_Exit` is declared `AFS_NORETURN`, making it suitable as the shared fatal-exit path from both the core and UI files.

## State and persistence behavior

The header defines in-memory structures only. Persistence is indirect: display data is copied from probe results and may later be written by output functions, but the structures themselves are process-local. Threshold handler strings can lead to external process execution when thresholds are crossed.

## Dependencies

The header assumes OpenAFS integer and noreturn definitions are already available through included configuration headers in the C files. It depends on xstat result length contracts from the OpenAFS FS/CM statistics structures and on label/category arrays in other afsmonitor files matching the entry counts declared here.

## Risks and test signals

The biggest risk is drift between these constants and the actual xstat payload structures or label arrays. If `NUM_*` counts are wrong, conversion loops and UI maps can write past fixed arrays or silently omit fields. Tests should compile afsmonitor with current xstat headers, assert that label arrays and display counts match these constants, exercise both FS collection ranges, and verify that long host names and threshold names are truncated or rejected consistently.
