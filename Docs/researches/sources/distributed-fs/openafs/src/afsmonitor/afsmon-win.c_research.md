# sources/distributed-fs/openafs/src/afsmonitor/afsmon-win.c

## Purpose

`afsmon-win.c` implements the interactive terminal user interface for the OpenAFS `afsmonitor` tool. It uses the OpenAFS GTX window/object/frame/keymap stack to present three screens: a system overview, a file-server detail table, and a cache-manager detail table. It does not collect xstat data itself. Instead, it consumes global state prepared by `afsmonitor.c`: host counts, current and previous probe numbers, display maps, alert counts, and display-ready `prev_fsData`/`prev_cmData` arrays.

## Important APIs, types, and functions

The file exports `gtx_initialize`, `ovw_refresh`, `fs_refresh`, and `cm_refresh` via `afsmonitor.h`. `gtx_initialize` creates the global GTX window, creates three frames, populates each frame with light-object onodes, installs key bindings, and leaves the overview frame active. `ovw_refresh` updates overview labels, probe counters, command availability, and the host summary columns. `fs_refresh` and `cm_refresh` render paged, horizontally scrollable detail tables for selected file-server and cache-manager statistics.

Important helper routines include `initLightObject`, which wraps `gator_objects_create` for one-line light objects; `justify_light`, which truncates and pads text for fixed-width GTX labels; `resolve_CmdLine`, which computes page/navigation capability bits and prompt text; `display_Server_datum`, which splits long datum strings across two stacked objects and highlights threshold crossings; and `display_Server_label`, which splits slash-separated labels across three header rows.

The many `Switch_*` functions are GTX key callbacks. They switch frames or call the relevant refresh routine with an updated page or column offset. The command bits are `CMD_NEXT`, `CMD_PREV`, `CMD_LEFT`, `CMD_RIGHT`, `CMD_FS`, and `CMD_CM`.

## Control flow

Initialization starts in `gtx_initialize`. It calls `gtx_Init`, creates the overview frame, binds it to `afsmon_win`, then calls `create_ovwFrame_objects`, `create_FSframe_objects`, and `create_CMframe_objects`. The overview object creation also determines terminal dimensions, checks the minimum size, computes overview page count, creates host-name object slots, and binds keys such as `f`, `c`, `n`, `N`, `p`, `P`, `Q`, and control-C. The detail frame creation routines compute host rows and data columns from `maxY`, `maxX`, `FC_HOSTNAME_O_WIDTH`, and `FC_COLUMN_WIDTH`, allocate onode-pointer grids, create host/data/label light objects, compute page counts, and bind navigation keys.

Runtime refresh is driven by `afsmonitor.c` after xstat probe cycles complete, and by key callbacks after the user navigates. `ovw_refresh` refuses to render FS or CM data until the corresponding `*_Data_Available` flag is set. It updates fixed labels and then walks the appropriate slice of `prev_fsData` or `prev_cmData` for the requested page. Failed probes render as `[ PF] host`, threshold overflows render as `[count] host`, and clean hosts render without highlight.

`fs_refresh` and `cm_refresh` have parallel logic. They validate page and column bounds, update fixed labels and prompts, fill the three-row statistic labels from `fs_labels`/`cm_labels` through `fs_Display_map`/`cm_Display_map`, then fill each host row from `prev_fsData` or `prev_cmData`. Host names are shortened at the first dot. Each statistic is displayed in two vertically stacked cells, with threshold overflow highlighting coming from `threshOvf`.

## State and persistence behavior

The UI state is entirely process-local and global: frame pointers, object arrays, dimensions, current pages, current left/right columns, availability flags, and page-type command masks. There is no durable persistence. The file mutates labels in GTX objects and relies on `WOP_DISPLAY` to redraw when the active frame matches the refreshed frame. On fatal UI inconsistencies, it writes into `errMsg`/`errMsg1` and exits through `afsmon_Exit`, which lives in `afsmonitor.c`.

## Dependencies and integration points

This file depends on OpenAFS GTX headers and runtime (`gtxwindows`, `gtxobjects`, `gtxlightobj`, `gtxcurseswin`, `gtxdumbwin`, `gtxX11win`, `gtxframe`, `gtxkeymap`), xstat headers for result sizing/type context, `afsmonitor.h` for shared structs/constants, and `afsmon-labels.h` for display labels. Its strongest integration point is the shared global state from `afsmonitor.c`; the UI assumes `prev_fsData` and `prev_cmData` are complete snapshots of the last finished probe cycle.

## Risks and edge cases

The UI relies heavily on fixed-size buffers and `sprintf` into stack arrays such as `printBuf[256]` and object labels. Most user-controlled strings arrive through host names, labels, or config-derived values, so long names and terminal geometry remain important test vectors. `justify_light` caps destination width to `GATOR_LABEL_CHARS`, but many callers build intermediate strings before justification. The detail refreshers allow `a_LcolNum == *_numCols`; that may render an empty page of columns rather than a useful view. `cm_refresh` sets `cm_cmd_o` when updating the CM probe-number label, which looks like a copy-paste bug because it formats `cm_probeNum_o` but calls `gator_light_set(cm_cmd_o, 1)`. Object grids allocated here are not explicitly freed in this file; cleanup is mostly process exit.

## Test signals

Useful tests include starting `afsmonitor` with narrow terminals below and above `80x12`, confirming all frame creation paths and error messages; monitoring only FS, only CM, and both, to validate command prompts and frame availability bits; using enough hosts and selected statistic columns to force vertical paging and horizontal scrolling; injecting failed probes and threshold overflows to verify highlights and alert counts; and running under ASAN or valgrind around frame creation and shutdown to detect allocation leaks or label overflows. Manual curses/GTX smoke tests are especially important because the code is display-state heavy.
