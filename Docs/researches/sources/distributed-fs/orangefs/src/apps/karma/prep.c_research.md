# sources/distributed-fs/orangefs/src/apps/karma/prep.c

## Purpose
`prep.c` converts raw OrangeFS management data into graph-ready structures for Karma's Status and Traffic pages. It chooses units, scales values, computes footer summaries, selects bar colors, and smooths unit changes for traffic labels.

## Important APIs, Types, and Functions
`gui_status_data_prepare()` accepts an array of `PVFS_mgmt_server_stat` and returns a static array of six `gui_status_graph_data` entries corresponding to `GUI_STATUS_*` graph IDs. It allocates/reallocates per-graph arrays when server count changes, computes space, uptime, handle, memory, and placeholder data/CPU graph values, and fills titles/footers/colors.

`gui_traffic_data_prepare()` accepts per-server raw byte/op counters and elapsed times, computes read/write bandwidth and metadata operation rates, stores per-server floats into `gui_traffic_graph_data`, chooses labels through `gui_units_size()` and `gui_units_ops()`, and uses static historical maxima to reduce rapid unit/divisor changes.

## Control Flow
The status preparation flow is a sequence of graph-specific transformations. For each metric, it finds the max value to pick units, fills arrays for all servers, and writes title/footer metadata. Traffic preparation does two passes: one for I/O bandwidth and one for metadata operation rates, each followed by unit scaling.

## State and Persistence
No disk persistence exists. Static `graph_data` and `graph_data_ct` persist allocated status graph buffers across timer ticks. Traffic unit smoothing uses static `hist_max_io` and `hist_max_meta`, so prior traffic influences later labels until process exit.

## Dependencies and Integration Points
The file depends on `PVFS_mgmt_server_stat`, graph DTOs from `karma.h`, bar color constants, and unit helpers from `units.c`. It is called by `karma.c` timers before rendering in `status.c` and `traffic.c`.

## Risks and Edge Cases
Allocation return values are not checked. `gui_status_data_prepare()` asserts `svr_stat_ct > 0`; a zero-server filesystem aborts in assert builds and may misbehave otherwise. Some divisions compute `second / (first + second)` without guarding against zero totals. Total free handles are formatted through an `int` cast, which can truncate large counts. Traffic rates use integer arithmetic before conversion to float, losing precision and risking overflow in `raw bytes * 1000`. If `time_ms` is zero, existing graph fields for that server may retain stale values because they are not explicitly cleared in every branch.

## Test Signals
Feed synthetic stats with zero totals, low free space/handles, very large counts, memory disabled, and zero servers. Traffic tests should include zero elapsed time, very high byte counters, decreasing rates to observe smoothing, and server-count changes. Render tests should verify titles, units, colors, and footers match expected thresholds.
