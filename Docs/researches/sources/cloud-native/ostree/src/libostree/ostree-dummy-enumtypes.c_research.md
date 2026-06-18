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
