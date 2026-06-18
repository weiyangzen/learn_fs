# Research: subset-b-008551

Grouped research for the Pebble LSM visualizer browser assets. Each section is wrapped for reconciliation into its source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/data/d3.v5.min.js -->
# sources/storage-engines/pebble/tool/data/d3.v5.min.js

## Purpose

This file is a vendored, minified browser build of D3 version 5.1.0. It provides the global `d3` namespace used by Pebble's `tool lsm` HTML visualizer when the generated page is not fully embedded. The file is third-party library code rather than project-authored logic.

The local SHA-256 is `e4f0898990c2ad72043660d51c4f857df0672d8e4ff27c20dc352cef733e3f27`, byte-for-byte identical to the other vendored Pebble docs copy at `sources/storage-engines/pebble/docs/js/d3.v5.min.js`.

## Important APIs, Types, and Functions

The bundle uses a UMD wrapper. In CommonJS it writes to `exports`; in AMD it defines an `exports` module; otherwise it attaches to `this.d3`.

Runtime inspection shows `d3.version` is `5.1.0` and the bundle exports 469 enumerable API names. The APIs directly needed by `sources/storage-engines/pebble/tool/data/lsm.js` are a much smaller subset:

- DOM selection and mutation: `select`, selection `append`, `attr`, `style`, `text`, `html`, `data`, `enter`, `exit`, `remove`, `selectAll`, `node`, `interrupt`.
- Scales: `scaleLinear`.
- Interaction: `drag`, mutable global `event`, `mouse`.
- Timers: `timer`.

The bundle also contains many unused D3 modules such as axes, brushes, color spaces, CSV/TSV parsing, force layouts, geo projections, hierarchy layouts, transitions, Voronoi, and zoom support. Those are available because this is the full D3 distribution build.

## Control Flow

The top-level control flow is immediate library initialization:

1. The UMD wrapper detects the host module system or browser global environment.
2. The factory function defines D3 internals and helper constructors.
3. Public exports are assigned onto the `d3` namespace.
4. Later scripts, especially `data/lsm.js`, synchronously call `d3` APIs.

There is no Pebble-specific entry point in this file. It only establishes library functions and runtime behavior for downstream scripts.

## State and Persistence Behavior

The D3 bundle does not persist Pebble data. It maintains transient browser/runtime state on DOM nodes for selections, event listeners, drag handlers, timers, transitions, and the v5 global `d3.event`. The LSM visualizer relies on `d3.event` in the checkbox, drag slider, and keyboard/mouse paths, and on D3 timer state for playback.

## Dependencies

The file is self-contained JavaScript. It expects browser-like DOM, SVG, event, timer, and pointer APIs. It has no project-local imports.

## Integration Points

`sources/storage-engines/pebble/tool/lsm.go` writes the generated visualizer HTML. If `l.embed` is false, it emits `<script src="data/d3.v5.min.js"></script>` before writing the inline `data = ...` object and then loading `<script src="data/lsm.js"></script>`. If `l.embed` is true, the generated page instead references `https://d3js.org/d3.v5.min.js` and embeds generated `lsmDataJS`.

The order matters: `lsm.js` evaluates immediately, calls `d3.select` while constructing the base DOM, and installs event handlers before `window.onload` initializes the visualizer state.

## Risks

- The file is minified and vendored, so manual edits are high-risk and hard to review. Updates should replace the bundle from a trusted D3 release.
- D3 v5.1.0 is old. Upgrading across major versions can break `d3.event`, `d3.mouse`, drag callback semantics, and global-script packaging used by `lsm.js`.
- The non-embedded LSM visualizer is script-order sensitive. If this file is missing or loaded after `lsm.js`, the visualizer fails during script evaluation.
- The embedded visualizer path does not use this local copy and instead depends on the network-hosted D3 URL, so offline and embedded modes can diverge if D3 is changed in one path but not the other.

## Test Signals

Useful verification signals are browser-level:

- `d3.version` should be `5.1.0`.
- The exported API should include `select`, `scaleLinear`, `drag`, `event`, `mouse`, and `timer`.
- A non-embedded `tool lsm` HTML output should load `data/d3.v5.min.js` before `data/lsm.js` and render the LSM levels without console errors.
- Slider dragging, checkbox toggling, hover overlap highlighting, index text input, keyboard stepping, and spacebar playback exercise the D3 APIs used by the visualizer.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/data/d3.v5.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/tool/data/lsm.js -->
# sources/storage-engines/pebble/tool/data/lsm.js

## Purpose

This browser-global script renders and controls Pebble's LSM manifest visualizer. It consumes a generated global `data` object from `tool/lsm.go`, constructs the page DOM with D3, displays SSTables across L0-L6, lets users step through manifest version edits, shows optional L0 sublevels, and highlights key-range overlaps on hover.

The same source is copied into generated Go by `sources/storage-engines/pebble/tool/make_lsm_data.sh` as `lsmDataJS` in `sources/storage-engines/pebble/tool/lsm_data.go`, so changes to this file require regenerating that Go asset.

## Important APIs, Types, and Functions

Global layout constants and state:

- `levelHeights`, `levelOffsets`, `lineStart`, `sublevelHeight`, and `levelWidth` define the vertical and horizontal geometry for the SVG.
- `vis` is the main `#vis` SVG selection.
- `reason` is the status text node showing the current edit or hovered file.
- `index` is the edit-index text input.
- `sliderX`, `offsetSliderX`, and `sliderHandle` hold the slider scale and handle state.
- `timer` holds the active D3 playback timer.

Helper functions:

- `renderHelp()` appends keyboard help text.
- `renderReason()` appends and returns the current status text.
- `humanize(s)` formats byte counts with IEC-style suffixes.
- `generateLevelOffsets()` derives level baselines from current heights.
- `styleWidth(e)` and `styleHeight(e)` parse pixel dimensions from D3 selections.
- `startPlayback(increment)` and `stopPlayback()` control timed forward stepping.

The central API is the mutable `version` object:

- `levels`: seven arrays of file numbers, one per LSM level.
- `sublevels`: arrays of L0 file numbers grouped by manifest-computed sublevel.
- `numSublevels`, `showSublevels`, `levelsInfo`, and `index` track display state.
- `init()` scans `data.Edits[*].Sublevels`, initializes sublevel containers, updates checkbox text, computes layout, and renders help.
- `setHeights()` adjusts L0 height when sublevels are visible and updates the SVG height.
- `onCheckboxChange(value)` toggles sublevel display, clears the SVG, rebuilds layout metadata, rerenders, and refreshes sizing.
- `set(index)` clamps and applies or unapplies version edits to reach a target edit index.
- `add(level, fileNums)` and `remove(level, fileNums)` mutate the per-level file arrays.
- `size(level, sublevel)`, `height(fileNum)`, `scale(level)`, `summarize(level, fileNums)`, and `describe(edit)` compute display metrics and text.
- `setLevelsInfo()` rebuilds display rows for levels or sublevels.
- `updateLevelsInfo()` refreshes row file arrays and sizes after a state change.
- `render(redraw)` draws labels, counts, sizes, level groups, clipping rectangles, overlap hit rectangles, SSTable rectangles, and slider/index state.
- `onMouseMove(i)` identifies the hovered SSTable, finds overlapping key ranges in other rows, updates overlap indicators, and writes the hover status text.
- `updateSize()` rebuilds the slider, ticks, SVG guide lines, clip paths, and cached level width after startup or resize.

The expected `data` shape is generated by Go:

- `data.Edits`: array of edits with `Reason`, optional `Added`, optional `Deleted`, and optional `Sublevels` maps.
- `data.Files`: map from file number to `Size`, `Smallest`, `Largest`, `SmallestSeqNum`, `LargestSeqNum`, and `Virtual`.
- `data.Keys`: array of key descriptors with `Pretty`, `SeqNum`, and `Kind`.
- `data.StartEdit`: manifest edit offset used for displaying external edit numbers.

## Control Flow

Script evaluation first creates the base DOM: `#container`, `#header`, the edit index input, the L0 sublevel checkbox, `#slider`, and `#vis`. It also installs the checkbox change handler.

At `window.onload`, the visualizer runs:

1. `version.init()` scans all edit sublevel maps, allocates `sublevels`, sets level heights and row metadata, and renders the help text.
2. `version.updateSize()` computes SVG/slider dimensions, creates the slider scale and drag behavior, renders tick labels, guide lines, and clip paths.
3. `version.set(0)` applies edits from initial index `-1` to edit `0`, rebuilds sublevels, sorts files, updates row metadata, and renders the first view.

When stepping forward, `version.set()` removes deleted files then adds added files for each edit crossed. When stepping backward, it removes files that were added by the current edit and re-adds files that were deleted by it. After every move it rebuilds L0 sublevels from the current L0 file set by scanning backward through `data.Edits` for each file's last known sublevel, sorts L0 by sequence numbers, sorts other levels by smallest key, updates display metadata, and renders.

User interactions are handled through global listeners:

- The slider drag in `updateSize()` maps drag x-coordinates through `sliderX.invert()` and calls `version.set()`.
- The index input subtracts `data.StartEdit` and calls `version.set()`.
- Left/right arrow keys stop playback and step by one or ten edits depending on `shiftKey`.
- Space toggles D3 timer playback.
- Resize calls `version.updateSize()` and rerenders.
- Mouse move over a level row calls `version.onMouseMove()`; mouse out restores the edit description and clears overlap indicators.

## State and Persistence Behavior

All state is in memory and DOM attributes. The script does not use local storage, cookies, network fetches, or filesystem persistence. The only durable input is the generated `data` object injected by `tool/lsm.go` before this script loads.

`version.levels` is the current materialized LSM state. It is incrementally updated by applying or reversing edit deltas, while `version.sublevels` is rebuilt from scratch after each movement because L0 sublevel assignment can change independently of add/delete membership. `levelsInfo` is derived render metadata used to bind rows to SVG elements.

The script mutates the DOM heavily through D3: labels, guide lines, slider contents, clipping definitions, transparent hit rectangles, overlap indicators, and SSTable rectangles are created, updated, and removed in response to state changes. Playback state is held in the global `timer`; stopping playback clears that timer.

## Dependencies

The script depends on:

- Global `d3` from D3 v5.1.0, either `data/d3.v5.min.js` in non-embedded output or the hosted D3 URL in embedded output.
- A global `data` object with the shape emitted by `sources/storage-engines/pebble/tool/lsm.go`.
- CSS from `sources/storage-engines/pebble/tool/data/lsm.css`, or the generated `lsmDataCSS` embed, for sizing `#slider`, `#vis`, `#container`, and text/slider styles.
- Browser DOM/SVG APIs and keyboard/mouse events.

## Integration Points

`sources/storage-engines/pebble/tool/lsm.go` writes the HTML shell, embeds or links CSS and JavaScript, serializes `l.state` into `data = ...`, then loads this script. The Go types `lsmTableMetadata`, `lsmVersionEdit`, `lsmKey`, and `lsmState` define the exact JSON contract consumed here.

`sources/storage-engines/pebble/tool/make_lsm_data.sh` concatenates this file into `lsm_data.go`, so the embedded output path depends on the generated Go copy matching the source asset. `sources/storage-engines/pebble/tool/lsm_test.go` has coverage for L0 edit construction order, which is indirectly important because this JavaScript assumes `Sublevels` values are valid and stable enough to reconstruct the visible L0 layout.

## Risks

- `version.set()` assumes every visible L0 file can resolve to a non-null sublevel by scanning backward through edits. If generated data omits a sublevel for an L0 file, `this.sublevels[sublevel].push(file)` can fail.
- `set(index)` clamps against `data.Edits.length - 1`; if `data.Edits` is empty, the computed index can become `-1` and downstream render code references `data.Edits[this.index]`.
- The script uses D3 v5 globals such as `d3.event` and `d3.mouse`; migrating to newer D3 versions requires event API changes.
- The L0 sort comparator returns `a < b` rather than a numeric `-1/0/1` fallback, which relies on JavaScript coercion and is less explicit than the other comparators.
- `render(redraw)` appends new clip groups, hit rectangles, indicators, and nested groups in some paths. The checkbox path clears the SVG first, but ordinary renders depend on D3 data joins being aligned with existing nodes; regressions can create duplicate DOM or stale clip paths.
- Hover overlap detection uses key-id ordering and treats `other.Smallest >= meta.Largest` as the break condition. Inclusive/exclusive sentinel semantics are already collapsed by Go into key ids, so any change in key encoding can affect visual overlap accuracy.
- Geometry depends on CSS pixel widths parsed from `.style("width")` and `.style("height")`; hidden containers or missing CSS can produce zero or invalid dimensions and break scaling.

## Test Signals

High-value checks are mostly integration/browser checks:

- Run or generate a `tool lsm` page and verify startup renders L0-L6 rows, counts, sizes, slider ticks, edit reason text, and the index input.
- Step forward and backward with arrow keys, shift-arrow jumps, slider dragging, and direct index input; verify counts and rectangles update consistently.
- Toggle "Show sublevels" and confirm L0 splits into `L0.*` rows, SVG height changes, and later stepping still works.
- Hover SSTables and verify the status text includes level, virtual marker when applicable, file number, size, key range, and adjacent-level overlap summary.
- Press space to start and stop playback; playback should stop automatically at the last edit.
- Resize the browser and verify slider ticks, clip paths, guide lines, and level widths recompute without console errors.
- Go-side tests such as `TestBuildEditsL0OutOfSeqNumOrder` are useful upstream signals because they protect the generated `Sublevels` contract this visualizer consumes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/tool/data/lsm.js -->
