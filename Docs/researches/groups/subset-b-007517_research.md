# Research Report: subset-b-007517

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/jquery-3.6.0.min.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/jquery-3.6.0.min.js

## Purpose
This is the vendored minified jQuery 3.6.0 browser library used by the HDFS web applications. It provides the global `jQuery` and `$` functions that the NameNode, DataNode, JournalNode, Balancer, SecondaryNameNode, and file explorer pages rely on for DOM lookup and mutation, event binding, AJAX, Deferred/callback handling, CSS/attribute helpers, and plugin hosting.

## Important APIs, Types, and Functions
- Public exports are installed through the UMD wrapper as `window.jQuery` and `window.$` in browser mode, with CommonJS and AMD compatibility preserved by the upstream wrapper.
- `S.fn.init` is the constructor behind `$()` selections. Its prototype exposes traversal and manipulation methods such as `each`, `map`, `slice`, `first`, `last`, `eq`, `end`, event helpers, CSS/dimension helpers, and legacy aliases like `bind`, `unbind`, `delegate`, and `undelegate`.
- `S.extend` and `S.fn.extend` merge objects and attach static or instance APIs. The implementation explicitly avoids assigning `__proto__` during deep copies, which is a relevant hardening detail for a general-purpose utility.
- AJAX APIs include `$.ajax`, shorthand helpers such as `$.get`, ajax event methods, and `$.ajaxSetup`. Hadoop's `rest-csrf.js` uses `$.ajaxSetup({ beforeSend: ... })`, while web UI pages use `$.ajax` and `$.get` against `/conf`, `/jmx`, and `/webhdfs/v1/...`.
- Deferred primitives include `$.Callbacks`, `$.Deferred`, and promise-style chaining, which back jQuery AJAX completion and failure flows.
- Compatibility aliases include `$.parseJSON = JSON.parse`, `$.trim`, `$.isArray`, `$.isFunction`, `$.isWindow`, `$.isNumeric`, `$.proxy`, and `$.noConflict`.

## Control Flow
The file executes immediately. The wrapper detects CommonJS/AMD/browser environments, creates the jQuery factory against the current `window.document`, builds internal helper tables and prototypes, then attaches `jQuery` and `$` unless a module loader consumes the export. There is no Hadoop-specific branch in this file; all project behavior comes from downstream page scripts and plugins.

In the HDFS UI flow, HTML pages load jQuery before `jquery.dataTables.min.js`, `dataTables.bootstrap.js`, `moment.min.js`, `json-bignum.js`, `rest-csrf.js`, and page-specific scripts. That ordering is important because DataTables attaches to `$.fn`, `rest-csrf.js` configures global AJAX behavior, and the page scripts call `$`, `$.get`, `$.ajax`, DOM event helpers, and plugin methods during initialization.

## State and Persistence Behavior
Runtime state is kept in memory in the browser only. jQuery stores event handlers, Deferred queues, per-node data, animation queues, and AJAX global settings in JavaScript objects associated with the current page. It does not write browser storage or persist state across page loads in this vendored file.

The most relevant mutable integration state is global: `window.$`, `window.jQuery`, `$.ajaxSetup` defaults, `$.fn` plugins, and `$.fn.dataTable`/`$.fn.DataTable` added by DataTables. A change in load order or a second jQuery copy would affect every downstream plugin.

## Dependencies and Integration Points
The library depends on a browser-like `window` with a `document`. Hadoop pages include it via `/static/jquery-3.6.0.min.js`. Direct consumers found in the HDFS webapp include:
- `hdfs/dfshealth.js`, which uses DOM selection, Dust template insertion, `$.get`, DataTables extension points, event binding, and selectors.
- `hdfs/explorer.js`, which uses `$.ajax`, `$.get`, event binding, editable plugins, modal interactions, and table initialization.
- `static/rest-csrf.js`, which synchronously reads `/conf` and installs a global AJAX `beforeSend` hook for WebHDFS CSRF headers.
- DataNode, JournalNode, Balancer, and SecondaryNameNode scripts, which use jQuery with Moment and shared Dust helpers.

## Risks and Edge Cases
- This is a minified vendored dependency, so local maintainers should not make ad hoc edits. Upgrades need browser regression testing across all web UI pages and plugins.
- Because `rest-csrf.js` modifies global AJAX behavior through `$.ajaxSetup`, any replacement or duplicate loading of jQuery can silently remove CSRF header injection for WebHDFS requests.
- Synchronous AJAX is still used by `rest-csrf.js` and portions of `explorer.js`; jQuery supports it, but browsers may warn or constrain synchronous main-thread network work.
- The library is security-sensitive because every web UI page depends on its selector, HTML insertion, and AJAX behavior. Vendored version drift should be tracked with third-party dependency scanning.
- Plugin compatibility matters: Hadoop ships DataTables 1.11.5 and Bootstrap DataTables integration that expect jQuery plugin semantics.

## Test Signals
There is no direct unit test for this minified file in the researched set. Indirect signals come from HDFS web UI behavior: table initialization in `dfshealth.js` and `explorer.js`, AJAX calls to `/conf`, `/jmx`, and `/webhdfs/v1`, and page load ordering in `dfshealth.html`, `explorer.html`, `datanode.html`, `journalnode.html`, `balancer.html`, and `secondary/status.html`. Manual or browser-based smoke tests should cover page load, AJAX failures, DataTables filtering/sorting, file explorer mutations, and CSRF-enabled WebHDFS operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/jquery-3.6.0.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/jquery.dataTables.min.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/jquery.dataTables.min.js

## Purpose
This is the vendored minified DataTables 1.11.5 library. It extends jQuery with dynamic table rendering, sorting, searching, pagination, column metadata, AJAX-backed data loading, state helpers, and a modern API facade used by the HDFS NameNode web UI.

## Important APIs, Types, and Functions
- The UMD wrapper attaches the library to jQuery and exports the main plugin as `$.fn.dataTable`. It also defines the capitalized API constructor helper `$.fn.DataTable`.
- `DataTable.Api` exposes table/row/column/cell accessors and chainable operations. Hadoop uses this through `$('#table-snapshots').DataTable(...)`, `table.row(tr)`, `row.child(...)`, `this.api().column(...)`, and `$.fn.dataTable.isDataTable(...)`.
- `$.fn.dataTable.ext` stores extension points for ordering, rendering, filtering, type detection, classes, and internal helpers. `dfshealth.js` registers `$.fn.dataTable.ext.order['ng-value']` to sort on a custom `ng-value` attribute rather than display text.
- Render helpers include `DataTable.render.number(...)` and `DataTable.render.text()`. Internal escaping uses HTML entity replacement for display/filter contexts.
- Internal functions manage column option normalization, DOM row extraction, sorting, filtering, pagination, width calculation, processing indicators, state save/load, and AJAX updates.
- DataTables settings are stored in `$.fn.dataTableSettings`, and compatibility extension data is exposed through `$.fn.dataTableExt`.

## Control Flow
The file executes after jQuery is loaded. It installs any small polyfills needed by the compiled bundle, runs the DataTables factory, initializes default settings and extension registries, and publishes `dataTable`/`DataTable` on `$.fn`.

When a Hadoop script calls `.dataTable({...})` or `.DataTable({...})`, the plugin reads table headers and supplied column definitions, builds an internal settings object, indexes row data, registers event handlers for sorting/filtering/pagination, draws wrapper DOM, then performs redraws as users interact with filters and pagination controls. The lower-case `dataTable` path returns a jQuery-style plugin object; the capitalized `DataTable` path returns a DataTables API instance.

## State and Persistence Behavior
DataTables stores per-table runtime settings and row/column caches in memory and associates them with the table node. State includes current page, search text, ordering, column visibility, row data, draw counters, and extension callbacks. This vendored file supports state save/load machinery, but the observed Hadoop initializations do not enable durable state persistence, so normal table state resets on page reload.

The library mutates the DOM by wrapping tables, inserting controls, adding sorting classes, generating pagination widgets, and in snapshot details creating child rows when page code asks for them. It also stores marker data such as row indexes on DOM nodes.

## Dependencies and Integration Points
This file depends on jQuery and must be loaded before `dataTables.bootstrap.js`, which adapts DataTables markup/classes to Bootstrap 3. Hadoop uses it in:
- `hdfs/dfshealth.js` for DataNode tables, snapshot tables, nested snapshot detail tables, filtering by DataNode status, custom attribute ordering, and wide table handling.
- `hdfs/explorer.js` for the file browser directory listing with deferred rendering, size/date render functions, paging, and column search/order settings.
- `hdfs/dfshealth.html` and `hdfs/explorer.html`, which include DataTables CSS, this script, and the Bootstrap integration script in order.

## Risks and Edge Cases
- The file is minified and generated upstream; local modifications are high-risk and should instead be made through configuration or by upgrading the vendored library.
- DataTables depends heavily on column definition alignment. If a Dust template changes table column count without matching `columns`/`columnDefs`, sorting and rendering can break at runtime.
- Hadoop relies on the custom `ng-value` ordering extension. Missing attributes or string values in numeric columns can produce unexpected sort order.
- The library adds substantial DOM around tables. Large NameNode datasets can stress browser memory and render time, although the explorer enables `deferRender` for its listing table.
- DataTables should be kept in lockstep with the Bootstrap integration file and CSS; mismatched versions can break pagination renderers and class names.

## Test Signals
There is no direct unit test for this minified dependency. Indirect coverage should come from browser smoke tests that open the NameNode health and explorer pages, verify DataNode and snapshot table sorting/filtering/pagination, expand snapshot detail rows, and browse large directories. Regression checks should include tables with missing/default column values because Hadoop's initialization supplies `defaultContent` for several columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/jquery.dataTables.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/json-bignum.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/json-bignum.js

## Purpose
This file provides `window.JSONParseBigNum`, a JSON parser based on Douglas Crockford's recursive-descent reference parser with Hadoop-specific handling for large numeric values. Its main purpose in the HDFS web UI is to parse WebHDFS JSON responses without losing precision for block IDs, generation stamps, file lengths, or other integer-like values that may exceed JavaScript's safe integer range.

## Important APIs, Types, and Functions
- `BigNumber(number)` is a small wrapper type that stores the original numeric token as `numberStr`. Its constructor validates the token with `parseFloat`/`isFinite`, and `toString()` returns the preserved string.
- `exports.JSONParseBigNum` is exported from an IIFE invoked with `window`, so the public API is a global browser function.
- Parser state variables are closure-scoped: `text` holds the source string, `at` is the current index, and `ch` is the current character.
- `error(m)` throws an object with `name: 'SyntaxError'`, `message`, `at`, and `text`.
- `next(c)`, `white()`, `word()`, `string()`, `number()`, `array()`, `object()`, and `value()` implement recursive-descent JSON parsing.
- The returned parse function accepts `(source, reviver)` and mirrors `JSON.parse` reviver traversal semantics, including deletion when the reviver returns `undefined`.

## Control Flow
Parsing starts by assigning the source to the closure state, setting `at = 0`, priming `ch = ' '`, and calling `value()`. `value()` skips whitespace and dispatches by the current character to object, array, string, number, or literal parsing. Objects reject duplicate keys with an explicit `Duplicate key` syntax error. Arrays and objects recursively call `value()` until their closing delimiter is reached.

The key Hadoop-specific path is `number()`. It builds the number token as a string, converts it with unary `+`, rejects non-finite results, then compares `number.toString()` with the original token. If JavaScript changed the textual representation, the parser attempts to return `new BigNumber(string)` instead of the rounded numeric value. If the wrapper cannot be constructed, it falls back to the normal numeric value.

After parsing, the function skips trailing whitespace and rejects any remaining characters. If a reviver is provided, it walks the resulting object graph depth-first using a temporary root holder and calls the reviver for every key/value pair.

## State and Persistence Behavior
All parser state is transient and closure-local to the parse invocation, but the variables are shared by the exported parser closure. Calls are synchronous and not reentrant; a reviver that calls `JSONParseBigNum` recursively would overwrite the shared parser state. Parsed results are normal JavaScript arrays/objects/numbers/strings/booleans/null plus `BigNumber` wrapper instances for precision-sensitive numeric tokens.

The file does not persist data, does not touch browser storage, and does not make network requests.

## Dependencies and Integration Points
The file depends only on standard browser JavaScript and `window`. It is loaded by `hdfs/explorer.html` before `rest-csrf.js`, `moment.min.js`, `dfs-dust.js`, and `explorer.js`.

The observed consumer is `hdfs/explorer.js`, which calls `JSONParseBigNum(data_text)` for a `/webhdfs/v1... ?op=GET_BLOCK_LOCATIONS` AJAX response declared as `dataType: 'text'`. That flow then passes the parsed `LocatedBlocks` data into Dust templates and UI controls. The custom parser prevents precision loss before block metadata is displayed or selected.

## Risks and Edge Cases
- The big-number detection compares `number.toString()` with the source token. Numerically equivalent alternate spellings such as exponent notation, leading zeros rejected/accepted by parser behavior, or decimal formatting can influence whether a value is wrapped.
- `BigNumber` is local to the closure and not exported directly. Consumers can stringify wrapper values, but cannot use `instanceof BigNumber` outside the closure.
- The parser uses a plain object for JSON objects. It rejects duplicate keys, which is stricter than some parsers and could reject inputs accepted by native `JSON.parse`.
- The parser does not use native `JSON.parse`, so it has its own syntax, performance, and maintenance risks. Large WebHDFS responses can parse more slowly than native JSON.
- Shared closure state means recursive use through a reviver is unsafe.
- Error throws are plain objects rather than `SyntaxError` instances, so consumers expecting `err instanceof SyntaxError` would not match.

## Test Signals
No direct tests for this file were found in the listed set. Useful regression tests would parse large block IDs above JavaScript's safe integer range, ordinary integers, decimals, exponent notation, duplicate keys, invalid strings, arrays/objects with whitespace, and reviver transformations. Browser-level testing should verify that the file explorer block-location modal displays large numeric identifiers without rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/json-bignum.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/moment.min.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/moment.min.js

## Purpose
This is the vendored minified Moment.js 2.29.4 library. The HDFS web UI uses it to format timestamps from JMX and WebHDFS responses, compute relative durations, and present date/time values in human-readable strings across NameNode, DataNode, JournalNode, Balancer, SecondaryNameNode, and shared Dust-rendered pages.

## Important APIs, Types, and Functions
- The UMD wrapper exports a global `moment` function in browser mode and supports CommonJS/AMD environments.
- `moment(input)` creates local-time Moment instances. Hadoop call sites frequently pass numeric millisecond timestamps via `moment(Number(value))`.
- Formatting APIs include `.format(pattern)`, `.toISOString()`, `.toString()`, `.toJSON()`, and token parsing/formatting machinery. Hadoop uses patterns such as `ddd MMM DD HH:mm:ss ZZ YYYY`, `MMM DD YYYY`, and `MMM DD HH:mm`.
- Relative and duration APIs include `moment.duration(...)`, `.fromNow(...)`, `.humanize(...)`, and unit accessors. DataNode code uses `moment().subtract(Number(value), 'seconds').fromNow(true)`.
- Calendar and comparison helpers include `moment.min`, `moment.max`, `.diff`, `.isBefore`, `.isAfter`, `.isSame`, and related unit-normalization code.
- Locale APIs include `moment.locale`, `moment.defineLocale`, `moment.updateLocale`, `moment.localeData`, weekday/month name helpers, and parsing flags.
- UTC and epoch helpers include `moment.utc`, `moment.unix`, `moment.parseZone`, token `X`, and token `x`.

## Control Flow
The file executes once, initializes the Moment factory, builds parsing and formatting token tables, installs default English locale behavior, defines prototype methods, then publishes `moment`. Calls from Hadoop scripts construct Moment objects from numeric timestamps or current time, perform optional arithmetic such as subtracting six months or seconds, then format or humanize the result for insertion into Dust templates or DataTables renderers.

In `hdfs/explorer.js`, Moment decides whether a modification time is older than six months and formats it with or without exact time. In `dfshealth.js` and shared Dust helpers, it renders JMX timestamps into full date strings. In DataNode status code, it converts elapsed seconds into relative text.

## State and Persistence Behavior
Moment maintains process/page-global runtime state for the active locale, locale registry, deprecation handlers, parsing flags, and relative-time thresholds. Individual Moment instances wrap JavaScript `Date` objects plus parsing metadata and UTC/offset flags. This file does not persist data to browser storage.

Formatted output depends on the browser's local timezone unless code uses UTC or parses a zone. Hadoop call sites generally use local-time formatting, so users in different timezones may see different rendered clock times for the same raw timestamp.

## Dependencies and Integration Points
Moment depends only on browser JavaScript and is loaded via `/static/moment.min.js`. It is included by multiple HDFS web pages after jQuery and before page-specific scripts. Integration points include:
- `hdfs/dfshealth.js` for NameNode health, startup progress, DataNode, volume failure, and snapshot timestamp display.
- `hdfs/explorer.js` for file modification time formatting and block/file detail helpers.
- `static/dfs-dust.js` for shared Dust date filters.
- `datanode/dn.js`, `journal/jn.js`, `balancer/balancer.js`, and `secondary/status.html` flows for status timestamps and relative ages.

## Risks and Edge Cases
- The file is a minified vendored dependency and should be upgraded as a unit, not locally edited.
- Moment is mutable: operations on an instance can alter it unless cloned. Current Hadoop call sites mostly use fresh instances, which limits this risk.
- Local-time formatting can make distributed-cluster timestamps appear different depending on the browser timezone.
- Invalid or missing numeric timestamps can produce "Invalid date" output rather than a Hadoop-specific error message.
- Moment is relatively large for simple formatting. If web UI performance or bundle size becomes a priority, replacement would require auditing every formatting token and relative-time call.

## Test Signals
No direct tests target this vendored file. Indirect validation should open web UI pages and verify timestamp display for NameNode overview, DataNode tables, snapshots, file explorer listings, DataNode status, JournalNode status, Balancer status, and SecondaryNameNode status. Edge checks should include zero, missing, future, old, and timezone-sensitive timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/moment.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/rest-csrf.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/rest-csrf.js

## Purpose
This Hadoop-specific browser script configures client-side CSRF protection for WebHDFS REST requests. It reads NameNode configuration from `/conf`, determines whether WebHDFS CSRF protection is enabled, and if so installs a jQuery global AJAX `beforeSend` hook that adds the configured custom header to protected `/webhdfs/` requests.

## Important APIs, Types, and Functions
- The file is an immediately invoked function expression with `"use strict"` and no exported public API.
- Closure state includes `restCsrfCustomHeader` and `restCsrfMethodsToIgnore`, initially `null`.
- A synchronous `$.ajax({ url: '/conf', dataType: 'xml', async: false })` fetch reads the NameNode XML configuration before subsequent scripts issue WebHDFS calls.
- Local helpers `getBooleanValue(element)`, `getTrimmedStringValue(element)`, and `getTrimmedStringArrayValue(element)` parse property values from XML.
- The script recognizes `dfs.webhdfs.rest-csrf.enabled`, `dfs.webhdfs.rest-csrf.custom-header`, and `dfs.webhdfs.rest-csrf.methods-to-ignore`.
- `addRestCsrfCustomHeader(xhr, settings)` is the installed callback. It checks the URL prefix, request method, configured header name, and ignored-method map before calling `xhr.setRequestHeader(restCsrfCustomHeader, '""')`.

## Control Flow
On load, the script requests `/conf` synchronously. In the success callback, it iterates all `<property>` elements, extracts the three CSRF-related settings, and if CSRF is enabled builds an object map of ignored methods. It then calls `$.ajaxSetup({ beforeSend: addRestCsrfCustomHeader })`.

For every later jQuery AJAX request, the callback returns immediately unless `settings.url` starts with `/webhdfs/`. It then reads `settings.type` and skips the request if the method is in the ignore map. For protected methods, it adds the configured header with a placeholder value because WebHDFS only requires header presence.

## State and Persistence Behavior
The script stores CSRF configuration only in closure variables and jQuery's global AJAX setup for the current page. It does not persist configuration in cookies, local storage, or server state. Configuration changes on the server require a page reload to be reflected in client behavior.

`$.ajaxSetup` is page-global. Later code that overwrites `beforeSend` through another `ajaxSetup` call could disable this protection unless it explicitly chains the previous callback.

## Dependencies and Integration Points
This file depends on jQuery and browser support for `String.prototype.startsWith`. It also depends on the NameNode `/conf` endpoint returning XML with the WebHDFS CSRF properties when configured.

The main integration point is `hdfs/explorer.html`, which loads this script before `explorer.js`. The explorer issues WebHDFS operations such as `GET_BLOCK_LOCATIONS`, `OPEN`, `LISTSTATUS`, `SETOWNER`, `SETREPLICATION`, and deletes/mutations through `/webhdfs/v1...`; this script ensures mutating or otherwise protected requests carry the required CSRF header when server-side enforcement is enabled.

The relevant server-side/documentation integration is the WebHDFS configuration documented in `src/site/markdown/WebHDFS.md`, including enabled flag, custom header name, ignored methods, and browser user-agent matching.

## Risks and Edge Cases
- The initial `/conf` request is synchronous and blocks page loading. This enforces ordering but can degrade UX or fail under browser policies that discourage sync XHR on the main thread.
- If `/conf` fails, the `.done` callback never runs and no CSRF hook is installed. A CSRF-enabled server would then reject protected WebHDFS requests rather than showing a specific configuration error.
- Method matching is case-sensitive because ignored methods are stored exactly as configured and compared to `settings.type`. jQuery defaults are usually uppercase, but inconsistent case in config or request options could cause unexpected header injection or omission.
- Only URLs starting with `/webhdfs/` are covered. Absolute URLs, alternate prefixes, or redirected DataNode URLs are intentionally outside this hook.
- The script replaces the global `beforeSend` option. Other global AJAX setup code can conflict unless composed carefully.
- `startsWith` may not exist in very old browsers; this is acceptable for modern Hadoop web UI assumptions but is still a compatibility point.

## Test Signals
No direct unit test was in the researched set. Browser/integration tests should enable WebHDFS CSRF protection, load the explorer, and verify that protected `/webhdfs/` methods include the configured header while ignored methods do not. Tests should also cover a failed `/conf` load, lowercase method values, and interaction with any other global jQuery AJAX setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/rest-csrf.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/site/site.xml

## Purpose
This Maven site descriptor configures the generated documentation site for the `hadoop-hdfs` module. It names the project as `Apache Hadoop ${project.version}`, selects the Maven Stylus skin, and adds a top-level link back to the Apache Hadoop website.

## Important APIs, Types, and Functions
This is declarative XML rather than executable code. Important elements are:
- `<project name="Apache Hadoop ${project.version}">`, which sets the displayed site project name using Maven property interpolation.
- `<skin>`, with `org.apache.maven.skins:maven-stylus-skin:${maven-stylus-skin.version}`, which selects the documentation site's visual skin.
- `<body><links><item ... /></links></body>`, which defines a navigation link named `Apache Hadoop` pointing to `http://hadoop.apache.org/`.

## Control Flow
There is no runtime control flow. During Maven site generation, Maven reads this descriptor, interpolates properties from the build, resolves the configured skin artifact, and applies the body link configuration when rendering the module's site pages.

## State and Persistence Behavior
The file has no mutable runtime state. Its only persistence effect is build output: generated site pages inherit the configured project name, skin, and link. Changes to this file affect future site generation but not the running HDFS service.

## Dependencies and Integration Points
The descriptor depends on Maven Site Plugin conventions and the `maven-stylus-skin.version` property being defined in the broader Hadoop build. It integrates with HDFS module documentation under `src/site`, including Markdown content such as WebHDFS documentation, and with parent build configuration that supplies project version and plugin settings.

## Risks and Edge Cases
- A missing or incompatible `${maven-stylus-skin.version}` property would break site generation or produce an unexpected site theme.
- The Apache Hadoop link uses `http://` rather than `https://`; this is a documentation navigation choice but may be flagged by link or security scanners.
- Since this descriptor is module-scoped, changes can alter generated documentation appearance/navigation without affecting tests that only compile code.

## Test Signals
Validation is through Maven site generation rather than unit tests. A useful check is running the relevant Maven site goal for the HDFS module and verifying that the skin resolves, the project version is interpolated, and the Apache Hadoop navigation link appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/site/site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestGenericRefresh.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestGenericRefresh.java

## Purpose
This JUnit 5 test class verifies the generic refresh mechanism exposed through `DFSAdmin -refresh` against a live in-process HDFS NameNode. It exercises argument validation, handler lookup, handler invocation, variable refresh arguments, unregister behavior, multiple handlers under one identifier, return-code merging, and exception handling.

## Important APIs, Types, and Functions
- Static test fixtures include `MiniDFSCluster cluster`, `Configuration config`, and two mock `RefreshHandler` instances.
- `setUpBeforeClass()` creates a `Configuration`, enables `hadoop.security.authorization`, sets the default filesystem URI to `hdfs://localhost:0`, builds a `MiniDFSCluster`, and waits for it to become active.
- `tearDownBeforeClass()` shuts down the cluster if it was created.
- `setUp()` creates two Mockito `RefreshHandler` mocks and registers them in `RefreshRegistry.defaultRegistry()` under `firstHandler` and `secondHandler`.
- `tearDown()` unregisters the default test handlers after each test using `unregisterAll`.
- Test methods instantiate `new DFSAdmin(config)` and call `admin.run(...)` with `-refresh` arguments targeting `localhost:<NameNodePort>`.
- Mockito stubbing and verification assert which handlers are called and with which identifier/argument array.

## Control Flow
The class-level setup starts a real NameNode once for all tests. Before each test, `firstHandler` is configured to return `RefreshResponse.successResponse()` for any identifier/argument array, while `secondHandler` returns different response codes for the exact `secondHandler` calls with `["one"]` and `["one", "two"]`.

Each test drives the `DFSAdmin -refresh` command path:
- `testInvalidCommand` passes too few arguments and expects `-1`.
- `testInvalidIdentifier` targets an unregistered identity and expects `-1`.
- `testValidIdentifier` refreshes `firstHandler`, expects success, verifies first handler invocation, and verifies the second handler is not called.
- `testVariableArgs` refreshes `secondHandler` with one and two trailing arguments, expecting return codes `2` and `3`.
- `testUnregistration` unregisters `firstHandler` and verifies a subsequent refresh fails.
- `testUnregistrationReturnValue` checks `RefreshRegistry.unregister` returns `true` for a registered handler.
- `testMultipleRegistration` registers both default handlers under `sharedId`, invokes refresh with one argument, expects merged failure `-1`, and verifies both handlers were called.
- `testMultipleReturnCodeMerging` registers two handlers returning non-zero codes and expects merged result `-1`.
- `testExceptionResultsInNormalError` registers two throwing handlers, verifies the command returns `-1`, and confirms both handlers were attempted.

## State and Persistence Behavior
State is held in the singleton `RefreshRegistry.defaultRegistry()` and in the static MiniDFSCluster. The test carefully unregisters standard handler identities after each test, and ad hoc shared identities are cleaned up within the tests that create them. No persistent filesystem assertions are made; the cluster is used to provide a reachable NameNode RPC/admin endpoint.

Because `RefreshRegistry` is process-global, missed cleanup could contaminate other tests in the same JVM. The use of exact identifiers and `unregisterAll` reduces that risk.

## Dependencies and Integration Points
The test depends on HDFS mini-cluster infrastructure, `DFSAdmin`, `RefreshRegistry`, `RefreshHandler`, `RefreshResponse`, Hadoop `Configuration`, `FileSystem`, JUnit Jupiter lifecycle/test annotations, and Mockito.

It integrates the client-side admin command with server-side refresh dispatch. Enabling `hadoop.security.authorization` is significant because the refresh protocol is an admin operation and the MiniDFSCluster must expose the NameNode port used by `DFSAdmin`.

## Risks and Edge Cases
- Exact Mockito array matching is used in several stubs/verifications. If the production path changes array construction or argument normalization, tests may fail even if behavior is semantically close.
- The default registry singleton is shared process state. Parallel test execution or unexpected failures before cleanup can leave handlers registered.
- Tests assume `localhost:<cluster.getNameNodePort()>` reaches the mini-cluster NameNode. Environmental port or networking issues can make failures look like refresh logic failures.
- Multiple-handler return code behavior intentionally collapses conflicting/non-zero responses to `-1`; future changes to merging semantics need updates here.
- Exception tests verify that all handlers are called even when earlier handlers throw, protecting an important dispatch guarantee.

## Test Signals
This file is itself the test signal for generic refresh. It covers success, bad command syntax, missing handler identity, argument forwarding, unregister mechanics, multiple handlers, return-code merging, and exception containment. Additional useful coverage would include authorization-denied behavior, a mix of one successful and one throwing handler, and explicit cleanup guarantees when an assertion fails mid-test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestGenericRefresh.java -->
