# sources/cloud-native/ostree/src/libostree/ostree-metalink.h

## Purpose
This private header declares the `OstreeMetalink` GObject wrapper and synchronous request API for Metalink resolution. It is hidden from GObject introspection.

## Important APIs, State, and Integration
It defines GObject type macros, `OstreeMetalinkClass`, an autoptr cleanup function, `_ostree_metalink_get_type()`, `_ostree_metalink_new()`, and `_ostree_metalink_request_sync()`. The constructor binds an `OstreeFetcher`, requested filename, max size, metalink URI, and network retry count; the request API returns the selected target URI and/or downloaded bytes.

## Dependencies, Risks, and Tests
The header depends on `ostree-fetcher.h` and GLib/GObject. It integrates with fetch code that can use Metalink metadata as a mirror list and verification envelope. Risks are internal ownership conventions for returned `OstreeFetcherURI` and `GBytes`. Tests should verify constructor/ref cleanup and request output ownership.
