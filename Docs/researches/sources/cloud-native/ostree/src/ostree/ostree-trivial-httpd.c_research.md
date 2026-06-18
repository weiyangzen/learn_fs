<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ostree-trivial-httpd.c -->
# sources/cloud-native/ostree/src/ostree/ostree-trivial-httpd.c

## Purpose
Implements `ostree-trivial-httpd`, a small libsoup-based static file server used primarily for OSTree tests and local repository serving.

## Important APIs and Types
Options support daemonization, auto-exit, port/port-file, log-file, forced range behavior, random 500/408 fault injection with caps, expected cookies, expected headers, and fixed test basic auth. `OtTrivialHttpd` stores root dir fd, running flag, and log stream. Key functions include `httpd_log`, `get_directory_listing`, `is_safe_to_access`, `calculate_etag`, `_server_cookies_from_request`, `do_get`, `httpd_callback`, `basic_auth_callback`, `on_dir_changed`, `run`, and `main`.

## Control Flow
`main` sets locale/prgname and calls `run`. `run` parses options, opens the root directory, optionally forks with parent/child readiness pipe, configures logging and libsoup server, writes the selected port, installs auth and request handlers, optionally monitors the root for deletion, then iterates the main context until stopped. Requests route through `httpd_callback` to `do_get` for GET/HEAD. `do_get` validates expected cookies/headers, rejects traversal, injects configured random failures, stats relative to the root fd, serves directory listings or index files, mmaps regular files, emits cache headers/ETags, handles range checks, and supports forced short responses for range retry tests.

## State and Persistence
Persistent effects include optional log-file creation, optional port-file writing, and serving file bytes from the opened root. Daemon mode changes process/session state and redirects stdio. Auto-exit monitors filesystem deletion events. Fault-injection counters are process-global.

## Dependencies and Integration Points
Depends on libsoup 2/3 compatibility shims, GIO Unix streams, libglnx fd helpers, signals, sockets, prctl, and OSTree utility formatting. It integrates with OSTree tests that exercise pull, cache validation, auth, retry, range, and HTTP error paths.

## Risks
Although permission checks require world-readable files and world-executable directories, this is still a simple server and not a hardened production daemon. Path traversal filtering only checks `"../"` before stripping leading slashes. Forced range behavior deliberately lies about content length and closes sockets. Daemon readiness relies on pipe status correctness. Cookie parsing assumes `KEY=VALUE` strings and uses assertions for malformed expected headers.

## Test Signals
Tests should cover GET/HEAD, directory redirects/listings/index.html, forbidden permissions, traversal attempts, ETag and If-None-Match/If-Modified-Since, range errors, forced ranges on objects, random 500/408 caps, expected cookie/header failures, basic auth, daemon port-file readiness, and auto-exit on root deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ostree-trivial-httpd.c -->
