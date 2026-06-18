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
