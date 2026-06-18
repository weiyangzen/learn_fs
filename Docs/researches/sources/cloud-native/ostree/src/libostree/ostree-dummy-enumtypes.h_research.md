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
