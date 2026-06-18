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
