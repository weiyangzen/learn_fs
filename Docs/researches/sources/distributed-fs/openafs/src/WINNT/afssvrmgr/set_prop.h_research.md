# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_prop.h

Purpose: Declares the fileset property dialog entry point and the apply packet used when changing fileset warning preferences.

Important APIs/types: `SET_PROP_APPLY_PARAMS` carries `LPIDENT lpi`, whether fileset-full warnings are enabled, whether to use the server default threshold, and the custom warning percentage. `Filesets_ShowProperties(LPIDENT, size_t, BOOL)` opens the fileset property sheet and optionally starts on the threshold-related tab.

Control flow/state: The header is consumed by UI code and task code. The packet is allocated by the dialog and passed to `taskSET_PROP_APPLY`.

Dependencies/integration: Requires `LPIDENT`, `BOOL`, and `WORD` types from the broader server manager headers. Integrated with property sheets, alert counts, and task application logic.

Risks/test signals: Verify that task handlers and UI code agree on boolean semantics: warnings disabled, server default (`perWarnSetFull == -1` in loaded prefs), and custom percentage.
