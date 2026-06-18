# Research: subset-b-000243

Grouped research for the OSTree libostree core/deployment/diff/fetcher/GPG files in `sources/cloud-native/ostree/src/libostree`. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core.h -->
# sources/cloud-native/ostree/src/libostree/ostree-core.h

## Purpose
This public header defines core libostree object constants, metadata GVariant formats, repository mode enums, checksum helpers, content stream parsing/checksumming APIs, structural validators, and commit metadata accessors. It is the central ABI contract for object naming, object validation, content serialization, and commit-level metadata used across the repository, pull, checkout, and verification code.

## Important APIs, Types, And Functions
`OstreeObjectType` enumerates file, dirtree, dirmeta, commit, tombstone, commitmeta, payload-link, and split-xattrs object variants; `OSTREE_OBJECT_TYPE_IS_META()` and `OSTREE_OBJECT_TYPE_LAST` define classification/range checks. `OstreeRepoMode` defines storage modes including archive, bare-user, bare-user-only, and bare-split-xattrs. Public helpers convert checksums between hex/base64/raw/GVariant forms, validate revs, remote names, collection IDs, and parse refspecs. Object-name APIs serialize and deserialize `(checksum, type)` pairs. Content APIs parse archive/raw content and create archive-z2/content streams. Checksum APIs cover `GFile`, fd-relative paths, async checksumming, xattr-aware checksumming, and hardlink breaking. `OstreeChecksumFlags` controls xattr and canonical-permission behavior. Structure validators check object variants and file modes. `OstreeCommitSizesEntry` represents entries in `ostree.sizes` metadata.

## Control Flow, State, And Persistence
The header itself has no executable flow, but it codifies persisted on-disk/wire formats: dirmeta/filemeta/tree/commit/summary GVariant signatures, commit metadata keys, SHA256 lengths, and metadata size limits. Consumers must preserve big-endian GVariant fields and stable metadata key semantics because these formats are persisted in OSTree repositories and exchanged over HTTP.

## Dependencies And Integration Points
It depends on GIO/GVariant, `ostree-types.h`, and `struct stat`. It is included by repository, diff, pull, checkout, and verification modules. The `OSTREE_MAX_METADATA_SIZE` value integrates with fetch logic to limit metadata download/storage abuse.

## Risks And Test Signals
ABI and persisted-format stability are the main risks: changing enum values, GVariant strings, checksum sizes, or metadata keys would break repositories and clients. Tests should cover checksum round trips, invalid refs/remotes/collections, object-name serialization, structural validation for malformed variants, mode-specific xattr/canonical-permission checksums, and backwards compatibility for commit size metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-date-utils-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-date-utils-private.h

## Purpose
This private header exposes `_ostree_parse_rfc2616_date_time()` to non-introspection builds. It is used by HTTP fetcher code to parse cache-related `Last-Modified` header values without depending on locale-sensitive parsing.

## Important APIs, Types, And Functions
The single API is `GDateTime *_ostree_parse_rfc2616_date_time (const char *buf, size_t len)`. It returns a UTC `GDateTime` on success and `NULL` on malformed input.

## Control Flow, State, And Persistence
The header holds no state. It constrains call sites to provide an explicit byte length, which matters for parsing HTTP header substrings that may not be independently NUL-terminated or may include stripped CRLF.

## Dependencies And Integration Points
It depends on GLib and is hidden behind `#ifndef __GI_SCANNER__`, signalling internal C-only use. The curl fetcher includes it to convert `Last-Modified` response headers into Unix timestamps returned through fetch completion APIs.

## Risks And Test Signals
The risk is accidental exposure or ABI assumptions around a private helper. Tests should validate that users of this header treat `NULL` as a parse failure and do not dereference the result blindly.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-date-utils-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-date-utils.c -->
# sources/cloud-native/ostree/src/libostree/ostree-date-utils.c

## Purpose
This file implements a strict, locale-independent parser for the RFC 2616/RFC 1123 HTTP date form used in cache validators, for example `Wed, 21 Oct 2015 07:28:00 GMT`.

## Important APIs, Types, And Functions
`parse_uint()` parses exactly two or four ASCII decimal digits within a caller-specified range and rejects overflow, partial parses, and non-digits. `_ostree_parse_rfc2616_date_time()` validates fixed length `29`, checks day and month names against static English arrays, validates separators and timezone `GMT`, parses numeric fields, allows second `60` for leap seconds, and returns `g_date_time_new_utc()`.

## Control Flow, State, And Persistence
The parser is positional and fail-fast: every delimiter, token, and numeric range is checked before constructing the timestamp. It deliberately does not verify that the weekday matches the date. No state is persisted; successful parses are returned as UTC timestamps for fetch metadata.

## Dependencies And Integration Points
It uses GLib character/date APIs, `errno`, and `strncmp`. It integrates with HTTP fetcher implementations, especially curl’s `response_header_cb()`, to populate `out_last_modified`.

## Risks And Test Signals
Strict format support means valid HTTP-date alternatives from RFC 2616, such as RFC 850 or asctime forms, are rejected. Leap-second handling depends on GLib accepting second `60`; callers handle a `NULL` return as timestamp `0`. Tests should cover exact valid strings, bad length, invalid month/day tokens, bad timezone, range failures, nonmatching weekday acceptance, leap second behavior, and malformed separators.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-date-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-deployment-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-deployment-private.h

## Purpose
This private header defines the full `OstreeDeployment` instance layout and internal helpers that are not part of the public deployment API. It represents one bootable deployment in a sysroot.

## Important APIs, Types, And Functions
`struct _OstreeDeployment` stores GObject base state plus bootloader index, stateroot/osname, commit checksum, deploy serial, boot checksum, boot serial, `OstreeBootconfigParser`, origin `GKeyFile`, unlocked/staged/finalization/soft-reboot state, overlay initrd checksums and derived ID, and cached device/inode identity. Internal functions include `_ostree_deployment_set_bootcsum()`, `_ostree_deployment_set_overlay_initrds()`, `_ostree_deployment_get_overlay_initrds()`, and `_ostree_deployment_get_kargs()`.

## Control Flow, State, And Persistence
The structure mirrors persistent sysroot state: deployment paths, `.origin` keyfiles, bootloader config, and boot artifacts under `/boot/ostree`. The dev/inode cache is process-local and used to compare deployment backing identity.

## Dependencies And Integration Points
It includes `ostree-deployment.h` and is used by deployment/sysroot/admin code that needs mutation beyond the public getters/setters.

## Risks And Test Signals
Because this exposes private layout to sibling C files, field changes can break assumptions in sysroot code. Overlay initrd ID generation currently concatenates checksums, so tests should cover ordering and collision-sensitive comparison behavior. Tests should also cover staged/finalization/soft-reboot flag propagation and kargs parsing from bootconfig.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-deployment-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-deployment.c -->
# sources/cloud-native/ostree/src/libostree/ostree-deployment.c

## Purpose
This file implements the `OstreeDeployment` GObject: creation, cloning, identity/equality, origin management, bootconfig ownership, transient-origin cleanup, overlay initrd tracking, and public state queries.

## Important APIs, Types, And Functions
The GObject is declared with `G_DEFINE_TYPE`. Getters expose checksum, boot checksum, osname, deploy serial, boot serial, bootconfig, origin, and index. Setters mutate index, boot serial, bootconfig, origin, and internal boot checksum/overlay initrds. `ostree_deployment_new()` validates required fields and initializes identity. `ostree_deployment_clone()` deep-copies bootconfig, origin keyfile data, overlay initrds, and cached dev/inode. `ostree_deployment_hash()` and `ostree_deployment_equal()` use osname, commit checksum, and deploy serial. `ostree_deployment_origin_remove_transient_state()` removes the transient group plus legacy transient keys. `_ostree_deployment_get_kargs()` parses bootconfig `options` into `OstreeKernelArgs`.

## Control Flow, State, And Persistence
The object owns string fields, bootconfig object references, and a refcounted `GKeyFile` origin. Cloning serializes and reloads the origin to avoid shared mutable keyfile state. `ostree_deployment_get_origin_relpath()` derives the persistent `.origin` path from osname, checksum, and deploy serial. Finalization frees all owned state.

## Dependencies And Integration Points
It depends on bootconfig parsing, kernel args parsing, GLib/GObject, and otutil helpers. Sysroot code constructs deployments from on-disk state, compares them for bootloader writes, and uses transient-origin cleanup during upgrades.

## Risks And Test Signals
Equality ignores boot checksum, boot serial, origin, staged flags, and overlay initrds; code needing full boot equivalence must compare additional fields. `ostree_deployment_set_bootserial()` is public but documented as historical API not to use. Tests should cover clone independence, origin transient removal, origin relpath formatting, hash/equality consistency, overlay initrd ID behavior, and lifecycle cleanup under valgrind/asan.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-deployment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-deployment.h -->
# sources/cloud-native/ostree/src/libostree/ostree-deployment.h

## Purpose
This public header declares the `OstreeDeployment` type and stable API for inspecting and lightly mutating deployments in a sysroot.

## Important APIs, Types, And Functions
It defines GType/check macros, `OSTREE_ORIGIN_TRANSIENT_GROUP`, the opaque `OstreeDeployment`, constructors, hash/equality helpers, getters for index/osname/checksums/serials/bootconfig/origin, state queries for staged/finalization-locked/soft-reboot/pinned, setters for index/bootserial/bootconfig/origin, transient origin cleanup, clone, origin relpath, and `OstreeDeploymentUnlockedState` with string conversion.

## Control Flow, State, And Persistence
The header’s public contract maps deployment identity to persistent sysroot layout. The origin transient group documents state that should not be carried across upgrades, while `.origin` relpaths are derived from deployment identity.

## Dependencies And Integration Points
It depends on `ostree-bootconfig-parser.h` and `ostree-types.h`. It is consumed by admin, sysroot, upgrader, bootloader, and bindings code.

## Risks And Test Signals
Public API additions must preserve ABI. State-query semantics evolve with features such as staged deployments and soft reboot, so tests should verify behavior with older origin/bootconfig data. Binding/introspection tests should confirm transfer annotations, nullability, and enum stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-deployment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-diff.c -->
# sources/cloud-native/ostree/src/libostree/ostree-diff.c

## Purpose
This file implements directory diffing for OSTree trees and filesystem directories, producing modified, removed, and added arrays plus a simple printer.

## Important APIs, Types, And Functions
`get_file_checksum()` uses repo-file checksums directly for `OstreeRepoFile` inputs or computes xattr-aware file checksums from `GFileInfo`, optional xattrs, and regular-file streams. `OstreeDiffItem` is a boxed refcounted struct with source/target files, infos, and checksums. `diff_files()` compares file checksums. `diff_add_dir_recurse()` records all descendants of an added directory. `ostree_diff_dirs()` delegates to `ostree_diff_dirs_with_options()`. The options variant supports owner UID/GID overrides for target-side info. `ostree_diff_print()` prints `M`, `D`, and `A` lines relative to base paths.

## Control Flow, State, And Persistence
The main diff first adjusts flags if either repo disables xattrs or uses bare-user-only mode. If the source tree is `NULL`, the entire target tree is added. For repo-file directories, matching dirtree content checksums provide a fast path. Otherwise it enumerates source children to detect removals/modifications and recurses into matching directories, then enumerates target children to detect additions. State is in caller-owned `GPtrArray`s and boxed diff items.

## Dependencies And Integration Points
It depends on GLib/GIO, libglnx xattr helpers, repo-private `OstreeRepoFile` APIs, and core checksum functions. CLI/admin code can use the result arrays or printer.

## Risks And Test Signals
The algorithm performs two directory enumerations and checksum reads, so large trees and xattr-heavy filesystems are expensive. `devino_to_csum_cache` exists in the ABI-sized options struct but is unused here. Tests should cover repo fast-path equality, xattr-ignore behavior, type changes, owner remapping, added directory recursion, missing-file errors versus real I/O errors, symlinks, and stable ABI size of `OstreeDiffDirsOptions`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-diff.h -->
# sources/cloud-native/ostree/src/libostree/ostree-diff.h

## Purpose
This public header declares OSTree directory diff APIs and the boxed `OstreeDiffItem` result type.

## Important APIs, Types, And Functions
`OstreeDiffFlags` currently supports `OSTREE_DIFF_FLAGS_IGNORE_XATTRS`. `OstreeDiffItem` contains atomic refcount, source/target `GFile`s, source/target `GFileInfo`s, and optional checksums. Ref/unref and GType functions make it usable from GLib containers/bindings. `ostree_diff_dirs()` and `ostree_diff_dirs_with_options()` fill modified/removed/added arrays. `OstreeDiffDirsOptions` contains owner remap fields plus reserved booleans, ints, and pointers for ABI extension; `OSTREE_DIFF_DIRS_OPTIONS_INIT` sets UID/GID to `-1`. `ostree_diff_print()` emits a human-readable summary.

## Control Flow, State, And Persistence
The header defines caller ownership expectations: arrays are supplied by the caller and receive object references or owned diff items. No persistent state is created.

## Dependencies And Integration Points
It includes core and type headers and references `OstreeRepoDevInoCache`. It is consumed by C users, CLI code, and introspection-visible APIs.

## Risks And Test Signals
Because the options struct is ABI-extensible, initialization discipline matters. Tests should ensure callers using `OSTREE_DIFF_DIRS_OPTIONS_INIT` avoid uninitialized owner fields, boxed type ref/unref works, and introspection sees correct element types.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-diff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-dummy-enumtypes.c -->
# sources/cloud-native/ostree/src/libostree/ostree-dummy-enumtypes.c

## Purpose
This compatibility source exports a stub enum-type function solely to pacify ABI checkers for an enum type that should not be practically used.

## Important APIs, Types, And Functions
`ostree_fetcher_config_flags_get_type()` returns `G_TYPE_INVALID`.

## Control Flow, State, And Persistence
There is no state or persistence. The function is intentionally inert.

## Dependencies And Integration Points
It includes `ostree-dummy-enumtypes.h` and GLib object typing through that header. The symbol exists for backwards compatibility and ABI tooling.

## Risks And Test Signals
Any runtime code depending on this symbol as a real enum GType will fail because it returns `G_TYPE_INVALID`. Tests should treat the symbol as ABI-only: verify it exports where expected but do not use it for actual type registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-dummy-enumtypes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-dummy-enumtypes.h -->
# sources/cloud-native/ostree/src/libostree/ostree-dummy-enumtypes.h

## Purpose
This header declares the ABI-only dummy enumtype function for non-introspection builds.

## Important APIs, Types, And Functions
It declares `_OSTREE_PUBLIC GType ostree_fetcher_config_flags_get_type (void)` behind `#ifndef __GI_SCANNER__`.

## Control Flow, State, And Persistence
No control flow or state is present. The header is a compatibility declaration.

## Dependencies And Integration Points
It depends on `glib-object.h` and is paired with `ostree-dummy-enumtypes.c`.

## Risks And Test Signals
The main risk is confusing this stub with generated enumtype support. Build and ABI tests should confirm the symbol is available where legacy ABI expects it while introspection ignores it.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-dummy-enumtypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-curl.c -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher-curl.c

## Purpose
This file implements the internal `OstreeFetcher` backend using libcurl multi/easy APIs integrated with GLib `GMainContext`, supporting HTTP/HTTPS/file fetches to memory or tmpfiles.

## Important APIs, Types, And Functions
`struct OstreeFetcher` stores config flags, remote/proxy/TLS/cookie/header/user-agent settings, tmpdir fd, libcurl multi handle, timer/socket sources, outstanding `GTask`s, socket table, and byte count. `FetcherRequest` tracks mirror list, filename, request/cache headers, size limits, tmpfile/memory buffer, response ETag/Last-Modified, curl easy handle, and write errors. `_ostree_fetcher_new()` constructs the GObject. Setters configure proxy, TLS DB, client cert/key including pkcs11 handling, cookies, extra headers, user agent, low-speed thresholds, retry-all, HTTP2 disable, and outstanding request count. `_ostree_fetcher_request_to_tmpfile()` and `_ostree_fetcher_request_to_membuf()` share `_ostree_fetcher_request_async()`. Finish functions transfer `GLnxTmpfile` or `GBytes`.

## Control Flow, State, And Persistence
Requests bind to one thread-default main context at a time. `initiate_next_curl_request()` creates/configures an easy handle, attaches request headers, auth, protocol restrictions, HTTP2 settings, callbacks, and adds it to the multi handle. `sock_cb()`, `event_cb()`, and `timer_cb()` drive `curl_multi_socket_action()`. `check_multi_info()` handles completions, maps curl/HTTP errors to `G_IO_ERROR`, logs failures, advances to the next mirror when possible, returns memory/tmpfile results, and clears main context when no requests remain. Tmpfiles are created lazily and rewound before transfer.

## Dependencies And Integration Points
It depends on libcurl, GLib Unix sources, libglnx tmpfile/write helpers, fetcher util, date parsing, enumtypes, and repo-private config. Pull and remote code use the common fetcher API without selecting this backend directly.

## Risks And Test Signals
Risks include single-main-context assertions, callback behavior during finalization, max-size enforcement, mirror fallback differences, HTTP2/libcurl version behavior, and security of protocol/TLS options. Tests should cover HTTP 304, ETag/Last-Modified parsing, optional 404 suppression at util level, file URI not found, max-size failure, retry-all mapping, TLS permissive/client cert/proxy/cookie settings, multiple mirrors, bytes-transferred accounting, and cancellation/finalization with outstanding sockets.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-curl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup.c -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup.c

## Purpose
This file implements the internal fetcher backend using libsoup2. It maintains a dedicated session thread and exposes the same async memory/tmpfile request surface as the curl backend.

## Important APIs, Types, And Functions
`ThreadClosure` owns the session thread state: `SoupSession`, main context, remote name, tmpdir fd, extra headers, transfer-gzip flag, outstanding requests, active output stream set, total downloaded bytes, and OOB proxy auth error. `OstreeFetcherPendingURI` stores mirror state, request object, cache validators, output stream/tmpfile/memory state, size limits, and response metadata. Setters enqueue session-thread callbacks for proxy, cookie jar, TLS interaction/database, extra headers, user agent, and max connections. Low-speed and retry-all setters are TODO stubs.

## Control Flow, State, And Persistence
Construction creates a private `GMainContext` and session thread, then initializes a `SoupSession` in that thread. Public request APIs create a `GTask`, attach a pending request, and schedule `session_thread_request_uri()`. That builds a `SoupRequest`, adds conditional headers and extra headers, starts async send, handles HTTP status and mirror fallback in `on_request_sent()`, then reads the stream in 8192-byte chunks through `on_stream_read()` and `on_out_splice_complete()`. Output streams are created lazily and tracked for byte accounting. Finalization stops the thread and joins it.

## Dependencies And Integration Points
It depends on libsoup2 unstable request APIs, GIO Unix streams, libglnx, TLS cert interaction when available, fetcher util, and repo-private helpers. It shares `OstreeFetcher` ABI with the other backends.

## Risks And Test Signals
The private thread model adds synchronization and lifecycle risk; proxy auth OOB errors can override final HTTP errors. Low-speed/retry-all configuration is not implemented here, unlike curl. Tests should cover thread shutdown, proxy credentials, TLS DB initialization errors, cookie jar and headers, mirror fallback, optional content, incomplete downloads via content length, NUL termination, memory/tmpfile transfer, file descriptor usage, and bytes-transferred during active downloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup3.c -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup3.c

## Purpose
This file implements the fetcher backend using libsoup3. Compared with libsoup2, it avoids a dedicated session thread and instead keeps a `SoupSession` per caller `GMainContext`.

## Important APIs, Types, And Functions
`FetcherRequest` stores mirror/file/message/session/main-context state, output mode, cache validators, response metadata, size counters, and tmpfile/memory streams. `struct OstreeFetcher` stores remote name, tmpdir fd, force-anonymous flag, main-context-to-session hash, proxy resolver, cookie jar, TLS interaction/database, extra headers, user agent, byte count, and max outstanding request setting. Setters configure proxy, cookies, client certs, TLS database, extra headers, user agent, and max connections; low-speed/retry-all remain TODO stubs.

## Control Flow, State, And Persistence
`create_request_message()` creates either a `GFile` for `file://` URIs or a `SoupMessage` for HTTP, attaches conditional headers, TLS permissive acceptance, and extra headers. `_ostree_fetcher_request_async()` selects or creates a session for the current thread-default main context, weakly removes sessions when finalized, creates a `GTask`, and calls `initiate_task_request()`. Completion handles `GFile` or Soup response streams, HTTP 304, mirror fallback, ETag/Last-Modified, content length, then chunked async reading and splicing to tmpfile or memory. Finish functions transfer the tmpfile or bytes.

## Dependencies And Integration Points
It depends on libsoup3, GIO, libglnx, fetcher util, URI helpers, and TLS cert interaction. The common fetcher header lets pull code use this backend interchangeably with curl/libsoup2.

## Risks And Test Signals
Session-per-main-context storage uses a hash with weak refs and shared configuration snapshots; changes after a session is created may not update existing sessions. Low-speed/retry-all are not implemented. Content length is ignored when content encoding is present. Tests should cover file URI handling, session reuse/removal across contexts, TLS permissive acceptance, proxy resolver, cookie jar, extra headers, ETag/Last-Modified parsing via soup date APIs, mirror fallback, max-size errors, incomplete tmpfile detection, and bytes-transferred accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-uri.c -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher-uri.c

## Purpose
This file wraps GLib `GUri` as `OstreeFetcherURI`, providing parse, clone, path manipulation, stringification, and scheme validation for fetcher backends.

## Important APIs, Types, And Functions
`_ostree_fetcher_uri_free()` unrefs the underlying `GUri`. `_ostree_fetcher_uri_parse()` parses encoded URIs with password support and scheme normalization; for older GLib it manually normalizes default ports. `_ostree_fetcher_uri_new_path_internal()` creates a new URI by replacing or extending the path while preserving user, password, host, port, query, fragment, and flags. Public internal helpers expose clone, new path, new subpath, scheme/path string copies, hidden-password URI string, and `_ostree_fetcher_uri_validate()`.

## Control Flow, State, And Persistence
The wrapper is immutable in practice: path operations return new `GUri` instances. Validation accepts only `http`, `https`, and `file`, intentionally rejecting protocols libcurl might otherwise support.

## Dependencies And Integration Points
It depends on GLib `GUri`, libglnx error helpers, and `ostree-fetcher.h`. All fetcher backends consume these URIs for mirror lists and request construction.

## Risks And Test Signals
Manual default-port normalization in the older-GLib branch appears to rebuild with scheme `"http"` for accepted default ports, which deserves compatibility scrutiny. `g_build_filename()` is used for URI paths, so tests should cover slash behavior and encoded path preservation. Validate accepted/rejected schemes, password hiding, query/fragment preservation, and file URI behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-uri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.c -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.c

## Purpose
This file provides synchronous and retrying helpers around the asynchronous fetcher API, plus HTTP failure journald logging and status-to-`GIOErrorEnum` mapping.

## Important APIs, Types, And Functions
`FetchUriSyncData` captures async completion state for a private main context. `fetch_uri_sync_on_complete()` calls the async finish function and wakes the context. `_ostree_fetcher_mirrored_request_to_membuf_once()` runs one async memory request synchronously, handles optional-content 404 as success with `NULL`, and transfers ETag/Last-Modified/not-modified outputs. `_ostree_fetcher_mirrored_request_to_membuf()` loops with retry classification. `_ostree_fetcher_request_uri_to_membuf()` wraps a single URI into a mirror list. `_ostree_fetcher_journal_failure()` emits structured systemd journal messages. `_ostree_fetcher_should_retry_request()` identifies transient errors. `_ostree_fetcher_http_status_code_to_io_error()` maps HTTP statuses.

## Control Flow, State, And Persistence
The sync helper pushes a new thread-default `GMainContext`, starts the fetch, iterates until completion, then pops and cleans state. Retry count is decremented by the caller loop. Journald output persists operational failure records when systemd support is enabled through otutil.

## Dependencies And Integration Points
It depends on GIO Unix output streams, optional systemd journal APIs, fetcher util header, and otutil. Repository pull/summary code uses these helpers for metadata fetches where synchronous control flow is simpler.

## Risks And Test Signals
The retry loop uses unsigned decrement in the condition, so tests should verify zero and nonzero retry counts. Optional content only suppresses not-found errors. Tests should cover transient classifications, HTTP mappings with retry-all, cancellation before request, out-argument cleanup on failure, journald skip for local/no-remote cases, and not-modified metadata propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.h -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.h

## Purpose
This private header declares utility functions shared by fetcher callers and backends and defines the default OSTree user-agent string.

## Important APIs, Types, And Functions
`OSTREE_FETCHER_USERAGENT_STRING` expands to `PACKAGE_NAME "/" PACKAGE_VERSION`. `_ostree_fetcher_tmpf()` creates a linkable tmpfile under a directory fd and chmods it `0644`. It declares mirrored/single-URI synchronous memory fetch helpers, journald failure logging, retry decision logic, and HTTP status mapping.

## Control Flow, State, And Persistence
The inline tmpfile helper creates filesystem state in the caller-supplied temp directory and returns a `GLnxTmpfile` for later linking or cleanup. Other declarations describe helpers implemented in `ostree-fetcher-util.c`.

## Dependencies And Integration Points
It includes `ostree-fetcher.h`, libglnx tmpfile helpers through that path, and is hidden from GI scanner. Fetcher backends use the user-agent and tmpfile helper; pull code uses the sync fetch helpers.

## Risks And Test Signals
Tmpfile permission and linkability are security-sensitive. Tests should validate tmpfile mode, cleanup/ownership transfer, and user-agent formatting. ABI is private, but backend parity depends on these declarations staying consistent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher.h -->
# sources/cloud-native/ostree/src/libostree/ostree-fetcher.h

## Purpose
This private header defines the common `OstreeFetcher` GObject API implemented by curl, libsoup2, and libsoup3 backends, plus the `OstreeFetcherURI` abstraction.

## Important APIs, Types, And Functions
It defines type macros and `OstreeFetcherClass`, `OstreeFetcherConfigFlags` (`TLS_PERMISSIVE`, `TRANSFER_GZIP`, `DISABLE_HTTP2`), and `OstreeFetcherRequestFlags` (`NUL_TERMINATION`, `OPTIONAL_CONTENT`, `LINKABLE`). URI helpers parse/clone/modify/get/validate URIs. Fetcher construction takes a tmpdir fd, remote name, and config flags. Setters cover anonymous tmpfiles, cookie jar, proxy, client cert, low-speed, retry-all, max outstanding requests, TLS database, extra headers, and user agent. Async APIs fetch to tmpfile or memory with cache validators, max size, priority, cancellable, and finish metadata outputs. `_ostree_fetcher_bytes_transferred()` reports progress.

## Control Flow, State, And Persistence
The header defines asynchronous request contracts but no implementation. Tmpfile requests return ownership through `GLnxTmpfile`; memory requests return `GBytes`. Cache validators and response metadata support HTTP conditional fetch persistence in higher layers.

## Dependencies And Integration Points
It depends on libglnx and GLib/GObject/GIO types. Pull, summary, and remote code integrate through this header while the build selects a backend implementation.

## Risks And Test Signals
Backend parity is the biggest risk: some setters are TODO in soup backends while implemented in curl. Tests should run common fetcher behavior against each configured backend, including request flags, output ownership, cancellation, ETag/Last-Modified, TLS/proxy/cookie/header settings, and byte accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-fetcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.c -->
# sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.c

## Purpose
This file implements `OstreeGpgVerifier`, the internal trusted-keyring manager and detached-signature verifier built on GPGME.

## Important APIs, Types, And Functions
`struct OstreeGpgVerifier` stores keyring `GFile`s, in-memory keyring data, and ASCII key file paths. Class init calls `gpgme_check_version()`. `_ostree_gpg_verifier_import_keys()` concatenates binary keyrings/data into a temporary `pubring.gpg`, then enables armor and imports ASCII keys with GPGME. `_ostree_gpg_verifier_list_keys()` builds a temporary GPG home, imports keys, and returns selected or all keys. `_ostree_gpg_verifier_check_signature()` creates an `OstreeGpgVerifyResult`, creates/imports into its temporary GPG home, wraps `GBytes` as GPGME data without copying, runs `gpgme_op_verify()`, refs the verify result details, and weak-ref hooks cleanup to result finalization. Add APIs support keyring files, keyring data, ASCII files, keyfile paths/dirs, keyring dirs, and global trusted keyring dir.

## Control Flow, State, And Persistence
Verification state is intentionally scoped to a temporary GPG home. On success, that temporary directory persists until the result object is finalized so later result inspection can resolve signing keys. On failure, the result and temporary directory are cleaned up. Global keyring defaults to `OSTREE_GPG_HOME` or `DATADIR/ostree/trusted.gpg.d/`.

## Dependencies And Integration Points
It depends on GPGME, ot-gpg-utils, libglnx, GLib/GIO, and the private result layout. Repository summary/commit verification code configures verifier keyrings and consumes `OstreeGpgVerifyResult`.

## Risks And Test Signals
Temporary home lifecycle and GPG agent cleanup are sensitive. Missing keyring files are ignored in one path but directory/open errors propagate elsewhere. Directory import filters only regular `.gpg` files excluding trustdb/secring. Tests should cover binary and ASCII key imports, global keyring env override, list-by-id and list-all, detached signature success/failure, missing/revoked/expired keys, tempdir cleanup on result finalize and error, cancellation, and directory traversal limitations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.h -->
# sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.h

## Purpose
This private header declares the `OstreeGpgVerifier` GObject and its key-loading/signature-verification API.

## Important APIs, Types, And Functions
It defines type macros, an opaque `OstreeGpgVerifier`, autoptr cleanup, `_ostree_gpg_verifier_new()`, `_ostree_gpg_verifier_check_signature()`, `_ostree_gpg_verifier_list_keys()`, keyring dir/file/data adders, global keyring import, ASCII key adders, and keyfile path/dir adders.

## Control Flow, State, And Persistence
The header defines verifier ownership contracts: key inputs are accumulated on the verifier object, and signature checks return an `OstreeGpgVerifyResult` tied to verifier-imported temporary key state.

## Dependencies And Integration Points
It includes `ostree-gpg-verify-result.h` and is used by repository verification internals, not public GI consumers.

## Risks And Test Signals
Because this is private but security-critical, tests should verify all declared import paths feed equivalent trust state and that errors are surfaced through `GError`. Header/API parity with `ostree-gpg-verifier.c` should be covered by build tests across GPG-enabled configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-dummy.c -->
# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-dummy.c

## Purpose
This file provides ABI-compatible dummy `OstreeGpgVerifyResult` functions for builds compiled with GPGME support disabled.

## Important APIs, Types, And Functions
It defines a minimal `OstreeGpgVerifyResult` GObject implementing `GInitable` without real initialization. Public result APIs log critical messages and return empty/false/NULL values. `ostree_gpg_verify_result_require_valid_signature()` returns `G_IO_ERROR_NOT_SUPPORTED`. `ostree_gpg_verify_result_describe_variant()` validates the expected full-result tuple type and appends a disabled-feature message if called with a valid variant. It also defines the `OstreeGpgError` quark.

## Control Flow, State, And Persistence
There is no verification state. The dummy implementation preserves symbols so callers can link, but any real GPG inspection fails explicitly at runtime.

## Dependencies And Integration Points
It includes public `ostree-gpg-verify-result.h` and must only compile when `OSTREE_DISABLE_GPGME` is defined. It substitutes for the real result implementation in no-GPG builds.

## Risks And Test Signals
Callers must handle disabled GPG as unsupported, not as a valid signature absence unless that is intended. `ostree_gpg_verify_result_describe()` calls `get_all()` after logging, which returns `NULL`; downstream `describe_variant()` has `g_return_if_fail`. Tests should cover no-GPG build behavior, error code from `require_valid_signature()`, critical logging expectations, and symbol availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-private.h

## Purpose
This private header exposes the real `OstreeGpgVerifyResult` instance layout to GPG verifier/result implementation files.

## Important APIs, Types, And Functions
`struct OstreeGpgVerifyResult` contains a GObject parent, `gpgme_ctx_t context`, and `gpgme_verify_result_t details`.

## Control Flow, State, And Persistence
The stored GPGME context owns key lookup state and is tied to the temporary GPG home created by the verifier. The `details` pointer holds verification result data refcounted from GPGME.

## Dependencies And Integration Points
It includes `ostree-gpg-verify-result.h` and `otutil.h`, which supplies GPGME-related cleanup macros/utilities. It is consumed by `ostree-gpg-verifier.c` and `ostree-gpg-verify-result.c`.

## Risks And Test Signals
The context and details lifetimes must remain aligned: freeing the temporary home too early breaks key detail lookup, while failing to release GPGME refs leaks resources. Tests should cover result finalization, repeated attribute queries after verification, and error cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.c -->
# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.c

## Purpose
This file implements public inspection and reporting APIs for GPG detached-signature verification results.

## Important APIs, Types, And Functions
`signature_is_valid()` treats GPGME `VALID`, `GREEN`, or status-ok/no-summary signatures as valid. `signing_key_is_revoked()` works around GPGME revoked-key reporting. The GObject implements `GInitable` to allocate a GPGME context and finalizes by releasing context/details. `ostree_gpg_verify_result_count_all()` and `_count_valid()` walk `details->signatures`. `ostree_gpg_verify_result_lookup()` canonicalizes a key ID via GPGME and compares primary key fingerprints. `ostree_gpg_verify_result_get()` builds a tuple for requested `OstreeGpgSignatureAttr`s, including validity, expiry/revocation/missing flags, fingerprints, timestamps, algorithm names, user ID fields, and key expiry fields. `get_all()` uses a synchronized attribute list. `describe()` and `describe_variant()` format human-readable status. `require_valid_signature()` enforces at least one valid signature and maps the last failed signature to `OstreeGpgError`.

## Control Flow, State, And Persistence
Attribute extraction walks a selected signature, lazily looks up the signing key only for key-dependent fields, and returns a floating `GVariant` tuple. Description validates the exact all-attributes tuple type `(bbbbbsxxsssssxx)`. Error construction for invalid results iterates signatures newest-last-to-first and strips trailing newlines.

## Dependencies And Integration Points
It depends on GPGME, GLib/GObject/GVariant, libglnx, and the private result layout. Repository verification APIs return these objects to callers who need either boolean acceptance or detailed diagnostics.

## Risks And Test Signals
Signature validity policy is security-critical and intentionally includes “valid with caveats” and “not certified but cryptographically OK” cases. Tuple order must stay synchronized with the enum. Tests should cover valid, bad, missing-key, revoked, expired-key, expired-signature, subkey versus primary fingerprint lookup, unknown algorithm fallbacks, invalid timestamps, `require_valid_signature()` error-code selection, and backwards-compatible tuple type/order.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.c -->
