# sources/distributed-fs/openafs/src/scout/scout.c

## Purpose
`scout.c` implements the OpenAFS `scout` monitoring command, a terminal GTX/curses dashboard that periodically probes one or more file servers and displays current connections, fetch/store counters, workstation counts, and per-partition free-space lights. It is a standalone user-facing monitoring program layered over `fsprobe`.

## Important APIs, types, and functions
The display model is built from `struct mini_screen`, `struct mini_line`, and `struct scout_disk`. A `mini_line` owns GTX light objects for connection/fetch/store/workstation/server-name columns plus a fixed `VOLMAXPARTS` disk pool split into used and free linked lists. Important functions are `main`, `scoutInit`, `execute_scout`, `FS_Handler`, `init_mini_line`, `mini_initLightObject`, `mini_justify`, `mini_PrintDiskStats`, `scout_FindUsedDisk`, `scout_RecomputeLightLocs`, `scout_SetNonDiskLightLine`, `scout_SetColumnWidths`, and `scout_AdoptThresholds`.

## Control flow
`main` defines the `cmd` syntax and dispatches to `scoutInit`. `scoutInit` parses servers, basename, probe frequency, hostname display, attention thresholds, debug file, and column widths, then calls `execute_scout`. `execute_scout` initializes soft signals and GTX, resolves server names into port-7000 socket entries, creates banner and per-server light objects, initializes `fsprobe_Init` with `FS_Handler`, starts the GTX input server, and then waits forever in `fsprobe_Wait`. Each probe callback recomputes window width, walks `fsprobe_Results` for each server, updates labels and highlight state, calls `mini_PrintDiskStats`, and redraws the frame.

## State and persistence behavior
State is process-local global UI and threshold state: `scout_screen`, `scout_frame`, `scout_frameDims`, column widths, debug flags, and attention thresholds. Persistent external effects are limited to opening a requested debug log and network probing of file servers. The disk list is maintained in memory across probe cycles so newly seen `/vicep*` partitions get light objects and existing lights can be reused.

## Dependencies and integration points
The file integrates OpenAFS GTX window/object/frame packages, `cmd` command parsing, `fsprobe` file-server statistics, `hostutil_GetHostByName`, and platform signal behavior. It relies on `ProbeViceStatistics` layout, `ViceDisk` names such as `/vicepa`, GTX light object private data, and curses-style window operations.

## Risks
The code is old C with many fixed-size buffers and `sprintf`/`strcpy` style operations; server names, banners, and threshold strings need bounded inputs. `scout_RemoveInactiveDisk` is effectively a stub, so inactive disk records are detected but not fully removed from display/list state. Width calculations can produce zero disk lights per line on very narrow terminals, risking poor layout behavior. Threshold parsing uses `atoi` without validation, and `%` disk threshold parsing mutates the command item string. Many globals make the command non-reentrant and difficult to unit test.

## Test signals
Useful tests include command parsing for required `-server`, basename expansion, debug-file failure, malformed threshold pairs, disk percent versus min-free modes, custom column widths including too many widths, resize handling in `FS_Handler`, probe failure blanking, first-seen and repeated disk partition updates, and integration runs against reachable and unreachable file servers.
