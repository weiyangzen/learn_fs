# subset-b-007763 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-win.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-win.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.c -->
# sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.c

## Purpose

`afsmonitor.c` is the main implementation of the OpenAFS `afsmonitor` performance monitoring tool. It parses command-line and optional config-file inputs, builds file-server and cache-manager monitor lists, configures xstat probe collections, receives asynchronous xstat callback results, converts raw probe structures into display-ready strings, checks thresholds, optionally writes raw output, and drives the GTX UI refresh functions implemented in `afsmon-win.c`.

## Important APIs, types, and functions

The file owns most shared globals used by the monitor: debug/output flags, probe frequency, host lists, xstat collection counts, circular result buffers, current and previous display buffers, alert counts, and display maps. Local list types include `afsmon_fs_Results_list`, `afsmon_fs_Results_CBuffer`, `afsmon_cm_Results_list`, and `afsmon_cm_Results_CBuffer`. Public structs used across files come from `afsmonitor.h`, especially `afsmon_hostEntry`, `Threshold`, `fs_Display_Data`, and `cm_Display_Data`.

Key routines include `afsmonInit`, the command syntax handler; `process_config_file`, which performs a two-pass parse of config files; `parse_hostEntry`, `parse_threshEntry`, `parse_showEntry`, and `store_threshold`, which build monitor configuration; `afsmon_execute`, which resolves hosts, sets ports, chooses xstat collection IDs, initializes xstat FS/CM probes, and starts GTX input; `afsmon_FS_Handler` and `afsmon_CM_Handler`, xstat callbacks; `save_*_results_inCB`, optional circular-buffer persistence; `save_*_data_forDisplay`, completed-cycle display snapshot logic; `fs_Results_ltoa`, `fs_FullPerfs_ltoa`, `fs_CallBackStats_ltoa`, and `cm_Results_ltoa`, which flatten xstat structures into strings; `check_*_thresholds` and `execute_thresh_handler`; and `afsmon_Exit`, the central cleanup/exit path.

## Control flow

`main` defines the `initcmd` syntax and dispatches through the OpenAFS `cmd` package. `afsmonInit` opens debugging and output files, validates frequency and option combinations, accepts host lists directly or processes a config file, initializes default or requested display maps, sets a SIGINT handler, allocates optional circular buffers and mandatory display buffers, initializes GTX, and then calls `afsmon_execute`.

Config-file parsing is deliberately two-pass. The first pass validates syntax, resolves and records host names, counts global and per-host thresholds, and processes `show` directives into display maps. After global threshold counts are added to each host's allocation count, the second pass allocates threshold arrays and stores threshold metadata with positional indexes into FS/CM display arrays. Global thresholds are applied to all known hosts, while local thresholds apply to the last host of the correct type.

`afsmon_execute` resolves all FS and CM host names to sockets and initializes xstat. FS collection IDs are chosen based on requested display fields: full performance stats, callback stats, or both. CM always requests full performance stats. After `xstat_fs_Init` and/or `xstat_cm_Init`, the GTX input server runs. xstat invokes `afsmon_FS_Handler` and `afsmon_CM_Handler` as probe results arrive.

Each handler optionally writes output, detects a new probe cycle by comparing probe numbers, advances circular-buffer indexes when needed, stores raw-ish copied probe results if circular buffers are enabled, and passes the current result to the display path. The display path finds the matching host slot, marks failed probes, converts successful probe data to strings, checks thresholds, and increments a static received-result count. Once all hosts and collections for the cycle have arrived, it verifies probe sequence continuity, copies `curr_*Data` to `prev_*Data`, clears current values while preserving threshold flags, recomputes alert totals, marks data available, and calls `ovw_refresh` plus the relevant detail-frame refresh.

## State and persistence behavior

Most state is in process globals and is reset at startup. The optional `-buffers` setting creates an in-memory circular history of copied xstat probe results, one linked-list row per host per buffer slot and per collection. This history is not persisted to disk and is freed in `afsmon_Exit`. Persistent filesystem effects are limited to the optional debug file and optional output file written via `afsmon_fsOutput`/`afsmon_cmOutput`. Threshold handlers can fork and exec external programs, passing host, host type, threshold name, threshold value, actual value, and handler-specified arguments.

## Dependencies and integration points

The file depends on OpenAFS command parsing (`afs/cmd.h`), GTX UI APIs through the exported functions in `afsmonitor.h`, xstat FS/CM client APIs and global `xstat_*_Results` objects, label/category arrays from other afsmonitor compilation units, host resolution through libc, and OpenAFS utility macros such as `opr_min`. It integrates with `afsmon-output.c` for optional output, `afsmon-win.c` for UI refresh/initialization, and xstat server/cache-manager collection contracts for raw data layout.

## Risks and edge cases

The implementation uses many fixed-size buffers and unbounded `sscanf`, `sprintf`, and some `strncpy` patterns. Long config tokens, host names, output names, handler strings, or label values are important risk areas. Threshold handler parsing is whitespace-only and stores at most 20 arguments in fixed 256-byte slots. A forked handler path calls `afsmon_Exit`, which performs broad cleanup before `execvp`; this is intentional but complex. Raw xstat conversion relies on fixed result-length constants and layout assumptions; comments note that those constants must be changed if xstat structures change. `fs_FullPerfs_ltoa` has special handling for 64-bit `struct timeval`, while CM conversion casts the full result buffer directly to `struct afs_stats_CMFullPerf` without an explicit decoder. Allocation failure handling in circular-buffer creation frees only allocations from the current partial item and relies on later `afsmon_Exit` for already-linked objects. `init_print_buffers` appears to initialize `tmp_fsData2` from `curr_fsData` instead of `prev_fsData`, and similarly for CM, which can leave `prev_*Data` host names empty until the first completed copy.

## Test signals

High-value tests include config parsing with global thresholds, per-host thresholds, duplicated threshold names, invalid section/group/variable names, command-line host lists, and mutually exclusive option combinations. xstat integration tests should cover successful and failed probes, missed probe numbers, FS full-perf-only, FS callback-only, both FS collections, and CM full-perf collection. UI smoke tests should confirm `prev_*Data` is populated before first refresh, threshold transitions trigger handlers only on crossing transitions, alert counts match failed probes plus overflows, and output/debug files are written when requested. Memory-checking runs should exercise `-buffers` with multiple slots and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/Makefile.in -->
# sources/distributed-fs/openafs/src/aklog/Makefile.in

## Purpose

`Makefile.in` defines the automake/autoconf-era build rules for OpenAFS `aklog`-related command-line tools. It builds `aklog`, `asetkey`, `klog`, and `akeyconvert`, sets Kerberos compiler/linker flags, links against OpenAFS internal libraries, and installs client and server administration binaries into the correct bindirs.

## Important variables and targets

The file includes generated configuration fragments from `src/config/Makefile.config` and `src/config/Makefile.pthread`. `MODULE_CFLAGS` adds Kerberos CPP flags and `-DALLOW_REGISTER`; `MODULE_LDFLAGS` adds Kerberos linker flags. `AKLIBS` combines generic libs, Kerberos ldflags/libs, and configured `@AKLOG_KRB5_LIBS@`. `AFSLIBS` collects ptserver, rxkad, cmd, opr, and util libtool archives. `KCLIBS` collects auth, cmd, and opr libraries for `akeyconvert`. `LT_libs` carries hcrypto and roken dependencies.

`SRCS`/`OBJS` describe the common `aklog` object set. The `all` target builds `aklog`, `asetkey`, `klog`, and `akeyconvert`. Each program target invokes `$(LT_LDRULE_static)`, so these tools are linked through the repository's libtool static-linking convention. `install` installs `aklog` and `klog.krb5` to `${bindir}` and `asetkey` plus `akeyconvert` to `${afssrvbindir}`. `dest` mirrors that behavior into OpenAFS staging paths. `clean` removes libtool output, objects, and built binaries.

## Control flow and integration

This file is consumed by the OpenAFS configure/build system. Substitution variables such as `@srcdir@`, `@TOP_OBJDIR@`, `@KRB5_CPPFLAGS@`, and `@AKLOG_KRB5_LIBS@` are filled during configuration. Build order is target-driven: object compilation rules come from included config makefiles, while this file specifies final link lines and install locations.

## State and persistence behavior

The makefile creates transient object files and binaries in the build tree and installs selected binaries into destination prefixes. It has no runtime state. `clean` is intentionally local to this directory and removes the known products.

## Dependencies

The rules depend on Kerberos 5, hcrypto, roken, pthread settings, OpenAFS internal libraries, and libtool helper macros. `akeyconvert` links against auth/cmd/opr rather than the broader ptserver/rxkad/util set used by `aklog`, `asetkey`, and `klog`.

## Risks and test signals

The `all` target builds `akeyconvert`, but `install` and `dest` list only `aklog asetkey klog` as prerequisites while still installing `akeyconvert`. A parallel or direct `make install` from a clean tree could attempt to install `akeyconvert` without first building it unless make reaches it through another dependency. Link-order regressions are another risk because Kerberos and OpenAFS static libraries can be order-sensitive. Test signals include clean `make all`, clean `make install DESTDIR=...`, clean `make dest DEST=...`, and configure variants with different Kerberos/com_err providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/add_etbl.c -->
# sources/distributed-fs/openafs/src/aklog/add_etbl.c

## Purpose

`add_etbl.c` is a small compatibility shim for platforms whose com_err implementation does not provide `add_to_error_table`. It adapts the older or alternate `add_error_table` API to the `add_to_error_table(struct et_list *)` interface expected by the surrounding aklog/Kerberos error-table code.

## Important APIs and control flow

The entire implementation is conditional on `#ifndef HAVE_ADD_TO_ERROR_TABLE`. When the platform already provides `add_to_error_table`, this translation unit effectively contributes no symbols. Otherwise it includes OpenAFS standard definitions, com_err declarations, and `afs/error_table.h`. If `HAVE_ADD_ERROR_TABLE` is also missing, it forward-declares `void add_error_table(const struct error_table *);`.

The implemented `add_to_error_table` accepts `struct et_list *new_table` and calls `add_error_table((struct error_table *) new_table->table)`. There is no validation, allocation, or error handling.

## State and persistence behavior

The function mutates whatever global error-table registry is managed by the linked com_err implementation through `add_error_table`. It has no file or durable state and no local static state.

## Dependencies and integration points

This file depends on configure-time feature detection for `HAVE_ADD_TO_ERROR_TABLE` and `HAVE_ADD_ERROR_TABLE`, the shape of `struct et_list`, and compatibility between `new_table->table` and `struct error_table`. It exists to keep aklog-related code building across com_err variants from Kerberos or system libraries.

## Risks and test signals

The cast from `new_table->table` to `struct error_table *` assumes ABI compatibility. If the com_err headers change the table representation, this shim could compile but register invalid data. The function also assumes `new_table` and `new_table->table` are non-null. Test signals are mostly build-matrix based: configure/build on platforms with native `add_to_error_table`, with only `add_error_table`, and with the shim declaration path. Runtime tests should trigger an aklog error path that requires registered error tables and confirm readable com_err messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/add_etbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/akeyconvert.c -->
# sources/distributed-fs/openafs/src/aklog/akeyconvert.c

## Purpose

`akeyconvert.c` implements the `akeyconvert` administrative migration tool for OpenAFS upgrades using the rxkad-k5 extension. It reads keys from the server `rxkad.keytab`, detects key identifier conflicts that cannot be represented in `KeyFileExt`, and writes compatible non-DES keys into `KeyFileExt`. By default it writes only the newest kvno for each principal; the `-all` flag writes older keys as well.

## Important APIs, types, and functions

The file uses Kerberos keytab APIs, OpenAFS server configuration APIs, typed-key APIs, and the OpenAFS `cmd` parser. Portability macros abstract Kerberos keytab entry fields: `deref_entry_keylen`, `deref_entry_keyval`, and `deref_entry_enctype` handle `key` versus `keyblock` layouts. Compatibility macros also normalize `krb5_free_keytab_entry_contents` and `krb5_free_unparsed_name`.

`ktent_to_typedKey` converts a `krb5_keytab_entry` to `struct afsconf_typedKey`. DES enctypes 1, 2, and 3 map to `afsconf_rxkad` with subtype zero; other enctypes map to `afsconf_rxkad_krb5` with the Kerberos enctype. `princ_sort`, `kvno_sort`, `etype_sort`, `ke_sort`, and `full_sort` define ordering. `slurp_keytab` reads the whole keytab into memory. `check_dups` rejects duplicate kvno/enctype pairs. `convert_kt` writes selected entries into `KeyFileExt` with `afsconf_AddTypedKey`. `free_ents` releases keytab-entry contents and the entry array. `CommandProc` is the command handler, and `main` registers the optional `-all` flag.

## Control flow

`main` creates a command syntax with the description "Convert cell keys for the 1.6->1.8 OpenAFS upgrade", adds `-all`, dispatches, and returns boolean failure. `CommandProc` initializes a Kerberos context, opens the server configuration directory `AFSDIR_SERVER_ETC_DIR`, builds the keytab path from `dir->name` and `AFSDIR_RXKAD_KEYTAB_FILE`, and calls `slurp_keytab`.

`slurp_keytab` resolves the keytab, performs a first sequential scan to count entries, allocates an array, then performs a second scan to copy entries into that array. If the keytab changes between passes and more entries are seen than allocated, it warns and stops early. After reading, `CommandProc` sorts by kvno/enctype using `ke_sort` and calls `check_dups` so duplicates across principals are fatal before any writes. It then sorts by principal, descending kvno, and descending enctype using `full_sort`.

`convert_kt` walks the fully sorted array. For each principal, it tracks the first kvno as the newest because the sort places higher kvnos first. Without `-all`, entries for older kvnos of the same principal are skipped. Each remaining key is converted to an OpenAFS typed key. Single-DES rxkad keys are explicitly not added to `KeyFileExt`; the tool prints a warning and continues. Duplicate existing KeyFileExt entries (`AFSCONF_KEYINUSE`) also produce a warning and continue. Other conversion or write errors abort the command.

## State and persistence behavior

The only intended persistent mutation is adding typed keys to the server configuration directory's `KeyFileExt` through `afsconf_AddTypedKey`. Input state is the existing `rxkad.keytab` under the same server config directory. The program keeps all keytab entries in memory until conversion completes, then frees entries, path strings, Kerberos context, and the AFS config directory handle. It prints diagnostics to stderr and a final count to stdout.

## Dependencies and integration points

This file depends on Kerberos keytab/principal APIs, com_err headers selected by configure checks, OpenAFS `afsconf` directory and typed-key APIs, server path constants from `afs/dirpath.h`, key constants from `afs/keys.h`, and `roken` for portability functions such as `asprintf`. It integrates with the `aklog` build through `Makefile.in`, which links it with auth, cmd, opr, Kerberos, hcrypto, roken, and pthread-related libraries.

## Risks and edge cases

`princ_sort` initializes and frees a Kerberos context on every comparison, which can be expensive for large keytabs and uses `opr_Verify` assertions for operations that can theoretically fail. The qsort comparators depend on Kerberos principal unparsing for deterministic ordering when principals differ. `check_dups` only checks adjacent entries after sorting by kvno/enctype; that is correct for duplicates but should be covered by tests. The first pass in `slurp_keytab` counts entries, and a concurrent keytab shrink/growth can make `*nents` differ from the number actually filled; the code warns only when more entries appear than allocated. `convert_kt` parses a well-known anonymous principal as the initial sentinel and frees it at exit; if `krb5_parse_name` fails before initialization, cleanup must still tolerate that path. Error reporting after `convert_kt` says "errno" even though many returned codes are OpenAFS/Kerberos codes rather than `errno`.

## Test signals

Useful tests include keytabs with one principal and multiple kvnos, multiple principals with overlapping kvno/enctype pairs, duplicate kvno/enctype pairs across principals, DES-only keys, mixed DES and rxkad-k5 keys, existing KeyFileExt entries, empty keytabs, unreadable keytabs, and `-all` versus default selection. Build tests should cover Kerberos implementations exposing `key` versus `keyblock` keytab entry fields and different com_err include paths. Runtime tests should verify that duplicate identifiers cause no writes, existing keys are skipped without aborting, and successful writes can be read back from `KeyFileExt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/aklog/akeyconvert.c -->
