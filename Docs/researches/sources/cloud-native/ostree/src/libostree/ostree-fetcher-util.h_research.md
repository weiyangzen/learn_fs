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
