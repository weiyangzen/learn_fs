<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis-bw-2d.c -->
# sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis-bw-2d.c

## Purpose
SDL/SDL_ttf graphical visualization that displays per-I/O-server OrangeFS read/write bandwidth bars and recent peaks.

## Important APIs, Types, And Functions
`options` stores mount point, window width, and update interval. `main` parses options, starts the shared visualization poller with `pvfs2_vis_start`, and calls `draw`. `draw` initializes SDL/TTF, opens `VeraBd.ttf`, allocates bar state and bandwidth matrices, waits on `pint_vis_cond`, computes MB/s from `pint_vis_shared` samples, and renders axes, labels, read/write bars, and peaks. `check_for_exit`, `parse_args`, and `usage` handle events and options.

## Control Flow
The UI blocks on a condition variable signaled by the background poller in `pvfs2-vis.c`. On each update it calculates bandwidth between adjacent samples or sample end time, adjusts global `max_bw`, redraws labels/borders/bars, and flips the SDL surface. Quit events, Escape, or `q` exit.

## State And Persistence
Runtime UI state includes SDL surfaces, font, allocated matrices, bar rectangles, and shared performance buffers protected by `pint_vis_mutex`. It writes no persistent data.

## Dependencies And Integration Points
Depends on SDL, SDL_ttf, pthreads, `pvfs2-vis.h`, and OrangeFS management performance samples. It is a frontend over `pvfs2_vis_start`.

## Risks And Test Signals
Risks include hard-coded font path, division by zero if timestamps do not advance, unbounded `max_bw` growth that never decays, memory leaks on repeated errors, and condition waits without a predicate loop. Test signals are successful window creation, updates for multiple server counts, quit handling, missing font behavior, and visual sanity with read/write traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis-bw-2d.c -->
