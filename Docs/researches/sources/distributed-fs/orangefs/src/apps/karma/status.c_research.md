# sources/distributed-fs/orangefs/src/apps/karma/status.c

## Purpose
`status.c` implements Karma's Status notebook page. It displays six small horizontal bar graphs for space, uptime, handles, data handles placeholder, memory, and CPU placeholder, and supports double-clicking a server bar to open a details popup.

## Important APIs, Types, and Functions
The public functions are `gui_status_setup()` and `gui_status_graph_update()`. Static `gui_status_graphs[6]` stores per-graph widgets, labels, drawing resources, titles/footers, and copied data arrays. `gui_status_graph_setup()` creates one framed graph widget, labels, drawing area, footer, and event callbacks. `gui_status_graph_update()` resizes graph data arrays, copies prepared values, stores title/footer, and calls `gui_status_graph_draw_stacked()`.

`gui_status_graph_draw_stacked()` draws horizontal single or stacked bars into a backing `GdkPixmap`, updates tic labels and footer, and forces redraw. Configure/expose callbacks allocate/repaint backing pixmaps. `gui_status_graph_button_press_callback()` maps double-click y coordinates to a bar index, retrieves current stats, and calls `gui_status_server_popup()`, which reuses details table helpers for a one-server dialog.

## Control Flow
`karma.c` creates all six graph frames during startup. Every status timer tick pushes prepared data into each graph. Drawing is pixmap-backed: configure creates resources and redraws any existing data; expose copies from pixmap to window; update redraws the pixmap and schedules drawing.

## State and Persistence
All state is in GTK widgets/GDK resources and static graph arrays. Graph data is copied from `prep.c`, so status rendering is insulated from later changes until the next update. No persistent storage is used.

## Dependencies and Integration Points
The file depends on GTK2/GDK drawing APIs, `gui_get_new_fg_color_gc()` from `color.c`, `gui_comm_stats_retrieve()` from `comm.c`, and `gui_details_view_new()`/`gui_details_view_fill()` from `details.c`. It consumes `gui_status_graph_data` prepared by `prep.c`.

## Risks and Edge Cases
`gui_status_graph_update()` calls `memcpy()` with `count` bytes even when `count == 0` and arrays may be NULL; many C libraries tolerate zero-length copies, but this is still fragile. `strncpy()` of title/footer does not guarantee NUL termination. Drawing asserts `barheight > 0`, so too many servers for the fixed graph height can abort. The no-data draw path returns before clearing footer labels or forcing redraw. Configure callback redraws with `footer` as NULL, losing stored footer after resize. `gui_status_graph_button_press_callback()` divides by `g_state->nr_bars` without first handling zero bars.

## Test Signals
Render status graphs with zero, one, six, and many servers; resize the window repeatedly; double-click valid bars, spaces between bars, and empty graphs. Verify stacked bars and colors for prepared thresholds. Leak testing should cover configure-event GC/pixmap replacement and popup creation/destruction.
