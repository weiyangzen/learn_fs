# Research: subset-b-008522

Grouped research for the Pebble docs benchmark visualization files. Each section is wrapped for reconciliation into its source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/docs/js/d3.v5.min.js -->
# sources/storage-engines/pebble/docs/js/d3.v5.min.js

## Purpose

This file is a vendored, minified browser build of D3 version 5.1.0. It provides the `d3` global consumed by the Pebble benchmark documentation UI, including the chart rendering, scales, axes, formatting, parsing, CSV parsing, pointer, and zoom behavior used by `app.js` and `write-throughput.js`.

The file is a third-party library artifact rather than project-authored business logic. It is loaded directly by `index.html` and `local-test.html` before the Pebble-specific scripts.

## Important APIs, Types, and Functions

The bundle uses a UMD wrapper. In CommonJS it writes to `exports`; in AMD it defines an `exports` module; otherwise it attaches to `this.d3`.

Runtime inspection shows `d3.version` is `5.1.0` and the bundle exports 469 enumerable API names. Important APIs used by this docs application include:

- DOM selection and mutation: `select`, `selectAll`, selection `append`, `attr`, `style`, `text`, `call`, `data`, `enter`, `each`, `classed`.
- Data helpers: `max`, `bisector`, `format`, `csvParseRows`.
- Time helpers: `timeParse`, `timeFormat`, `timeDay`, `scaleTime`.
- Linear/category chart helpers: `scaleLinear`, `scaleOrdinal`, `schemeCategory10`, `axisBottom`, `axisLeft`, `line`.
- Interaction helpers: `zoom`, `zoomTransform`, `mouse`, mutable global `event`.

The bundle also contains many unused D3 modules such as brushes, colors, force simulation, geo projections, hierarchy, transitions, requests, and Voronoi helpers. Those exports are not directly consumed by the researched local files but are part of the full vendored D3 distribution.

## Control Flow

The top-level control flow is immediate library initialization:

1. The UMD wrapper detects CommonJS, AMD, or browser-global execution.
2. The factory function defines the minified D3 internals and helper constructors.
3. It assigns public exports to the `d3` namespace.
4. Browser scripts that load after it use that global synchronously.

There is no application entry point in this file. Behavior is invoked by downstream code. For example, `write-throughput.js` calls `d3.select`, builds scales and axes, parses CSV detail payloads with `d3.csvParseRows`, and wires zoom/mouse callbacks through D3's event system.

## State and Persistence Behavior

The library itself does not persist application data to storage. It does maintain runtime state on DOM nodes for interactive behavior, notably fields such as `__zoom` for zoom transforms and transition-related internal properties. `write-throughput.js` depends on this behavior when it reads and writes zoom state on `.chart` SVG nodes and calls `d3.zoomTransform(svg.node())`.

D3's mutable `d3.event` global is important in this version. `write-throughput.js` reads `d3.event.transform` and `d3.event.sourceEvent` inside the zoom callback. This is a D3 v5 style integration point and would need migration work for newer D3 versions where event handling changed.

## Dependencies

The bundle is self-contained JavaScript. It expects browser-like DOM APIs for selection, SVG manipulation, events, timers, and pointer coordinates. It has no project-local source dependency and no module import statements.

It is loaded by:

- `sources/storage-engines/pebble/docs/index.html`
- `sources/storage-engines/pebble/docs/local-test.html`

It is required by:

- `sources/storage-engines/pebble/docs/js/app.js`
- `sources/storage-engines/pebble/docs/js/write-throughput.js`

## Integration Points

The docs pages load this file first, before the remote or local benchmark data fixture and before the app scripts. That order is necessary because `app.js` initializes date parsers and chart helpers using D3 at script-evaluation time, and `write-throughput.js` references D3 when rendering charts.

The researched write-throughput chart uses D3 for all rendering and interaction:

- Selects `.chart.write-throughput` and `.chart.write-throughput-detail`.
- Builds time and linear scales.
- Draws axes and SVG paths.
- Parses detail `rawData` CSV rows into numeric series.
- Handles mouse position and zoom events.

## Risks

- The file is minified and vendored, so project-level changes should not be made manually inside this artifact. Updating should replace the whole bundle from a trusted D3 release.
- D3 v5.1.0 is old. Upgrading across major versions could break `d3.event`, `d3.mouse`, zoom behavior, selection semantics, or module packaging.
- Because the bundle is loaded as a browser global, script ordering is fragile. If this script fails or moves after `app.js`, the docs UI fails immediately.
- The file is large and hard to review for supply-chain or local patch drift. The observed SHA-256 is `e4f0898990c2ad72043660d51c4f857df0672d8e4ff27c20dc352cef733e3f27`.

## Test Signals

Useful verification signals are browser-level rather than unit-level:

- `d3.version` should equal `5.1.0`.
- The exported API should include the functions used by the Pebble docs app: `select`, `scaleTime`, `scaleLinear`, `axisBottom`, `axisLeft`, `line`, `bisector`, `timeParse`, `timeFormat`, `timeDay`, `zoom`, `zoomTransform`, `mouse`, `csvParseRows`, `max`, and `format`.
- `index.html` and `local-test.html` should render YCSB charts and write-throughput charts without console errors.
- Zooming, mouse hover, and click-to-detail interactions are high-value regression tests because they cover D3's event, pointer, scale, and DOM mutation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/docs/js/d3.v5.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/docs/js/write-throughput.js -->
# sources/storage-engines/pebble/docs/js/write-throughput.js

## Purpose

This browser-global script renders the Pebble write-throughput benchmark charts in the docs UI. It fetches a summary JSON file, renders a time-series chart for the `write/values=1024` workload, supports hover/zoom/click interactions, fetches per-run detail JSON for the selected date, parses worker-level CSV data, and renders the detail chart.

The file is part of a non-module script stack. It defines globals used by `app.js`, and it also depends on globals supplied by `app.js`, which is called out by a TODO in `app.js` as an awkward script-loading relationship.

## Important APIs, Types, and Functions

- `writeThroughputWorkload`: global constant with value `write/values=1024`. `app.js` uses it to pick the default workload for initial detail rendering.
- `isLocalMode()`: reads `window.location.search` through `URLSearchParams` and returns true only when `local=true`.
- `writeThroughputSummaryURL()`: returns `testdata/write-throughput/summary.json` in local mode, otherwise `https://pebble-benchmarks.s3.amazonaws.com/write-throughput/summary.json`.
- `writeThroughputDetailURL(filename)`: returns a local or S3 detail URL under the same `write-throughput` prefix.
- `bisectAndRenderWriteThroughputDetail(data, detailDate)`: uses a D3 bisector on parsed dates to select a summary datapoint, fetches its detail data, then renders the detail chart. Fetch failures render the detail chart with `null` data.
- `renderWriteThroughputSummary(allData)`: renders the summary time series, axes, clip path, hover labels, marker, synchronized zoom callback, synchronized mouse callback, and click handler.
- `fetchWriteThroughputSummaryData(file)`: fetches a detail JSON file and converts each run's `rawData` CSV string into numeric row objects `{ elapsed, opsSec, passed, size, levels }`.
- `renderWriteThroughputSummaryDetail(workload, date, opsSec, rawData)`: clears and redraws the detail chart for worker-level ops/sec over elapsed time, with a dashed average line at the calculated `opsSec`.

The expected summary data shape is an object keyed by workload name, with arrays of objects containing `name`, `date`, `opsSec`, optional `sha`, `writeAmp`, and `summaryPath`. The expected detail data shape is an object keyed by worker/run id, where each value contains `rawData` CSV rows before parsing and `data` row objects after parsing.

## Control Flow

The main flow is orchestrated by `app.js`, not by this file directly:

1. `app.js` calls `initData()`, which fetches `writeThroughputSummaryURL()` and merges each returned workload into the global `data` object.
2. `app.js` calls `renderWriteThroughputSummary(data)` after initializing date range, annotations, and query params.
3. `renderWriteThroughputSummary` selects `.chart.write-throughput`, picks `allData["write/values=1024"]`, computes dimensions from `styleWidth` and `styleHeight`, creates time/linear scales, renders axes and a single SVG line, then attaches hover and zoom state to the SVG DOM node.
4. The summary chart installs a transparent mouse rectangle. Mouse movement updates all charts with an `updateMouse` method, mouse over/out toggles hover opacity, and click floors the x-coordinate date to a day and calls `bisectAndRenderWriteThroughputDetail`.
5. On initialization, `app.js` also calls `bisectAndRenderWriteThroughputDetail(data[writeThroughputWorkload], max.date)` so the detail chart is populated for the latest selected date.
6. The detail fetch path calls `fetchWriteThroughputSummaryData(summaryPath)` and then `renderWriteThroughputSummaryDetail`. If the fetch rejects, the detail chart receives `rawData = null` and displays "Data unavailable".

The zoom callback updates the summary chart locally for programmatic zoom events, and broadcasts user-originated zoom transforms to every `.chart` node with an `updateZoom` method. It then normalizes each chart node's `__zoom` transform by forcing the y translation to zero.

## State and Persistence Behavior

This script does not use persistent browser storage. Runtime state lives in:

- DOM nodes and SVG children appended under `.chart.write-throughput` and `.chart.write-throughput-detail`.
- `svg.node().updateMouse` and `svg.node().updateZoom` callback properties.
- D3 zoom state on SVG nodes, including `__zoom`.
- Hover SVG elements whose opacity and text are updated on mouse events.

The detail chart is explicitly cleared with `svg.selectAll("*").remove()` before each render to avoid accumulating old runs. The summary chart is not cleared by this function, so repeated calls to `renderWriteThroughputSummary` would append duplicate axes, paths, clip paths, mouse rectangles, and handlers.

The local/remote mode is derived from the current URL query string on each URL helper call. No query state is mutated by this file.

## Dependencies

Direct browser/runtime dependencies:

- Global `d3` from `d3.v5.min.js`.
- Browser `fetch`.
- Browser `URLSearchParams`.
- DOM/SVG APIs through D3 selections.
- `window.location.search`.

Project-global dependencies supplied by `app.js`:

- `parseTime`
- `formatTime`
- `styleWidth`
- `styleHeight`
- `minDate`
- `max.date`

Data dependencies:

- Remote summary and detail JSON under `https://pebble-benchmarks.s3.amazonaws.com/write-throughput/`.
- Local summary fixture at `testdata/write-throughput/summary.json` when `?local=true`.
- Local detail fixture files matching each `summaryPath`, if present, for click-through detail testing.

## Integration Points

The HTML pages include two relevant SVGs:

- `.chart.write-throughput`
- `.chart.write-throughput-detail`

`index.html` loads D3, remote `data.js`, `write-throughput.js`, and then `app.js`. `local-test.html` loads D3, local `testdata/data.js`, `write-throughput.js`, and then `app.js`.

`app.js` consumes this file by calling `writeThroughputSummaryURL`, `renderWriteThroughputSummary`, `bisectAndRenderWriteThroughputDetail`, and reading `writeThroughputWorkload`. In the other direction, this file calls helpers that are defined later by `app.js`. That works because those helper-dependent functions are not invoked until `window.onload`, after all scripts have been evaluated.

## Risks

- `bisectAndRenderWriteThroughputDetail` does not guard against the bisector returning `data.length`; unlike the hover code, it immediately reads `data[i]`. A click or initial date beyond the last datapoint may throw when accessing `workload.date`.
- `renderWriteThroughputSummaryDetail` iterates `for (let key in rawData)` before checking `rawData == null`. The intended "Data unavailable" branch is unreachable for `null` and will throw before rendering the fallback.
- `const noData = mousex < x(parseTime(data[0].date));` is computed but unused, and the hover logic still indexes `data[i - 1]` when the mouse is before the first datapoint. With `i === 0`, this can read `data[-1]` and throw.
- `renderWriteThroughputSummary` hardcodes `dataKey = "write/values=1024"` even though the SVG has `data-key` and the file defines `writeThroughputWorkload`. This limits reuse and can drift from markup/configuration.
- The clip path id is set to `write/values=1024`, which contains slash and equals characters. It works in many SVG URL contexts but is brittle for CSS selectors and duplicate chart instances.
- The script relies on D3 v5 globals such as `d3.event` and `d3.mouse`, which are migration hazards for newer D3.
- There is no explicit handling for missing workload keys, empty data arrays, malformed dates, non-OK fetch responses, or malformed detail `rawData`.

## Test Signals

High-value test cases:

- Load `local-test.html?local=true` and confirm the summary fetch uses `testdata/write-throughput/summary.json`.
- Load the normal page and confirm the summary fetch uses the S3 URL.
- Render the summary chart from a fixture with 10 ordered datapoints and verify an SVG path, x/y axes, hover marker, and mouse interaction rectangle are created.
- Hover before the first point, between points, and after the last point to exercise bisector boundary behavior.
- Click on a valid date and confirm `fetchWriteThroughputSummaryData` parses detail `rawData` into numeric `{ elapsed, opsSec, passed, size, levels }` rows.
- Simulate detail fetch failure and verify whether the fallback "Data unavailable" path works; current code appears to throw before reaching the null check.
- Zoom the summary chart and verify x-axis/path updates and that other chart nodes with `updateZoom` receive synchronized transforms.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/docs/js/write-throughput.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/docs/testdata/data.js -->
# sources/storage-engines/pebble/docs/testdata/data.js

## Purpose

This local fixture defines a global `data` object for `local-test.html`. It mirrors the remote Pebble benchmark `data.js` shape with synthetic YCSB benchmark series so the docs UI can be exercised without loading the S3-hosted fixture.

Each property is a workload key and each value is a newline-delimited CSV string. `app.js` parses these strings into arrays of benchmark datapoints during `initData()`.

## Important Data Shape

The file assigns `data = { ... }` without `var`, `let`, or `const`, intentionally creating or replacing a browser-global `data` binding for the legacy script stack.

It contains 12 workload keys:

- `ycsb/A/values=1024`
- `ycsb/A/values=64`
- `ycsb/B/values=1024`
- `ycsb/B/values=64`
- `ycsb/C/values=1024`
- `ycsb/C/values=64`
- `ycsb/D/values=1024`
- `ycsb/D/values=64`
- `ycsb/E/values=1024`
- `ycsb/E/values=64`
- `ycsb/F/values=1024`
- `ycsb/F/values=64`

Each workload has 10 CSV rows spanning dates from January 25, 2026 through February 3, 2026. Rows use the schema consumed by `app.js`:

1. Date string, either `YYYYMMDD` or `YYYYMMDD-sha`.
2. `opsSec`.
3. `readBytes`.
4. `writeBytes`.
5. `readAmp`.
6. `writeAmp`.

The fixture intentionally includes both date-only rows and date-with-SHA rows. That exercises `parseDateStr`, which strips the SHA suffix for date parsing and stores the suffix separately.

## Control Flow

There are no functions. The file executes a single top-level assignment when loaded by the browser. The later `app.js` initialization flow reads the global `data`, parses each CSV string with `d3.csvParseRows`, computes global and per-chart maxima, then fetches write-throughput summary data and merges it into the same `data` object.

`local-test.html` loads this file before `write-throughput.js` and `app.js`, so by the time `window.onload` runs, the YCSB fixture is available.

## State and Persistence Behavior

The file seeds mutable in-memory global state only. It does not persist data to storage or make network requests. `app.js` mutates the global `data` object by replacing each CSV string with parsed arrays and adding write-throughput arrays fetched from local or remote summary JSON.

Because the assignment is unqualified, any previous global `data` value is overwritten when this script loads.

## Dependencies

This fixture has no code dependencies. It depends structurally on `app.js` expecting a global object of CSV strings. It is integrated through `local-test.html`, not through an import system.

The data is coupled to:

- `app.js` CSV parsing and date parsing.
- `app.js` chart rendering for YCSB workloads.
- `write-throughput.js` indirectly, because `app.js` merges write-throughput summary data into this same object before calling the write-throughput renderer.

## Integration Points

`local-test.html` loads:

1. `js/d3.v5.min.js`
2. `testdata/data.js`
3. `js/write-throughput.js`
4. `js/app.js`

That means this fixture is the local replacement for the remote `https://pebble-benchmarks.s3.amazonaws.com/data.js` script used by `index.html`.

The workload keys are expected by the YCSB chart sections in the docs UI. The write-throughput chart does not consume these YCSB keys directly, but shares the global `data` object after `initData()` merges write-throughput summary rows.

## Risks

- The global assignment lacks a declaration and will fail under strict mode or module loading. This is acceptable for the current legacy script style but fragile for modernization.
- Because values are raw CSV strings, schema changes in `app.js` can silently misparse fixtures if the column order is changed.
- The fixture contains synthetic-looking future dates and mixed SHA formats. That is useful for parser coverage but may not reflect production freshness semantics.
- Missing or malformed rows in a single workload could break chart rendering because parsing and max computation assume numeric columns.
- The local fixture does not include write-throughput summary data; that lives in `testdata/write-throughput/summary.json` and is fetched separately.

## Test Signals

Useful checks:

- Evaluate the script and confirm `Object.keys(data).length === 12`.
- Confirm every workload has 10 newline-delimited rows and every row has six comma-separated fields.
- Confirm rows with and without SHA suffixes both parse through `parseDateStr`.
- Load `local-test.html` and verify YCSB charts render without using the remote S3 `data.js`.
- Verify that after `app.js` initialization, each workload value has been converted from a CSV string into parsed row objects with numeric metric fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/docs/testdata/data.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/docs/testdata/write-throughput/summary.json -->
# sources/storage-engines/pebble/docs/testdata/write-throughput/summary.json

## Purpose

This JSON fixture supplies local write-throughput summary data for the Pebble docs UI. It is used when `writeThroughputSummaryURL()` sees `?local=true`, allowing `local-test.html` or the normal docs page in local mode to render the write-throughput summary chart without fetching the S3 summary.

## Important Data Shape

The top-level object has one workload key:

- `write/values=1024`

The value is an array of 10 summary datapoints. Each object contains:

- `name`: workload name, always `write/values=1024` in this fixture.
- `date`: benchmark date, usually `YYYYMMDD-sha`; one row uses date only (`20260129`).
- `opsSec`: calculated max sustainable write throughput.
- `writeAmp`: write amplification metric for the run.
- `summaryPath`: detail JSON filename for per-worker time-series data.

The fixture spans January 25, 2026 through February 3, 2026. `opsSec` ranges from 58,825 to 68,000 in the provided rows. `summaryPath` values follow the pattern `YYYYMMDD-pebble-write-size=1024-run_1-summary.json`.

## Control Flow

This file is data-only. It is fetched by `writeThroughputSummaryURL()` through the `initData()` flow in `app.js`:

1. `app.js` calls `fetch(writeThroughputSummaryURL())`.
2. The response JSON is parsed.
3. For each workload key, `app.js` maps each datapoint to a new object that preserves the original fields, rewrites `date` to the date-only prefix, and stores the parsed SHA suffix in `sha`.
4. The resulting array is assigned into the global `data` object under `write/values=1024`.
5. `renderWriteThroughputSummary(data)` reads this array and draws the summary chart.
6. Clicks or initial detail rendering use `summaryPath` to fetch a corresponding detail file through `writeThroughputDetailURL()`.

## State and Persistence Behavior

The fixture is static JSON and has no internal state. Once fetched, its values become mutable in-memory objects owned by `app.js` and `write-throughput.js`.

No persistence occurs. The `summaryPath` fields are references to additional detail fixtures or remote detail files; this file does not embed the worker-level `rawData` used by the detail chart.

## Dependencies

The file depends on the schema expected by `app.js` and `write-throughput.js`. The chart code expects:

- A top-level key matching `writeThroughputWorkload` / `write/values=1024`.
- A non-empty, date-sorted array.
- Valid `date` strings parseable by `parseDateStr`.
- Numeric `opsSec`.
- Valid `summaryPath` values for detail fetches.

It is selected by `writeThroughputSummaryURL()` when local mode is enabled.

## Integration Points

Local mode URL resolution points to `testdata/write-throughput/summary.json`. The HTML pages provide the SVG containers, `app.js` performs the fetch/merge, and `write-throughput.js` renders the resulting series.

Each `summaryPath` integrates with `fetchWriteThroughputSummaryData`, which expects the corresponding detail JSON file to be located under `testdata/write-throughput/` in local mode or the S3 `write-throughput/` prefix in remote mode.

## Risks

- The chart assumes sorted data for bisector behavior. If rows are reordered, hover and click selection can become incorrect.
- One fixture row lacks a SHA suffix. That is useful for parser coverage, but any UI logic assuming `sha` exists must handle null.
- Missing local detail files for `summaryPath` entries cause the detail fetch to reject. The intended fallback currently has a bug in `renderWriteThroughputSummaryDetail` because it iterates `rawData` before checking for null.
- The summary contains `writeAmp`, but `renderWriteThroughputSummary` only plots `opsSec`; if future charting expects write amplification, code changes are needed.
- Date values are future-dated relative to many real benchmark histories; freshness indicators in `app.js` will reflect the fixture dates rather than current production data.

## Test Signals

Useful validation:

- JSON parses successfully and has exactly one top-level key, `write/values=1024`.
- The array has 10 entries sorted by date from `20260125` to `20260203`.
- Every entry has `name`, `date`, numeric `opsSec`, numeric `writeAmp`, and `summaryPath`.
- At least one date with SHA and one date without SHA parse through `parseDateStr`.
- In local mode, `app.js` merges this array into global `data` and `renderWriteThroughputSummary` draws the summary line.
- Clicking a datapoint should attempt to fetch the matching `summaryPath` under `testdata/write-throughput/`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/docs/testdata/write-throughput/summary.json -->
