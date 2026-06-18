# sources/distributed-fs/seaweedfs/weed/filer/configuration.go

## Purpose
This file loads SeaweedFS filer store configuration, selects the enabled default store, and configures optional path-specific stores.

## Important APIs, Types, and Functions
- Global `Stores []FilerStore` receives store implementations via backend `init` functions.
- `(*Filer).LoadConfiguration` validates default store selection, instantiates a fresh store of the registered type, initializes it, installs it on the filer, then scans for path-specific store configs.
- `validateOneEnabledStore` enforces at most one default store.

## Control Flow and State
Configuration first checks that only one top-level `<store>.enabled` is true. The first enabled registered store is cloned using reflection, initialized with prefix `<store>.`, and passed to `f.SetStore`. Then all config keys ending in `.enabled` with a dotted `<store>.<id>` prefix are examined. Enabled path-specific configs are cloned, initialized, require a `.location`, and are added through `f.Store.AddPathSpecificStore(location, storeId, store)`.

## State and Persistence Behavior
The file does not persist metadata itself. It determines which persistent backend receives future filer operations and whether path-specific routing is active.

## Dependencies and Integration Points
It uses `util.ViperProxy`, registered `FilerStore` implementations, reflection to create new concrete store instances, and logging/fatal exits for invalid configuration.

## Risks and Edge Cases
- Reflection assumes registered stores are pointers to concrete types and can be `Elem()` cloned.
- Store selection depends on registration order.
- Validation only enforces top-level default stores; path-specific store conflicts are not checked here.
- On missing default or invalid path-specific config, the process exits instead of returning an error.

## Test Signals
Tests should cover single default selection, duplicate default fatal behavior, missing default behavior, path-specific store loading, missing location, and registered store cloning. No local tests are listed.
