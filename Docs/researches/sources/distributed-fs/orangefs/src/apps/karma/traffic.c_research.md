# sources/distributed-fs/orangefs/src/apps/karma/traffic.c

## Purpose
`traffic.c` implements Karma's Traffic notebook page. It draws a vertical multi-bar graph per server showing I/O read/write bandwidth and metadata read/write operation rates with separate left/right axes.

## Important APIs, Types, and Functions
The public functions are `gui_traffic_setup()` and `gui_traffic_graph_update()`. Static `gui_traffic_graph` stores axis labels, main labels, drawing area, backing pixmap, color GCs, per-server arrays (`read`, `write`, `rmeta`, `wmeta`), server count, and historical max values. `gui_traffic_setup()` builds the widget layout with left I/O tic labels, central drawing area, right metadata tic labels, and bottom labels. `gui_traffic_graph_update()` allocates/resizes data arrays, copies prepared traffic values, updates labels, and draws if configured. `gui_traffic_graph_draw()` scales axes, smooths maxima, updates tic labels, and draws four bars per server.

## Control Flow
The page is constructed once. Drawing waits until the drawing area receives a configure event and allocates pixmap/GC resources. Timer updates from `karma.c` store data and trigger drawing when configured. Expose events copy the pixmap to the visible window.

## State and Persistence
Graph data and axis history are process-local static state. There is no persistence. Axis smoothing means previous traffic levels influence current scale even after rates drop; server count changes reset `io_max` and `meta_max`.

## Dependencies and Integration Points
The file depends on GTK2/GDK, color GC creation from `color.c`, and prepared traffic data from `prep.c`. It is fed by the one-second traffic timer in `karma.c`, which obtains raw data from `comm.c`.

## Risks and Edge Cases
Allocation failures are unchecked. In `gui_traffic_graph_draw()`, the temporary `tmp` value is not reset before the metadata-axis branch when the current max exceeds historical max, so metadata scaling can reuse stale I/O state. `barwidth > 0` is asserted; many servers or very small drawing widths can abort. If `svr_ct` becomes zero, old arrays are not freed and labels may remain stale. Repeated configure events allocate colors through `color.c`, which leaks `GdkColor` allocations. There is no clipping check for bars if values exceed the smoothed axis.

## Test Signals
Feed traffic data for zero, one, many, and very many servers; resize the drawing area down to small widths; alternate high and low rates to verify axis smoothing; and compare left/right tic labels to expected maxima. Leak tests should resize repeatedly. Visual tests should confirm bar color order: orange read, blue write, green metadata read, purple metadata modify.
