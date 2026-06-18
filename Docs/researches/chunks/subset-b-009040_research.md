# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 210097-218440

## Scope

This chunk spans the end of SQLite's amalgamated `json.c` section, the start and main body of `rtree.c`, and the beginning of the optional `geopoly.c` inclusion. It is a large-file chunk, so this document records only the visible behavior in lines 210097-218440 and leaves whole-file synthesis to the later merge lane.

The JSON section covers JSONB-to-text rendering, pretty printing, JSON path lookup and mutation, SQL scalar and aggregate JSON functions, and the `json_each`/`json_tree` table-valued functions. The R-Tree section covers virtual-table state, node serialization, scan planning, priority-queue traversal, insert/delete/rebalance logic, shadow-table persistence, module registration, setup, and integrity checking. The final visible lines begin GeoPoly polygon parsing and scalar functions, guarded by `SQLITE_ENABLE_GEOPOLY`.

## Purpose

- Implement SQLite JSON1/JSONB SQL behavior for extraction, mutation, validation, pretty printing, aggregation, and JSON table-valued scans.
- Maintain JSONB as the internal representation for parsed JSON text, JSONB BLOB input, and editable update targets.
- Register the JSON scalar/aggregate functions and JSON virtual tables with SQLite when JSON support is enabled.
- Implement SQLite's R-Tree virtual table module over three shadow tables: `%_node`, `%_parent`, and `%_rowid`.
- Provide R-Tree query planning and execution for rowid lookup, coordinate constraints, and callback-driven `MATCH` constraints.
- Maintain on-disk R-Tree structure through inserts, deletes, splits, condense/reinsert operations, transaction cleanup, rename/drop, and integrity checks.
- Start optional GeoPoly support, which stores polygons as BLOBs and exposes conversion/rendering/geometry helper SQL functions.

## Important APIs, Types, And Functions

JSON/JSONB:

- `JsonPretty` carries a `JsonParse`, output `JsonString`, indent string, and current indentation depth for `json_pretty()`.
- `jsonTranslateBlobToPrettyText()` renders JSONB recursively with newline and indentation handling for arrays and objects; scalar values delegate to `jsonTranslateBlobToText()`.
- `jsonbArrayCount()` scans a JSONB array payload using `jsonbPayloadSize()` to count elements.
- `jsonBlobOverwrite()`, `jsonBlobEdit()`, and `jsonAfterEditSizeAdjust()` perform in-place JSONB byte edits, including a compact optimization that expands JSONB header encoding to avoid moving surrounding bytes when a replacement is slightly shorter.
- `jsonBytesToBypass()` and `jsonUnescapeOneChar()` implement JSON5-compatible escape handling, including escaped newlines, `\u` surrogate pairs, `\xNN`, `\0`, and legacy compatibility behind `SQLITE_BUG_COMPATIBLE_20250510`.
- `jsonLabelCompare()` and `jsonLabelCompareEscaped()` compare object labels with or without escape decoding.
- `jsonLookupStep()` is the central JSON path engine. It resolves `.` object labels and `[N]`, `[#]`, and `[#-N]` array indices, and it also performs edit actions (`JEDIT_DEL`, `JEDIT_REPL`, `JEDIT_INS`, `JEDIT_SET`) when `pParse->eEdit` is set.
- `jsonCreateEditSubstructure()` constructs missing nested JSONB objects/arrays for inserts such as `json_insert('{}', '$.a.b.c', 123)`.
- `jsonReturnFromBlob()` maps JSONB primitives to SQL values or returns JSON text/JSONB blobs for arrays and objects.
- `jsonFunctionArgToBlob()` converts SQL function arguments to JSONB insert/update payloads, preserving JSON-subtyped text as JSON and treating ordinary text as `JSONB_TEXTRAW`.
- `jsonArgIsJsonb()` detects whether a BLOB is JSONB, using full validation for small ambiguous blobs and a superficial outer-size check for larger blobs.
- `jsonParseFuncArg()` parses/caches function input as `JsonParse`, optionally cloning cached JSONB into editable memory.
- SQL entry points include `jsonQuoteFunc()`, `jsonArrayFunc()`, `jsonArrayLengthFunc()`, `jsonExtractFunc()`, `jsonPatchFunc()`, `jsonObjectFunc()`, `jsonRemoveFunc()`, `jsonReplaceFunc()`, `jsonSetFunc()`, `jsonTypeFunc()`, `jsonPrettyFunc()`, `jsonValidFunc()`, and `jsonErrorFunc()`.
- Aggregate/window handlers `jsonArrayStep()`, `jsonArrayFinal()`, `jsonArrayValue()`, `jsonObjectStep()`, `jsonObjectFinal()`, `jsonObjectValue()`, and `jsonGroupInverse()` build JSON arrays/objects and support window inverse removal.
- `JsonEachCursor`, `JsonParent`, and `JsonEachConnection` back the `json_each` and `json_tree` virtual tables.
- `jsonEachConnect()`, `jsonEachBestIndex()`, `jsonEachFilter()`, `jsonEachNext()`, `jsonEachColumn()`, and related cursor methods implement JSON table-valued function scans.
- `sqlite3RegisterJsonFunctions()` registers JSON scalar and aggregate functions; `sqlite3JsonTableFunctions()` registers `json_each` and `json_tree`.

R-Tree:

- `Rtree` is the virtual-table instance. It stores connection pointers, dimensions, coordinate type, node size, auxiliary column metadata, prepared statements for shadow tables, cached blob handle, node hash table, and transaction/cursor/reference state.
- `RtreeCursor` owns scan constraints, priority queue state, cached nodes, auxiliary-column read statement, and current search point.
- `RtreeNode` is an in-memory node image with reference count, dirty bit, parent pointer, node id, and on-disk byte buffer.
- `RtreeCell` is a deserialized rowid/child id plus up to five-dimensional lower/upper coordinate pairs.
- `RtreeConstraint`, `RtreeGeomCallback`, and `RtreeMatchArg` model coordinate constraints and callback-based `MATCH` searches.
- Serialization helpers `readInt16()`, `readInt64()`, `readCoord()`, `writeInt16()`, `writeInt64()`, and `writeCoord()` read/write big-endian shadow-table node bytes with platform byte-order optimizations.
- Node lifecycle helpers include `nodeAcquire()`, `nodeRelease()`, `nodeWrite()`, `nodeNew()`, `nodeBlobReset()`, `nodeHashLookup()`, `nodeHashInsert()`, and `nodeHashDelete()`.
- Cell helpers include `nodeGetRowid()`, `nodeGetCoord()`, `nodeGetCell()`, `nodeOverwriteCell()`, `nodeInsertCell()`, `nodeDeleteCell()`, `cellArea()`, `cellMargin()`, `cellUnion()`, `cellContains()`, and `cellOverlap()`.
- Search helpers include `rtreeBestIndex()`, `rtreeFilter()`, `rtreeEnqueue()`, `rtreeSearchPointNew()`, `rtreeSearchPointPop()`, `rtreeStepToLeaf()`, `rtreeRowid()`, and `rtreeColumn()`.
- Mutation helpers include `ChooseLeaf()`, `AdjustTree()`, `SplitNode()`, `splitNodeStartree()`, `updateMapping()`, `fixLeafParent()`, `deleteCell()`, `removeNode()`, `fixBoundingBox()`, `rtreeInsertCell()`, `reinsertNodeContent()`, `rtreeDeleteRowid()`, and `rtreeUpdate()`.
- Module lifecycle/setup functions include `rtreeCreate()`, `rtreeConnect()`, `rtreeDisconnect()`, `rtreeDestroy()`, `rtreeOpen()`, `rtreeClose()`, `rtreeBeginTransaction()`, `rtreeEndTransaction()`, `rtreeRollback()`, `rtreeRename()`, `rtreeSavepoint()`, `rtreeSqlInit()`, `getNodeSize()`, and `rtreeInit()`.
- Integrity/debug helpers include `rtreenode()`, `rtreedepth()`, `RtreeCheck`, `rtreeCheckTable()`, `rtreeIntegrity()`, and `rtreecheck()`.

GeoPoly start:

- `GeoPoly` stores polygon vertex count, 4-byte endian/count header, and coordinate array.
- `GeoParse` tracks JSON polygon parsing state.
- `geopolyParseJson()`, `geopolyFuncParam()`, `geopolyBlobFunc()`, `geopolyJsonFunc()`, `geopolySvgFunc()`, `geopolyXformFunc()`, `geopolyArea()`, `geopolyAreaFunc()`, `geopolyCcwFunc()`, `geopolyRegularFunc()`, and the start of `geopolyBBox()` parse, normalize, transform, render, and summarize polygons.

## Control Flow

JSON function calls generally enter through a registered SQL wrapper, parse the first argument with `jsonParseFuncArg()`, resolve paths with `jsonLookupStep()` when needed, then return via `jsonReturnFromBlob()`, `jsonReturnParse()`, or `jsonReturnString()`. JSON text is converted to JSONB for internal operations. JSONB BLOB input is accepted when `jsonArgIsJsonb()` recognizes it; otherwise BLOBs may fall through to text interpretation for legacy compatibility in parse-oriented functions.

JSON path lookup is recursive. At each path segment, `jsonLookupStep()` verifies the current JSONB node type, scans object label/value pairs or array elements, compares labels with escape-aware logic, and recurses into the selected value. If edit mode is active and the target path exists, it replaces or deletes the matching node. If insert/set mode reaches a missing object key or array append point, it builds needed nested substructure and edits bytes into the parent JSONB blob, then bubbles size changes upward with `jsonAfterEditSizeAdjust()`.

JSON scalar functions are thin wrappers around this machinery. `json_extract()` can return a single SQL value, a JSON value, a JSONB blob, or a JSON array of multiple path results depending on arguments and registration flags. `->` and `->>` support abbreviated PostgreSQL-like path arguments by constructing a temporary path string. `json_valid()` chooses text validation or superficial/strict JSONB validation according to the flags argument. `json_patch()` applies the RFC 7396 merge-patch algorithm recursively over JSONB object entries.

`json_each` and `json_tree` are virtual tables. `xBestIndex` requires an equality constraint on hidden `json` and optionally uses hidden `root`. `xFilter` parses the input, resolves the root, initializes cursor path state, and for nonrecursive `json_each` positions the cursor on direct children of an array/object. `xNext` either advances linearly over siblings or, for `json_tree`, maintains a stack of `JsonParent` frames and path prefixes for depth-first traversal. `xColumn` materializes columns such as `key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, and `path`.

R-Tree scans begin in `rtreeBestIndex()`, which prefers direct rowid lookup unless a `MATCH` constraint is present. Otherwise it builds a compact `idxStr` where each two-byte pair identifies a constraint operator and coordinate index. `rtreeFilter()` decodes that plan, initializes `RtreeConstraint` objects, deserializes callback constraints, seeds the root search point, and calls `rtreeStepToLeaf()`.

`rtreeStepToLeaf()` drives traversal with a small optimized first-point slot plus a heap priority queue. It obtains nodes through `nodeAcquire()`, tests each cell against coordinate or callback constraints, pushes qualifying child nodes or leaf entries with their score and level, and stops when the best point is a leaf row ready for `xRowid`/`xColumn`. Callback constraints can update score and within-state through `sqlite3_rtree_query_info`.

R-Tree writes enter `rtreeUpdate()`. It rejects writes while nodes are referenced by active readers, checks coordinate ordering, handles duplicate rowid conflicts and `REPLACE`, deletes any old row, chooses a leaf, inserts the new cell, writes auxiliary columns, and returns the rowid. Insertions update bounding boxes via `AdjustTree()` or split overfull nodes through the R*-Tree split algorithm in `splitNodeStartree()` and `SplitNode()`. Deletions locate the leaf through `%_rowid`, delete the cell, remove underfull nodes, repair bounding boxes, possibly shorten the root, and reinsert removed node contents.

R-Tree setup in `rtreeInit()` declares the virtual schema, validates dimensions and auxiliary columns, determines node size from page size or the existing root node, creates/opens shadow tables, prepares persistent SQL statements, and loads row estimates from `sqlite_stat1`. `rtreeModule` wires these functions into SQLite's virtual-table API, including `xIntegrity` for integrity checks.

The visible GeoPoly code parses either BLOB polygons or GeoJSON-like text, handles endian conversion, outputs BLOB/JSON/SVG representations, applies affine transforms, computes signed area/winding, constructs regular polygons, and begins bounding-box construction.

## State And Persistence Behavior

JSON state is mostly per-function-call and in-memory. `JsonParse` owns or references JSONB bytes, original JSON text, error/OOM flags, edit deltas, cached reference counts, and insertion payloads. `jsonParseFuncArg()` may insert parsed JSON into SQLite's function-argument cache and use reference-counted strings for original JSON text. Edits mutate `pParse->aBlob` in-place after ensuring it is editable, but persistence only occurs if the SQL caller stores the returned text or BLOB.

JSON aggregate state lives in SQLite aggregate context as a `JsonString`. The final/value routines temporarily append the closing delimiter and either return text or JSONB, trimming the delimiter again for window value calls. `jsonGroupInverse()` mutates the aggregate string buffer to drop the first element for sliding-window frames.

`json_each`/`json_tree` cursor state persists for the duration of a virtual-table scan: parsed JSONB, current blob offset, rowid counter, root path, traversal stack, and path string. Cursor reset/close releases parse buffers, parent arrays, and path storage.

R-Tree state is persistent. User-visible virtual tables are represented by three shadow tables:

- `%_node(nodeno INTEGER PRIMARY KEY, data BLOB)` stores fixed-size big-endian node images.
- `%_parent(nodeno INTEGER PRIMARY KEY, parentnode INTEGER)` maps non-root nodes to parents.
- `%_rowid(rowid INTEGER PRIMARY KEY, nodeno INTEGER, ...)` maps user rowids to leaf nodes and stores auxiliary columns.

In-memory `RtreeNode` objects are reference-counted and cached in `Rtree.aHash`. Dirty nodes are written by `nodeWrite()` when their reference count drops to zero. `Rtree.pNodeBlob` caches an incremental blob handle for reading nodes and is closed at transaction end, savepoint boundaries, cursor teardown when safe, rename, destroy, or on corruption/error paths. `Rtree.nNodeRef` prevents updates while read cursors could be invalidated by rebalancing.

R-Tree mutations update both node images and mapping tables. Root depth is stored in the first two bytes of node 1. Node count, parent maps, rowid maps, and auxiliary values must stay synchronized; `rtreecheck()` and `xIntegrity` validate that relationship.

GeoPoly state is transient except for BLOBs returned by functions or stored in GeoPoly/R-Tree tables. The BLOB header records endian marker and vertex count; polygon coordinates are copied into SQLite-managed result BLOBs.

## Dependencies And Integration Points

- The JSON code depends on SQLite core APIs for SQL values/results, function registration, memory allocation, subtype propagation, UTF-8 decoding, numeric conversion, aggregate/window contexts, and virtual-table APIs.
- JSON behavior is controlled by compile-time flags such as `SQLITE_OMIT_JSON`, `SQLITE_DEBUG`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_LEGACY_JSON_VALID`, and `SQLITE_BUG_COMPATIBLE_20250510`.
- JSONB encoding helpers and constants used here (`JSONB_*`, `jsonbPayloadSize()`, `jsonBlobAppendNode()`, `jsonConvertTextToBlob()`, `jsonbValidityCheck()`, `jsonCacheSearch()`, `jsonCacheInsert()`, `jsonReturnString()`, and related `JsonString` helpers) are defined earlier in the same amalgamated file.
- `sqlite3RegisterJsonFunctions()` integrates with SQLite's builtin function registry via `sqlite3InsertBuiltinFuncs()`. `sqlite3JsonTableFunctions()` integrates with virtual-table module registration through `sqlite3_create_module()`.
- R-Tree depends on the SQLite virtual-table API, prepared statements, incremental blob I/O, schema declaration, transaction/savepoint hooks, `sqlite_stat1`, conflict handling, and shadow-table support.
- R-Tree geometry/query callbacks integrate through `sqlite3_rtree_geometry_callback()`/`sqlite3_rtree_query_callback()` data represented by `RtreeMatchArg` and `sqlite3_rtree_query_info`.
- R-Tree is conditionally compiled when building as extension or with `SQLITE_ENABLE_RTREE` and virtual tables enabled. `SQLITE_RTREE_INT_ONLY`, `SQLITE_ENABLE_GEOPOLY`, endian/compiler intrinsic macros, and mutation/coverage flags alter behavior.
- GeoPoly is intentionally included inside `rtree.c` so it can access R-Tree internals and coordinate types.
- Within this repository, the file is vendored under WiredTiger's SQLite third-party test dependency. Changes affect the embedded SQLite behavior used by that test tree rather than application code written directly in this repository.

## Risks And Edge Cases

- This chunk starts mid-function and spans amalgamated component boundaries. Whole-file research must account for definitions before and after this range.
- JSONB editing is byte-offset sensitive. Incorrect payload-size adjustment, stale `delta`, or a missed `jsonAfterEditSizeAdjust()` can corrupt parent container sizes.
- `jsonBlobOverwrite()` is an optimization that intentionally relies on alternate JSONB header encodings. Mistakes there may preserve total byte count but produce noncanonical or malformed JSONB.
- JSON escape handling has compatibility-sensitive behavior. The `\0` digit-following rule changes under `SQLITE_BUG_COMPATIBLE_20250510`, and escaped newline/U+2028/U+2029 handling affects both parsing and object-label comparison.
- `jsonArgIsJsonb()` deliberately uses weaker validation for larger BLOBs. That is a performance/compatibility tradeoff; malformed internal JSONB may be detected later, produce errors, or in some translation paths produce incorrect JSON text.
- `json_each` path building quotes object labels only with simple alphanumeric checks in the visible code. Labels with embedded quotes or escapes rely on earlier JSONB label representation and path consumers; path rendering should be tested for unusual keys.
- `jsonGroupInverse()` removes the first aggregate element by scanning JSON text for commas outside strings/nesting. It depends on aggregate output being well-formed and on escape skipping being correct.
- R-Tree shadow tables are a consistency boundary. Missing nodes, bad parent maps, stale rowid maps, or corrupt node counts lead to `SQLITE_CORRUPT_VTAB` or integrity-check failures.
- R-Tree node memory management is reference-counted and recursive through parents. Incorrect parent reassignment or failure to detect loops can leak nodes or corrupt traversal; this chunk has explicit loop checks in `fixLeafParent()` and `updateMapping()`.
- Writes are refused while `nNodeRef` is nonzero. Any path that leaks node references can cause persistent `SQLITE_LOCKED_VTAB` on updates.
- R-Tree coordinate comparison has integer/float distinctions and explicit rounding for REAL32 inserts. Boundary tests around float rounding, very large integers, and inclusive/exclusive comparisons are important.
- `rtreeBestIndex()` omits some constraints from VDBE rechecking only for selected operators. Planner behavior and `idxStr` encoding must remain synchronized with `rtreeFilter()`.
- R*-Tree split and condense/reinsert logic is algorithmically dense. Off-by-one errors in minimum-cell counts, root-depth updates, or mapping rewrites can make data silently unreachable.
- GeoPoly parsing requires a closed polygon with at least four coordinates and matching first/last points. The visible code returns `SQLITE_OK` for some invalid BLOB-looking values with `p==0`, which callers interpret as NULL rather than necessarily raising an error.
- The optional GeoPoly BLOB format embeds endian state. Cross-platform tests are needed for byte-swapping and stored BLOB portability.

## Test Signals

- JSON scalar tests should cover `json_extract`, `->`, `->>`, `json_type`, `json_array_length`, `json_pretty`, `json_valid`, `json_error_position`, `json_patch`, `json_set`, `json_insert`, `json_replace`, and `json_remove` over both text JSON and JSONB BLOB input.
- JSON path tests should include quoted object labels, escaped labels, empty labels, array append/count forms (`[#]`, `[#-N]`), missing paths, malformed paths, and nested insert creation.
- JSONB mutation tests should validate returned JSON/JSONB after replacement, deletion of object label/value pairs, array insertion, root replacement, root removal, and repeated edits that change payload sizes.
- JSON compatibility tests should cover JSON5 escapes, surrogate pairs, invalid escape sequences, escaped newlines, `\0` followed by digits with and without the compatibility macro, and legacy BLOB-as-text behavior.
- JSON virtual-table tests should verify `json_each` direct-child output and `json_tree` recursive output for all columns (`key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, `path`, hidden `json`, hidden `root`) with root constraints and malformed input.
- JSON aggregate/window tests should compare `json_group_array`/`json_group_object` and JSONB variants for ordinary aggregate and sliding window frames, including nested strings containing commas and escapes.
- R-Tree query tests should exercise rowid lookup, coordinate constraints for all operators, `MATCH` callbacks, `sqlite3_rtree_query_info` scores, auxiliary column reads, and planner estimates after `ANALYZE`.
- R-Tree write tests should cover insert, update, delete, duplicate rowid with and without `REPLACE`, coordinate-order constraint failures, auto-rowid allocation, auxiliary columns, and update rejection while cursors are active.
- R-Tree structural tests should insert enough rows to force splits, root growth, root shrink after deletes, underfull-node removal, reinsertion, and parent/rowid mapping updates.
- R-Tree corruption/integrity tests should tamper with `%_node`, `%_parent`, and `%_rowid` to ensure `rtreecheck()` and `xIntegrity` report missing nodes, bad mappings, bad cell counts, invalid depth, and coordinate bounds violations.
- R-Tree platform tests should cover big-endian/little-endian serialization paths, REAL32 rounding around representability boundaries, and integer-only builds.
- GeoPoly tests should cover valid/invalid JSON polygons, BLOB endian conversion, `geopoly_blob`, `geopoly_json`, `geopoly_svg`, affine transforms, signed area/winding correction, regular polygon construction limits, and bounding-box behavior as continued after this chunk.
