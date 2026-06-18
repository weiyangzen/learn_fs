# subset-b-007910 Research

Grouped research for Tahoe-LAFS web resources under `sources/distributed-fs/tahoe-lafs/src/allmydata/web`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/check_results.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/check_results.py

## Purpose
Renders check, verify, repair, deep-check, and deep-check-and-repair results for the Tahoe-LAFS WebAPI. It converts `ICheckResults` and `ICheckAndRepairResults` objects into HTML template elements or JSON, and it lets deep operation result pages drill into per-storage-index details through the `/operations/<handle>/<storage-index>` child path.

## Important APIs, Types, And Functions
The JSON helpers are `json_check_counts`, `json_check_results`, and `json_check_and_repair_results`. `ResultsBase` provides shared HTML rendering for share counts, corrupt shares, share maps, and permuted server order. `LiteralCheckResultsRenderer`, `CheckResultsRenderer`, and `CheckAndRepairResultsRenderer` are `MultiFormatResource` adapters for literal files, normal checks, and repair checks. `DeepCheckResultsRenderer` and `DeepCheckAndRepairResultsRenderer` wrap monitor-backed long-running results; their element classes render counters, corrupt-share tables, object lists, and reload/cancel controls inherited from `ReloadMixin`.

## Control Flow
Callers in `filenode.py` and `directory.py` run node `check`, `check_and_repair`, `start_deep_check`, or `start_deep_check_and_repair`, then instantiate one of these renderers. `MultiFormatResource` dispatches `output=json` to JSON renderers and otherwise renders Twisted templates such as `check-results.xhtml`, `check-and-repair-results.xhtml`, `deep-check-results.xhtml`, and `deep-check-and-repair-results.xhtml`. Deep renderers read counters and object maps from `monitor.get_status()`. Their `getChild` decodes the child segment as base32 storage index, looks up the per-object result in the monitor status, and returns a single-object renderer or a `WebError` for unknown storage indexes.

## State And Persistence
The module owns no persistent storage. Renderers keep references to the client, a result object, or a monitor. Long-lived state is in the monitor registered by `operations.OphandleTable`; this file only reads it. Generated JSON includes storage indexes, summaries, health/recoverability, share counts, server long names, corrupt share coordinates, operation completion state, and stats from result objects.

## Dependencies And Integration Points
This module depends on Twisted Web templates, `allmydata.interfaces.ICheckResults` and `ICheckAndRepairResults`, `allmydata.util.base32`, `dictutil.DictOfSets`, Tahoe JSON byte support, and shared web helpers from `common.py`. It is directly integrated by file and directory POST `t=check`, deep-check operation handles, streaming deep-check output in `directory.py`, and the `MoreInfo` check forms in `info.py`. It also uses the client storage broker to present share placement in permuted server order.

## Risks And Test Signals
Important risks are drift between result-interface methods and JSON field names, HTML escaping around paths/summaries/server names, and incomplete deep-repair rendering: `post_repair_corrupt_shares` is explicitly unimplemented and deep check-and-repair JSON sets `count-corrupt-shares-post-repair` from the pre-repair counter. Literal files are handled by `None` results and need separate coverage. Useful test signals exist in `src/allmydata/test/test_checker.py`, `test_deepcheck.py`, and WebAPI integration tests for `start-deep-check`, JSON output, per-SI child resources, repair summaries, and corrupt-share tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/check_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/common.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/common.py

## Purpose
Provides the shared WebAPI utility layer for Tahoe-LAFS Twisted resources. It normalizes request argument handling, format selection, exception-to-HTTP conversion, asynchronous render completion, common text/time/size formatting, child traversal error wrapping, static-resource installation, and private-key parsing for mutable object creation.

## Important APIs, Types, And Functions
`WebError` carries user-facing HTTP errors. Request parsing helpers include `get_arg`, `boolean_of_arg`, `parse_replace_arg`, `get_format`, `get_mutable_type`, `parse_offset_arg`, `get_root`, `should_create_intermediate_directories`, and `get_keypair`. Metadata and JSON helpers include `get_filenode_metadata` and `convert_children_json`. `humanize_exception` and `humanize_failure` map Tahoe domain exceptions to status codes. `exception_to_child` and `render_exception` wrap Twisted `getChild` and render methods with Eliot actions, deferred handling, cancellation, and error pages. `MultiFormatResource` dispatches renderers by query argument. `SlotsSequenceElement` is the local sequence-rendering helper used by many templates.

## Control Flow
Most resources call `get_arg` to merge query args and multipart form fields, then either return a value directly or rely on `@render_exception` to process Deferreds, resources, URLs, bytes, strings, `NOT_DONE_YET`, and failures. `_finish` is the central response finisher: failures are humanized or converted to traceback/error pages, resources are rendered, text is encoded, `DecodedURL` values become redirects, and cancellation after connection loss is ignored. `exception_to_child` similarly wraps traversal methods in `DeferredResource`, mapping exceptions into `ErrorPage` responses.

## State And Persistence
The module has no application persistence. It manages temporary package-resource extraction for static files through an `ExitStack` finalized with the root resource. It also parses request-local RSA private keys from a URL-safe base64 `private-key` argument to support deterministic mutable file/directory creation. Request mutation is limited to response headers, status codes, and cancellation of pending Deferreds when clients disconnect.

## Dependencies And Integration Points
It depends on Twisted Web, Twisted Deferreds, Eliot logging, Hyperlink URLs, importlib package resources, Tahoe interfaces/exceptions, mutable version constants, encoding utilities, and RSA key creation. Nearly every other module in this group imports it. `get_arg` imports `TahoeLAFSRequest` lazily to avoid a circular import with `webish`. `add_static_children` is used by both client and introducer roots to serve packaged static assets.

## Risks And Test Signals
Because this module is a cross-cutting compatibility layer, regressions affect almost every WebAPI endpoint. Risk areas include bytes/str boundary handling in `get_arg`, `url_for_string`, and format dispatch; non-JSON-safe output from `convert_children_json`; request double-finish if resources are not consistently decorated; information exposure from unhandled failures when `Accept` permits HTML traceback; and permissive `when_done` redirects. Test signals include `src/allmydata/test/web/test_common.py`, broad `test_web.py` endpoint coverage, tests for exception mapping, multipart/query precedence, `MultiFormatResource` format errors, cancellation behavior, static assets, and private-key argument handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/directory.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/directory.py

## Purpose
Implements WebAPI handling for Tahoe directory nodes, including traversal, dynamic handler selection, directory listing, HTML forms, child creation/replacement, uploads into directories, URI attachment, unlink/rename/relink, shallow and deep checks, manifest/deep-size/deep-stats operations, streaming JSON-lines traversal, and unknown-node metadata.

## Important APIs, Types, And Functions
`make_handler_for` chooses `FileNodeHandler`, `DirectoryNodeHandler`, or `UnknownNodeHandler` based on Tahoe node interfaces. `DirectoryNodeHandler` is the main `Resource`, with `getChild`, `render_GET`, `render_PUT`, `render_POST`, and many `_POST_*` helpers. `DirectoryAsHTML`, `RenameForm`, `ManifestElement`, `ManifestResults`, `DeepSizeResults`, and `DeepStatsResults` are presentation resources/elements. `ManifestStreamer` and `DeepCheckStreamer` implement `IPushProducer` over `dirnode.DeepStats`. Helpers `_directory_json_metadata`, `_directory_uri`, `_directory_readonly_uri`, `_slashify_path`, `_cap_to_link`, `abbreviated_dirnode`, and `UnknownJSONMetadata` support representations.

## Control Flow
Traversal first rejects empty path components, fetches children asynchronously, and, for write requests, may create intermediate directories or a placeholder leaf. `GET` without `t` renders `DirectoryAsHTML`; `t=json`, `info`, `uri`, `readonly-uri`, and `rename-form` return alternate resources. `PUT t=mkdir` completes traversal-created directories, while `PUT t=uri` replaces the current directory link. `POST` dispatches by `t`: creating directories, uploading form files through a child/placeholder handler, setting child caps, deleting links, moving links, running checks, starting monitor-backed deep operations through `OphandleTable`, streaming manifest/check JSON lines directly to the request, and setting a full children map from JSON.

## State And Persistence
The handler stores `client`, current `node`, optional `parentnode`/`name`, and the client's operation table. Durable changes are delegated to directory nodes: `create_subdirectory`, `set_uri`, `delete`, `move_child_to`, `set_children`, immutable/mutable directory creation, and uploads that create child file nodes. Operation state is held by `Monitor` instances registered under operation handles. Streaming producers keep request and monitor references and cancel the monitor when the HTTP producer is stopped.

## Dependencies And Integration Points
This file integrates Twisted Web, Tahoe directory/file interfaces, URI parsing, blacklist/prohibited nodes, monitor cancellation, mutable version constants, `filenode.ReplaceMeMixin` and file handlers, check result renderers, `MoreInfo`, operation reload behavior, and shared helpers from `common.py`. It is reached under `/uri/<dircap>/...` and supplies the directory half of the user-facing WebAPI. Templates include `directory.xhtml`, `rename-form.xhtml`, `manifest.xhtml`, and deep operation result templates through `check_results.py`.

## Risks And Test Signals
High-risk areas are traversal-time mutation, empty-path validation, replace semantics including `replace=only-files`, slash handling in child names, body parsing for children JSON, and streaming producers that ignore backpressure pause while honoring stop/cancel. HTML rendering assumes `_get_children` succeeds before template renderers read `self.dirnode_children`. Unknown-node and prohibited-node metadata must avoid capability confusion. Tests should exercise `src/allmydata/test/web/test_web.py`, `test_grid.py`, `test_deepcheck.py`, path auto-creation, upload forms, mkdir variants, set-children JSON, relink across directories, operation-handle requirements, stream-manifest/deep-check cancellation, and immutable/read-only directory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/directory.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/filenode.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/filenode.py

## Purpose
Implements WebAPI resources for file nodes and placeholder leaf nodes. It handles file downloads, metadata/capability views, immutable replacement, mutable overwrite/update, form uploads, child-cap replacement, checks/repairs, deletion from a parent directory, byte-range GET/HEAD responses, and JSON metadata generation.

## Important APIs, Types, And Functions
`ReplaceMeMixin` contains shared replacement helpers: `replace_me_with_a_child`, `replace_me_with_a_childcap`, and `replace_me_with_a_formpost`. `PlaceHolderNodeHandler` handles writes to a not-yet-existing child. `FileNodeHandler` handles existing files with `getChild`, `render_GET`, `render_HEAD`, `render_PUT`, `render_POST`, `render_DELETE`, `replace_my_contents`, `update_my_contents`, and form overwrite helpers. `FileDownloader` parses Range headers and streams file bytes. `_file_json_metadata`, `_file_uri`, `_file_read_only_uri`, and `FileNodeDownloadHandler` support alternate routes and `/file/<cap>/...` downloads.

## Control Flow
Directory traversal returns a placeholder when a leaf does not exist but a PUT/upload can create it. Replacement chooses immutable CHK upload through `FileHandle` and `parentnode.add_file` or mutable SDMF/MDMF creation through `MutableFileHandle` and `client.create_mutable_file`, optionally using `get_keypair`. Existing file `GET` without `t` obtains the best readable version and returns a `FileDownloader`; `GET t=json` may refresh mutable servermap before reading edge metadata; `t=info`, `uri`, and `readonly-uri` return specialized resources or text. PUT to mutable files overwrites or updates at a nonnegative offset, while PUT to immutable files replaces the parent link. POST supports check and multipart upload. Download rendering sets content type, content disposition, range headers, content length, and delegates streaming to `filenode.read`.

## State And Persistence
Handlers retain client, node, parentnode, and name. Persistent effects are all delegated to Tahoe nodes and parent directories: uploads create immutable files, mutable files are created or overwritten, mutable versions can be updated at an offset, child links can be set or deleted, and check/repair can add leases. Download state is request-local; `FileDownloader` holds the readable filenode/version and filename. ETags are emitted for immutable fixed outputs based on storage index and output type.

## Dependencies And Integration Points
The module depends on Twisted HTTP/static resources, Tahoe upload and mutable publish handles, mutable read mode, blacklist/prohibited-node wrappers, monitor checks, check result renderers, `MoreInfo`, and shared argument/error helpers. It is used by `directory.make_handler_for`, `/file` via `root.FileHandler`, and directory upload delegation. Its metadata shape feeds WebAPI clients expecting `filenode` JSON tuples with caps, verify caps, mutability, format, size, and edge metadata.

## Risks And Test Signals
Risk areas include Range parsing edge cases, single-range-only behavior, lack of Content-Range support for PUT, offset parsing raising raw `ValueError`, readonly mutable replacement rejection, bytes/str handling for filenames and content-disposition, and weak error signaling after streaming has already started. `replace` is parsed as `only-files` in PUT but as boolean for some POST paths. Test signals include WebAPI upload/download tests in `src/allmydata/test/web/test_web.py`, range GET/HEAD coverage, mutable overwrite/update tests, JSON metadata tests, prohibited-node behavior, ETag behavior for immutable files, and check/repair rendering through `test_checker.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/filenode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/info.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/info.py

## Purpose
Renders the `t=info` page for files, directories, and unknown nodes. It exposes node type, storage index, size, write/read/verify capabilities, raw download links, check forms, mutable overwrite forms, and directory deep-operation forms.

## Important APIs, Types, And Functions
`MoreInfo` is a `MultiFormatResource` whose HTML and `t=info` renderers flatten `MoreInfoElement`. `MoreInfoElement` provides renderers for title/header/type/storage index, size, directory caps, file caps, raw links, checkability, check form, mutable overwrite form, directory-only deep-check/deep-size/deep-stats/manifest forms, and helper methods `abbrev`, `get_type`, and `get_root`.

## Control Flow
File and directory handlers return `MoreInfo(self.node)` for `GET t=info`. The element class determines node kind through `IDirectoryNode` and `IFileNode`, then fills sections conditionally. Size is asynchronous via `node.get_current_size()` and treats `UnrecoverableFileError` as unknown size. Forms post back to `/uri/<cap>` or the current directory URL with `t=check`, `t=upload`, `t=start-deep-check`, `t=start-deep-size`, `t=start-deep-stats`, or `t=start-manifest`; operation handles are generated from random bytes encoded with base32.

## State And Persistence
The resource stores only the original node. It does not mutate state itself, but it exposes write caps and generates forms that can trigger repair, lease renewal, overwrite, and long-running directory operations. The generated operation handles are request-local random values; resulting operation state is managed by `operations.py` after form submission.

## Dependencies And Integration Points
This module depends on Twisted templates, Tahoe file/directory interfaces, `MDMF_VERSION`, base32, URL quoting, `UnrecoverableFileError`, and the shared `MultiFormatResource`. It integrates with `filenode.py`, `directory.py`, `root.py` routes under `/uri`, and templates in `info.xhtml`. The raw-link generation uses the `/file/<cap>/@@named=/raw.txt` route to avoid directory-context capability exposure.

## Risks And Test Signals
The page intentionally displays capabilities, so access control relies on the surrounding WebAPI threat model. Several renderers reach into `node._node` for directory-backed file caps, making wrapper internals part of this presentation path. Bytes returned from `base32.b2a`/cap methods must flatten correctly in Twisted templates. Tests should cover `t=info` for immutable, mutable, MDMF/SDMF, readonly, LIT, directory, and unknown nodes; size failure handling; form target construction; and integration with deep-operation WebAPI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/introweb.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/introweb.py

## Purpose
Defines the web root for an introducer node. It renders a human-readable introducer status page and a JSON summary of subscriber and announcement counts, plus static web assets.

## Important APIs, Types, And Functions
`IntroducerRoot` is the `MultiFormatResource` root. It stores the introducer node/service, installs itself as the empty child, adds static children, and renders HTML or JSON. `IntroducerRootElement` fills `introducer.xhtml` with node metadata and sequence rows for announcements and subscribers. Renderers include `node_data`, `announcement_summary`, `client_summary`, `services`, and `subscribers`.

## Control Flow
Construction fetches the service named `introducer` from the node. HTML rendering builds an `IntroducerRootElement`; JSON rendering iterates `get_subscribers()` and `get_announcements()` to count by `service_name`. Template renderers sort announcements by service name/nickname, format subscriber/announcement timestamps with `render_time`, and produce `SlotsSequenceElement` rows.

## State And Persistence
The module owns no durable state. It reads live introducer service state: announcements, subscribers, connection hints, versions, nicknames, tub IDs, and timestamps. It records a node data dict for the duration of one element instance, including rendered time, node ID, Tahoe version, and import path.

## Dependencies And Integration Points
It depends on Twisted templates, `allmydata.__full_version__`, `idlib`, Tahoe JSON byte dumping, and shared web helpers. It is used as the root resource for introducer nodes rather than client nodes, complementing `root.py`. Tests exist in `src/allmydata/test/test_introducer.py` and `src/allmydata/test/web/test_introducer.py`.

## Risks And Test Signals
Risks are mostly representation drift: bytes/str flattening for server IDs, service-name sorting, and JSON counts matching HTML summaries. The root attaches static children, so packaging-resource behavior from `common.add_static_children` matters. Useful tests verify HTML renderability, JSON count fields, empty subscriber/announcement lists, static children, and realistic introducer service fake objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/introweb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/logs.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/logs.py

## Purpose
Creates the authenticated private log-streaming WebSocket resource under `/private/logs/v1`. While a WebSocket is open, it forwards Eliot log messages as JSON frames.

## Important APIs, Types, And Functions
`TokenAuthenticatedWebSocketServerProtocol` subclasses Autobahn's Twisted `WebSocketServerProtocol` and implements `onConnect`, `_received_eliot_log`, `onOpen`, and `onClose`. `create_log_streaming_resource` builds a `WebSocketResource` with that protocol. `create_log_resources` builds a Twisted `Resource` with child `v1`.

## Control Flow
The private resource tree in `private.py` enforces the Tahoe auth-token HTTP scheme before this resource is reached. Once the WebSocket opens, `onOpen` registers `_received_eliot_log` as an Eliot destination. Every Eliot message is encoded with `json.dumps_bytes(..., any_bytes=True)` and sent as a WebSocket message. `onClose` removes the destination and tolerates `ValueError` if it was already removed.

## State And Persistence
There is no persisted state. Active state is one Eliot destination callback per open WebSocket connection. Log messages are transient and sent to clients as they arrive.

## Dependencies And Integration Points
The module depends on Autobahn Twisted WebSocket resources, Eliot, Twisted `Resource`, and Tahoe JSON bytes support. It is intentionally placed behind the authenticated private tree created in `private.py`. Test coverage is in `src/allmydata/test/web/test_logs.py`.

## Risks And Test Signals
The protocol class name mentions token authentication, but this module itself does not inspect headers; security depends on `/private` wrapping. `_received_eliot_log` has no send-error handling, so broken connections or serialization issues can affect destination cleanup. Test signals include successful child lookup at `/private/logs/v1`, WebSocket frame emission for Eliot messages, destination removal on close, and authentication tests in `test_private.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/logs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/operations.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/operations.py

## Purpose
Maintains in-memory operation handles for long-running WebAPI jobs such as deep checks, manifests, and deep stats. It exposes `/operations/<ophandle>` resources, supports cancellation, retention timers, release-after-complete, and reload/cancel template helpers.

## Important APIs, Types, And Functions
`OphandleTable` is both a Twisted `Resource` and `service.Service`. It stores `(monitor, renderer, when_added)` tuples in `handles` and delayed calls in `timers`. Key methods are `add_monitor`, `_operation_complete`, `redirect_to`, `getChild`, `_set_timer`, `_release_ophandle`, and `stopService`. `ReloadMixin` provides `refresh` and `reload` renderers for monitor-backed result elements.

## Control Flow
Directory operations require an `ophandle` argument before calling `add_monitor`. The table records the monitor/renderer, optionally schedules `retain-for`, and attaches `_operation_complete` to `monitor.when_done()`. `redirect_to` constructs `/operations/<handle>` and preserves `output`. Later `getChild` validates the handle, processes `POST t=cancel`, optionally refreshes timers, releases handles after complete if requested, converts monitor `Failure` status to a failed Deferred, and otherwise returns the renderer. Completed handles without explicit retention are retained first as uncollected and then as collected after a GET.

## State And Persistence
All state is process-local and lost on node restart. Default retention constants are four days for uncollected handles and one day after collection. Timers use an injected clock for tests or the global Twisted reactor. Cancellation delegates to the monitor. No filesystem or database persistence is used.

## Dependencies And Integration Points
It depends on Twisted resources, services, Deferreds, reactor timers, URLPath, Hyperlink URLs, and shared `get_arg`/`WebError`/`boolean_of_arg` helpers. `directory.py` registers monitor-backed renderers here; `check_results.py` and `directory.py` elements use `ReloadMixin` to present reload/cancel affordances.

## Risks And Test Signals
Risks include unbounded handle growth if timers are not set or cancelled correctly, byte/string mismatches for handle keys, invalid `retain-for` values raising raw conversion errors, race behavior when a handle is cancelled/released while being fetched, and process-local loss of operation status. Tests should use deterministic clocks for timer expiry, cover cancellation, release-after-complete, unknown handles, `Failure` monitor status, redirect URL construction, and directory operations that require `ophandle`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/operations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/private.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/private.py

## Purpose
Builds the authenticated `/private` resource tree for node-local private WebAPI features. It implements a custom Tahoe-LAFS HTTP authorization scheme based on the node's `api_auth_token`, currently protecting the private log-streaming subtree.

## Important APIs, Types, And Functions
`IToken` is the credentials interface. `Token` stores the proposed token and compares it with `timing_safe_compare`. `TokenChecker` validates credentials against `get_auth_token`. `TokenCredentialFactory` defines scheme `tahoe-lafs` and decodes authorization bytes. `PrivateRealm` returns the protected resource root for `IResource`. `_create_vulnerable_tree` installs `logs`, `_create_private_tree` wraps it in `HTTPAuthSessionWrapper`, and `create_private_tree` is the public constructor.

## Control Flow
`root.Root` calls `create_private_tree(client.get_auth_token)` and mounts the result at `/private`. Twisted Web guard parses the `Authorization` header using `TokenCredentialFactory`, passes a `Token` to `TokenChecker`, and, on success, asks `PrivateRealm` for the wrapped resource. The vulnerable tree is only reachable through this wrapper and currently exposes `logs/v1`.

## State And Persistence
The module stores no durable state. `TokenChecker` holds a callable used to fetch the current auth token on each login attempt. `Token` instances hold request-local proposed tokens. The protected tree holds child resources such as log streaming.

## Dependencies And Integration Points
It depends on `attrs`, Zope interfaces, Twisted cred/guard/resource interfaces, Tahoe timing-safe comparison and precondition helpers, and `logs.create_log_resources`. It integrates directly with `root.py` and indirectly with `logs.py` for private WebSocket access. Tests are in `src/allmydata/test/web/test_private.py` and `test_logs.py`.

## Risks And Test Signals
Security depends on correct Twisted credential parsing and constant-time token comparison. The token is accepted as raw bytes after the `tahoe-lafs` scheme, so tests should include missing, wrong, and correct Authorization headers. `_create_vulnerable_tree` is deliberately named to show it must remain wrapped. Useful test signals include scheme challenge, unauthorized login failures, successful resource traversal, no accidental exposure of `/private/logs` through the public root, and token type preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/private.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/root.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/root.py

## Purpose
Defines the main client-node web root and top-level WebAPI routing. It mounts capability, file-download, status, statistics, incident-reporting, private, and static resources, renders the welcome page, and emits a JSON summary of introducer and storage-server connectivity.

## Important APIs, Types, And Functions
`URIHandler` handles `/uri` and `/cap` creation, redirect, and capability traversal. `FileHandler` handles `/file` and `/named` download-only file-cap paths. `IncidentReporter` records user-triggered incidents. `Root` installs children and renders HTML/JSON. `RootElement` fills `welcome.xhtml` with node identity, introducer/helper/storage status, service rows, incident form, version, import path, and render time. Helpers include `_describe_known_servers`, `_describe_server`, `_describe_server_and_connection`, and `_describe_connection_status`.

## Control Flow
`Root.__init__` mounts `/uri`, `/cap`, `/private`, `/file`, `/named`, `/status`, `/statistics`, `/report_incident`, and static assets. Dynamic `getChild` returns helper and storage status resources because those services may attach after root construction. `/uri` GET with `uri=<cap>` validates and redirects to `/uri/<cap>` preserving other query args; PUT/POST without a child create unlinked files or directories via `unlinked.py`; child traversal parses a cap and delegates to `directory.make_handler_for`. `/file/<filecap>/...` only permits GET/HEAD and returns a download handler. Root JSON describes introducer connection summaries and known storage servers.

## State And Persistence
The root stores the client and optional time provider. Persistent effects are delegated: unlinked uploads create grid objects, incident reports go through Tahoe logging, and private routes expose live log streams. The root itself does not persist state. Welcome rendering reads live service state from storage, helper, uploader, introducer connection statuses, and storage broker.

## Dependencies And Integration Points
This is the central integration point for `filenode.py`, `directory.py`, `unlinked.py`, `status.py`, `storage.py`, `private.py`, `common.add_static_children`, Tahoe URI parsing, and client service APIs. It depends on Twisted resources/templates and Hyperlink URL handling. Test coverage is in `src/allmydata/test/web/test_root.py`, `test_web.py`, `test_grid.py`, `test_private.py`, `test_status.py`, and broader system tests.

## Risks And Test Signals
Risk areas include capability parsing and URL quoting for `/uri?uri=...` redirects, ensuring `/file` rejects directory caps and non-GET/HEAD methods, delayed storage/helper service lookup, exposing private resources only through auth wrapping, and bytes/str handling in version/server JSON. Test signals include root HTML renderability, JSON schema, top-level child routing, `/uri` upload/mkdir variants, `/file` download route behavior, helper/storage dynamic pages, incident POST method restriction, and reverse-proxy-sensitive URL generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/root.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/status.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/status.py

## Purpose
Renders operation status pages and machine-readable status/statistics for uploads, downloads, mutable publishes/retrieves, servermap updates, helper state, and node counters. It also produces download event JSON for frontend timing visualizations and OpenMetrics output for statistics scraping.

## Important APIs, Types, And Functions
`UploadResultsRendererMixin` renders upload result timings, rates, shares, and server maps. Page/element pairs include `UploadStatusPage`/`UploadStatusElement`, `DownloadStatusPage`/`DownloadStatusElement`, `RetrieveStatusPage`/`RetrieveStatusElement`, `PublishStatusPage`/`PublishStatusElement`, and `MapupdateStatusPage`/`MapupdateStatusElement`. `_EventJson`, `_find_overlap`, `_find_overlap_requests`, and `_color` support download event visualization. `marshal_json`, `Status`, and `StatusElement` summarize active/recent operations. `HelperStatus`, `HelperStatusElement`, `Statistics`, and `StatisticsElement` render helper and stats pages; `Statistics.render_OPENMETRICS` emits OpenMetrics text.

## Control Flow
`Status.render_HTML` builds active/recent operation lists from the history object; `render_JSON` serializes them with `marshal_json`. `Status.getChild` parses paths like `up-1`, `down-2`, `publish-3`, `retrieve-4`, and `mapupdate-5`, then searches the corresponding history lists for a matching counter and returns the detail page. Detail elements read status objects synchronously or with Deferred upload results. Download status installs child `event_json` for timeline data. `Statistics` dispatches `t=openmetrics` through `MultiFormatResource` and mangles Tahoe stat names into metric identifiers/quantile labels.

## State And Persistence
This module owns no durable state. It reads live and recent operation status objects from a history provider, helper stats from the helper service, and counters/stats from a stats provider. `_EventJson` and detail elements hold references to status objects. The only transformation state is request-local rows, colors, and JSON dicts.

## Dependencies And Integration Points
It depends on Twisted templates/resources, Tahoe status interfaces (`IUploadStatus`, `IDownloadStatus`, `IPublishStatus`, `IRetrieveStatus`, `IServermapUpdaterStatus`), base32/idlib/json utilities, and formatting helpers from `common.py`. It is mounted by `root.Root` at `/status`, `/statistics`, and dynamic `/helper_status`; `unlinked.UploadResultsElement` reuses `UploadResultsRendererMixin`. Tests include `src/allmydata/test/web/test_status.py`, `test_openmetrics.py`, `test_statistics.py`, `test_storage_web.py` for adjacent stats patterns, and WebAPI integration coverage.

## Risks And Test Signals
Risks include many loosely typed status-object method assumptions, bytes/str mismatches in storage-index rendering, `Status.getChild` returning `None` for unknown counters instead of an explicit error resource, download result renderers depending on `get_results()` despite a comment noting it is unimplemented, and OpenMetrics name mangling that may not cover all metric characters. Tests should cover active/recent sorting, all detail child types, upload result Deferreds, event JSON shape and row allocation, helper absent/present states, OpenMetrics content type and EOF, NaN handling for `None`, and status JSON fields for all interface types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/status.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage.py

## Purpose
Renders the local storage-server status page and JSON status document. It reports disk usage, accepting-shares state, bucket-counter progress, lease-expiration configuration, current and last lease-checker cycle results, corrupt shares discovered by crawlers, and storage nickname/node ID.

## Important APIs, Types, And Functions
`remove_prefix` is a small string helper. `StorageStatusElement` is the main template element with renderers for nickname, node ID, disk stats, accepting state, crawler status, storage-running condition, lease expiration mode/progress/results, and `format_recovered`. `StorageStatus` is a `MultiFormatResource` that renders HTML with `StorageStatusElement` or JSON with stats, bucket-counter state, lease-checker state, and lease-checker progress.

## Control Flow
`root.Root.getChild("storage")` fetches the storage service dynamically and returns `StorageStatus`. HTML rendering reads `storage.get_stats()` repeatedly for disk fields, reads `bucket_counter.get_state()`/`get_progress()`, and reads `lease_checker.get_state()`/`get_progress()` to format current and historical cycle summaries. JSON rendering serializes the same major state objects. Formatting helpers convert byte counts and timings into display strings.

## State And Persistence
The module stores only the storage service reference and nickname. It reads persistent storage-server crawler/lease-checker state but does not mutate it. If the storage server is absent, `StorageStatusElement.storage_running` renders a no-storage message; many other renderers assume `_storage` is not `None` and are therefore template-flow dependent.

## Dependencies And Integration Points
It depends on Twisted templates, Tahoe time/id/json utilities, `abbreviate_space`, and `common.abbreviate_time`/`MultiFormatResource`. It integrates with the storage service API, bucket counter, lease checker, and root dynamic `/storage` child. Tests are concentrated in `src/allmydata/test/test_storage_web.py`.

## Risks And Test Signals
Risks include template renderers dereferencing `_storage` when no storage server is running, assumptions about detailed lease-checker state keys, stale or partial crawler state, and content-type `text/plain` for JSON. Test signals should cover storage absent/present paths, all disk stat fields including `None`, accepting immutable shares, bucket counter progress states, lease expiration modes (`age`, `cutoff-date`), current-cycle and last-cycle summaries, corrupt share lists, and JSON serialization of stats/crawler state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage_plugins.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage_plugins.py

## Purpose
Provides a parent Twisted resource for web resources contributed by enabled storage client plugins. It dispatches child path segments to plugin-provided resources by name.

## Important APIs, Types, And Functions
`StoragePlugins` is the only class. It stores the Tahoe client and implements `getChild(segment, request)`, using `client.get_client_storage_plugin_web_resources()` to retrieve a mapping from plugin names to `IResource` objects.

## Control Flow
On child traversal, the segment is decoded as UTF-8 and used as a key into the plugin resource mapping. If found, the resource is cached with `putChild(segment, result)` and returned. If not found, `NoResource()` is returned.

## State And Persistence
The resource holds only the client reference and Twisted child-resource cache entries created by `putChild`. It does not persist plugin state or modify plugin configuration.

## Dependencies And Integration Points
It depends on Twisted `Resource`/`NoResource` and the client method `get_client_storage_plugin_web_resources`. It is a narrow extension point for Tahoe storage plugins that expose web UI/API resources.

## Risks And Test Signals
Risks include UTF-8 decode failures for arbitrary path bytes, stale cached child resources if the plugin resource mapping changes after first access, and name collisions between plugins. Tests should cover known plugin child lookup, unknown child lookup, non-ASCII plugin names if supported, and whether dynamic plugin enable/disable behavior is expected to reflect after caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage_plugins.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/unlinked.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/web/unlinked.py

## Purpose
Implements `/uri` operations that create Tahoe objects without linking them into an existing directory. It supports PUT/POST uploads of immutable CHK and mutable SDMF/MDMF files, mutable directories, directories with initial children, immutable directories, upload-result pages, and optional redirects.

## Important APIs, Types, And Functions
Creation helpers are `PUTUnlinkedCHK`, `PUTUnlinkedSSK`, `PUTUnlinkedCreateDirectory`, `POSTUnlinkedCHK`, `POSTUnlinkedSSK`, `POSTUnlinkedCreateDirectory`, `POSTUnlinkedCreateDirectoryWithChildren`, and `POSTUnlinkedCreateImmutableDirectory`. `UploadResultsPage` and `UploadResultsElement` render multipart CHK upload results and reuse `status.UploadResultsRendererMixin` for share/timing details.

## Control Flow
`root.URIHandler` dispatches PUT/POST `/uri` requests here after parsing `format`/`mutable`. PUT reads from `req.content`; POST reads multipart `req.fields["file"].file` for uploads or request body JSON for directory children. CHK uploads call `client.upload(FileHandle(...))`; mutable uploads call `client.create_mutable_file(MutableFileHandle(...))`; directory creation calls `client.create_dirnode` or `client.create_immutable_dirnode`. `when_done` on CHK multipart upload can redirect to a URL after substituting `%(uri)s`; `redirect_to_result=true` on directory creation sends a 303 to `uri/<newcap>`.

## State And Persistence
The module does not keep local state. Persistent effects are new Tahoe objects on the grid: immutable files, mutable files, mutable directories, and immutable directories. Optional `private-key` arguments are parsed via `get_keypair` for deterministic mutable object keypairs. Upload result resources hold an in-memory upload result object only long enough to render the response.

## Dependencies And Integration Points
It depends on Twisted HTTP/templates/resources, Tahoe `FileHandle` and `MutableFileHandle`, common helpers for format parsing, children JSON conversion, redirects, keypair parsing, and status upload-result rendering. It is reached exclusively through `root.URIHandler` for top-level `/uri` creation operations.

## Risks And Test Signals
Risks include multipart field assumptions (`file` must exist), content-type heuristics for distinguishing `t=mkdir` from `t=mkdir-with-children`, URL quoting and open redirect behavior through `when_done`, bytes/str substitution for `%(uri)s`, rejecting `format=CHK` for directories, and inconsistent use of `unique_keypair` between PUT/POST mutable file creation. Tests should cover all `/uri` PUT/POST creation variants, `format` and `mutable` combinations, bad children JSON/body rejection, redirect behavior, upload-result rendering, private-key handling, and resulting capability usability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/web/unlinked.py -->
