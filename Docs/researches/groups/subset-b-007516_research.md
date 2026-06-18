# subset-b-007516 Research

Grouped research for the listed Hadoop HDFS static web UI files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/d3-v4.1.1.min.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/d3-v4.1.1.min.js

## Purpose
Vendored minified D3 bundle used by the HDFS NameNode web UI for client-side visualization. Although the filename says `d3-v4.1.1`, the file banner and runtime `d3.version` report `4.1.0`. In this tree it is loaded by `hdfs/dfshealth.html` before `dfshealth.js` and supplies the histogram primitives for the DataNode disk-usage chart.

## Important APIs, Types, And Functions
The UMD wrapper exports a global `d3` object in the browser and also supports AMD/CommonJS. Runtime inspection shows 382 exported symbols. The locally exercised surface in `hdfs/dfshealth.js` is small: `d3.format(",.0f")`, `d3.scaleLinear()`, `d3.histogram()`, `d3.max()`, `d3.select()`, and `d3.axisBottom()`. The bundle also includes common D3 v4 modules for arrays/statistics, collections, requests, timers, selections, transitions, axes, scales, shapes, hierarchy, force layout, drag/zoom/brush, color/interpolation, CSV/TSV parsing, and geo projections.

## Control Flow
The file executes immediately when the script tag loads, defines D3 functions in closure scope, and assigns exports to `window.d3`. Later, `dfshealth.js` calls `renderHistogram(data)` after the NameNode JMX response is normalized. That function maps each live DataNode to `(usedSpace / capacity) * 100`, builds a linear x scale over `[0, 100]`, bins values with `d3.histogram().thresholds(x.ticks(20))`, scales counts with another linear scale, appends an SVG under `#datanode-usage-histogram`, draws bars and text labels, and adds a bottom axis.

## State And Persistence
D3 itself keeps no application persistence here. It mutates the DOM by appending SVG nodes and uses transient internal state inside scale, histogram, selection, and axis objects. The surrounding HDFS page stores the normalized live node array in `window.liveNodes`; that state is consumed by `histogram-hostip.js` rather than by D3.

## Dependencies And Integration Points
The bundle has no runtime dependency on jQuery or Hadoop code, but its output depends on an available browser DOM/SVG environment. It integrates with `hdfs/dfshealth.html`, `hdfs/dfshealth.js`, and `histogram-hostip.js`: D3 draws histogram bars, and those bars receive inline `onclick` attributes that call the host/IP list helper with each bin's `x0` and `x1`.

## Risks
The version mismatch between filename and banner can confuse vulnerability or compatibility audits. The library is old and minified, so local patch review is difficult and upstream fixes are not obvious from source diffs. The chart assumes positive DataNode capacity; zero or missing capacity can produce `Infinity`/`NaN` values that D3 may bin or render poorly. The histogram width is computed once from `div.container`, so it does not automatically reflow after resize.

## Test Signals
Useful smoke tests are page-level: load `hdfs/dfshealth.html` with a representative NameNode JMX response, confirm `window.d3.version === "4.1.0"`, verify `#datanode-usage-histogram svg` is created, confirm there are 20 bin groups for the configured ticks, and click a bar to confirm `open_hostip_list(x0, x1)` receives the expected bin bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/d3-v4.1.1.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dataTables.bootstrap.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dataTables.bootstrap.js

## Purpose
Bootstrap 3 integration adapter for jQuery DataTables. It changes DataTables defaults and renderer hooks so HDFS tables use Bootstrap row/column layout, form-control styling, and Bootstrap pagination markup.

## Important APIs, Types, And Functions
The file defines a `factory($, DataTable)` inside a UMD-style wrapper. It extends `DataTable.defaults` with a Bootstrap-oriented `dom` layout and `renderer: "bootstrap"`. It extends `DataTable.ext.classes` with `dataTables_wrapper form-inline dt-bootstrap`, `form-control input-sm` filter inputs, and matching length selects. Its key function is `DataTable.ext.renderer.pageButton.bootstrap(settings, host, idx, buttons, page, pages)`, which constructs `<ul class="pagination">` and `<li><a>` page controls for `first`, `previous`, numbered pages, `ellipsis`, `next`, and `last`.

## Control Flow
On load, the wrapper selects AMD, CommonJS, or browser global initialization. In the HDFS UI it takes the browser path and calls `factory(jQuery, jQuery.fn.dataTable)`. During table draws, DataTables calls the registered Bootstrap page-button renderer. The renderer recursively walks the provided `buttons` array, computes display text and disabled/active classes from current page state, binds click actions through `settings.oApi._fnBindAction`, and calls `api.page(action).draw(false)` for enabled controls.

## State And Persistence
The adapter mutates global DataTables defaults, extension class names, and renderer registry for the lifetime of the page. It does not persist data itself. It briefly captures `document.activeElement`'s `data-dt-idx` before recreating pagination markup and restores focus after rendering when possible, which matters for keyboard navigation.

## Dependencies And Integration Points
Requires jQuery, DataTables 1.10 or newer, and Bootstrap 3 CSS. HDFS pages load it after `/static/jquery.dataTables.min.js` and Bootstrap JS/CSS in `hdfs/dfshealth.html` and `hdfs/explorer.html`. It affects tables initialized in `hdfs/dfshealth.js` such as `#table-datanodes`, `#table-snapshots`, nested snapshot tables, and in `hdfs/explorer.js` for file listings. If `DataTable.TableTools` exists, it also remaps legacy TableTools button and collection classes to Bootstrap-compatible markup.

## Risks
Because it mutates global DataTables defaults, every table on the page inherits Bootstrap rendering whether or not the table initialization mentions it. The renderer builds HTML with `.html(btnDisplay)` for pagination labels; labels normally come from trusted DataTables language settings but should not be populated from untrusted input. The focus restore branch depends on `data-dt-idx` and may not restore index `0` because the code checks `if (activeEl)`. Compatibility should be checked if `jquery.dataTables.min.js` is upgraded beyond the adapter's era.

## Test Signals
Smoke-test by loading `dfshealth.html` and `explorer.html`, initializing tables, and confirming wrappers have `dt-bootstrap`, filter and length controls have Bootstrap `form-control input-sm`, pagination is an unordered list with `pagination`, and disabled/active states update as pages change. TableTools paths are only relevant if that optional plugin is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dataTables.bootstrap.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dfs-dust.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dfs-dust.js

## Purpose
Hadoop-specific Dust.js extension layer for HDFS web pages. It adds formatting filters used by inline Dust templates and exposes a shared `load_json` helper for fetching multiple JMX endpoints before rendering.

## Important APIs, Types, And Functions
The IIFE receives `jQuery`, `dust`, and `window`. It defines filters and merges them into `dust.filters` with `$.extend`. Filters are `fmt_bytes`, `fmt_percentage`, `fmt_time`, `date_tostring`, `format_compile_info`, `helper_to_permission`, `helper_to_directory`, `helper_to_acl_bit`, `fmt_number`, and `fmt_human_number`. The exported API is `window.load_json(beans, success_cb, error_cb)`, where `beans` entries are objects with `url` and `name`.

## Control Flow
Filter functions are invoked by Dust templates during render, for example `{Total|fmt_bytes}` or `{PercentUsed|fmt_percentage}`. `load_json` starts one `$.get` per bean. Each successful response is stored as `data[b.name]`; a countdown is decremented; when all outstanding requests complete, `success_cb(data)` runs. On the first failed request, an `error` flag is set and `error_cb(url, jqxhr, text, err)` runs. The `$.each` callback stops launching later requests if the error flag is already set, though requests already started can still finish.

## State And Persistence
No persistent storage is used. Filter registration mutates the global `dust.filters` object for the current page. `load_json` maintains per-call in-memory `data`, `error`, and `to_be_completed` variables. Numeric and date formatting is stateless apart from relying on the global `moment` object for date conversion.

## Dependencies And Integration Points
Depends on jQuery, Dust core, and Moment.js. It must be loaded after `dust-full-2.0.0.min.js`, `dust-helpers-1.1.1.min.js`, and `moment.min.js` where date filters are used. It is included by NameNode, DataNode, JournalNode, SecondaryNameNode, Balancer, and Explorer pages. `hdfs/dfshealth.js` and `journal/jn.js` use `load_json` for JMX fan-out; many templates in `dfshealth.html`, `explorer.html`, `datanode.html`, and `balancer.html` consume the filters.

## Risks
The comment says "Load a sequence of JSON", but the implementation launches asynchronous requests concurrently. `load_json([])` never calls `success_cb` because the countdown starts at zero and no request decrements it. `fmt_number` calls `v.toLocaleString()` and will fail for `null`/`undefined`. `format_compile_info` assumes the input contains `" by "` and will append `undefined` if it does not. `fmt_bytes` and `fmt_human_number` do not explicitly handle negative, `NaN`, or infinite inputs. `helper_to_permission` mixes parsed octal state with decimal digit extraction from the original value, so malformed permission strings can produce misleading output.

## Test Signals
Unit-style browser tests can call each filter with boundary values: `0`, `1`, powers of `1024`, large byte values, `-1`, missing compile-info delimiters, sticky permissions such as `1755`, and directory/ACL booleans. For `load_json`, stub `$.get` to verify all named responses are collected, first failure calls the error callback with the failing URL, already-started successes after failure do not trigger success, and the empty-bean behavior is either documented or fixed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dfs-dust.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dust-full-2.0.0.min.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dust-full-2.0.0.min.js

## Purpose
Vendored minified Dust.js 2.0.0 "full" build. It provides the browser-side template runtime plus parser/compiler used by HDFS web UI pages to compile inline `<script type="text/x-dust-template">` templates and render JMX responses into HTML.

## Important APIs, Types, And Functions
Runtime inspection exposes `dust.helpers`, `dust.cache`, `dust.register`, `dust.render`, `dust.stream`, `dust.renderSource`, `dust.compileFn`, `dust.load`, `dust.loadSource`, `dust.isArray`, `dust.nextTick`, `dust.isEmpty`, `dust.filter`, `dust.filters`, `dust.makeBase`, `dust.escapeHtml`, `dust.escapeJs`, `dust.compile`, `dust.filterNode`, `dust.optimizers`, `dust.pragmas`, `dust.compileNode`, `dust.nodes`, and `dust.parse`. Core internal types include `Context`, `Stack`, `Stub`, `Stream`, `Chunk`, and `Tap`. Built-in filters are `h`, `j`, `u`, `uc`, `js`, and `jp`.

## Control Flow
On load, the file creates or exports the `dust` object. HDFS pages call `dust.loadSource(dust.compile(templateHtml, name))` during page initialization. Compilation parses Dust template syntax to JavaScript source, `loadSource` evaluates that source, and `dust.register` stores the compiled template function in `dust.cache`. Calls to `dust.render(name, data, callback)` create a `Stub`, load the named template, wrap the data in a `Context`, write output through chunks, and invoke the callback with the rendered string. `dust.stream` follows the same template loading path but returns a stream-like object.

## State And Persistence
The main state is `dust.cache`, a page-local registry keyed by template name such as `dfshealth`, `startup-progress`, `datanode-info`, `snapshot-info`, `explorer`, `block-info`, `dn`, and `jn`. Context stack state is transient per render. No browser storage is used by Dust itself.

## Dependencies And Integration Points
The browser build can stand alone, but HDFS uses it with `dust-helpers-1.1.1.min.js` and `dfs-dust.js`. It integrates with inline templates in `hdfs/dfshealth.html`, `hdfs/explorer.html`, `datanode/datanode.html`, `journal/journalnode.html`, `secondary/status.html`, and `balancer/balancer.html`. Page scripts such as `dfshealth.js`, `explorer.js`, and `dn.js` compile templates, create helper bases with `dust.makeBase`, and call `dust.render`.

## Risks
`dust.loadSource` uses `eval(source)`, so only trusted templates should be compiled. In this repository templates are static HTML resources, but any future path that compiles user-controlled template text would be code execution. The library is old and minified, making security review and source-level debugging difficult. Optional nested keys in startup progress already required renaming in `dfshealth.js`, indicating Dust 2.0.0 has edge cases with nested optional data. Rendering errors are often passed to callbacks, but several page scripts do not surface `err` before replacing DOM content.

## Test Signals
Smoke-test by compiling and rendering each inline template on the pages that include this file. Verify `dust.cache` contains the expected template names after initialization, built-in escaping filters still escape HTML and JavaScript contexts, and pages render both normal JMX data and missing/optional fields without throwing. Any upgrade should compare rendered HTML for `dfshealth`, DataNode, JournalNode, Balancer, and Explorer templates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dust-full-2.0.0.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dust-helpers-1.1.1.min.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dust-helpers-1.1.1.min.js

## Purpose
Vendored minified Dust helpers plugin. It augments `dust.helpers` with conditional, comparison, selection, index, separator, math, size, and context-dump helpers used by HDFS Dust templates and page-local helper bases.

## Important APIs, Types, And Functions
After loading with Dust core in a browser, runtime inspection shows helper names `contextDump`, `default`, `eq`, `gt`, `gte`, `idx`, `if`, `lt`, `lte`, `math`, `ne`, `select`, `sep`, `size`, and `tap`. `tap` resolves literal/function parameters into values. The comparison helpers share a filter operation routine that supports explicit `key`, selected values from `select`, optional `type` conversion (`number`, `string`, `boolean`, `date`, `context`), body rendering on match, and `{:else}` rendering on mismatch. `math` supports `mod`, `add`, `subtract`, `multiply`, `divide`, `ceil`, `floor`, `round`, and `abs`.

## Control Flow
The plugin executes immediately and assigns a new helpers object onto the global Dust object. Templates invoke helpers such as `{@eq key=max value="-1" type="number"}...{:else}...{/eq}`. During rendering, helpers read parameters through `tap`, may push temporary selection state into the context stack, then render the main or else body into the current chunk. `sep` and `idx` inspect `ctx.stack.index` and `ctx.stack.of` to support array iteration formatting.

## State And Persistence
The file mutates `dust.helpers` globally for the current page. Most helpers are stateless, but `select` and `math` can push temporary objects containing `isSelect`, `isResolved`, and `selectKey` onto the render context. `contextDump` writes JSON output or logs to console, but no browser storage is used.

## Dependencies And Integration Points
Depends on Dust core being available first. It supports CommonJS by requiring `dustjs-linkedin`, but HDFS pages use the browser global path. It is loaded before `dfs-dust.js` on all pages that use Dust. HDFS templates use helpers such as `eq` for unbounded memory display and page scripts call `dust.helpers.tap` in custom helpers in `dfshealth.js`, `explorer.js`, `dn.js`, and `jn.js`.

## Risks
The `if` helper evaluates the `cond` parameter with JavaScript `eval`, so conditions must remain trusted static template code. The boolean conversion treats many non-empty strings as true except a special `"false"` path, which can surprise template authors. Math divide/mod by zero logs warnings but still writes JavaScript `Infinity` or `NaN` results. `contextDump` can expose the current render context if accidentally left in a template. Because the file replaces/sets `dust.helpers`, load order matters if other helper plugins are added.

## Test Signals
Render representative templates using `eq`, `ne`, comparison helpers, `select/default`, `idx`, `sep`, and `math` with both main and else bodies. Include type conversion cases for numeric strings, booleans, and dates. Page smoke tests should confirm HDFS templates using `{@eq ...}` still choose the correct branch and custom helpers using `dust.helpers.tap` continue to resolve parameter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/dust-helpers-1.1.1.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/histogram-hostip.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/histogram-hostip.js

## Purpose
Small HDFS-specific browser helper for the DataNode usage histogram. It lets users click a D3 histogram bar and see the DataNode host/IP addresses whose disk usage falls inside that bin.

## Important APIs, Types, And Functions
The file defines two global functions: `open_hostip_list(x0, x1)` and `close_hostip_list()`. `open_hostip_list` reads the global `liveNodes` array, filters DataNodes by `(dn.usedSpace / dn.capacity) * 100.0`, extracts host/IP text from `dn.infoAddr`, creates a read-only `<textarea id="datanode_ips">`, creates a clickable `<div id="close_ips">X</div>`, and appends both under `#datanode-usage-histogram`. `close_hostip_list` removes those two elements with jQuery selectors.

## Control Flow
`hdfs/dfshealth.js` sets `window.liveNodes = dnData.LiveNodes` in `renderHistogram`. It attaches an inline `onclick` attribute to each D3 bar rectangle that calls `open_hostip_list(d.x0, d.x1)`. When invoked, `open_hostip_list` first removes any existing list, scans all live nodes, coerces zero usage to `1` so empty nodes are included in the first positive bin, excludes nodes above the clicked range, and writes one address per line into the textarea. Clicking the `X` div calls `close_hostip_list`.

## State And Persistence
The helper relies on page-global mutable state: `window.liveNodes` supplied by `dfshealth.js`. Its own state is DOM state: a relative-position style on `#datanode-usage-histogram`, the generated textarea, and the generated close div. Nothing is persisted across page loads.

## Dependencies And Integration Points
Depends on jQuery for removal and on the DOM element `#datanode-usage-histogram` from `dfshealth.html`. It is loaded by `dfshealth.html` after `dfshealth.js`; that order is acceptable because the functions only need to exist when a user later clicks a histogram bar. It is tightly coupled to DataNode objects containing `usedSpace`, `capacity`, and `infoAddr`, and to the bin bounds produced by D3's `histogram()`.

## Risks
The script assumes `liveNodes` exists and is an array; clicking before histogram setup or after a failed JMX request would throw. Division by zero or missing capacity can produce invalid usage values. The IPv6 parser only handles bracketed `host]:port` patterns and strips the leading `[`, while IPv4/hostname parsing splits at the first colon. The close div style contains `height;20px`, a typo that leaves height unset. Setting inline `onclick` and writing `innerHTML` are acceptable with current generated values, but using `textContent`/event listeners would be safer and easier to audit.

## Test Signals
Create a page fixture with `#datanode-usage-histogram` and a `liveNodes` array containing IPv4, hostname, and bracketed IPv6 `infoAddr` values. Call `open_hostip_list(0, 5)` and verify the textarea contains the expected one-address-per-line list, previous generated nodes are removed on repeated calls, and `close_hostip_list()` removes both generated elements. Include boundary checks for exactly `x0`, exactly `x1`, zero usage, and usage above 100 percent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/histogram-hostip.js -->
