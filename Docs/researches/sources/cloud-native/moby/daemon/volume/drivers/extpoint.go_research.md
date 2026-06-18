# sources/cloud-native/moby/daemon/volume/drivers/extpoint.go

## Purpose
Manages registered volume drivers and dynamically discovered `VolumeDriver` plugins.

## Important APIs, Types, And Functions
`Store` holds an extension map, a global mutex, per-driver `locker.Locker`, and optional `plugingetter.PluginGetter`. Public methods include `Register`, `GetDriver`, `CreateDriver`, `ReleaseDriver`, `GetDriverList`, and `GetAllDrivers`. `makePluginAdapter` builds adapters for v1-client and address-based plugins.

## Control Flow
`lookup` validates the name, serializes lookup by driver name, checks registered extensions, then queries the plugin getter with lookup/acquire/release mode. It adapts the plugin, validates its scope, and releases an acquired reference if validation fails. v1 plugins are cached in `extensions`; newer plugins can be returned without caching. `GetAllDrivers` combines registered drivers with discoverable plugins, skipping duplicates.

## State And Persistence
The store is entirely in-memory. Plugin reference counts are maintained outside the store through `PluginGetter.Get` modes.

## Dependencies And Integration Points
The volume service creates this store, registers the local driver, and uses it for create/get/list/remove flows. It integrates Moby plugin discovery, generated volume proxy adapters, and typed errdefs.

## Risks
Reference count balance is subtle: acquire failures during create must release plugin refs. Holding `s.mu` while adapting plugins in `GetAllDrivers` can make slow plugin calls visible to driver listing. Invalid plugin scopes are rejected or coerced depending on path, so capability validation behavior must remain consistent.

## Test Signals
`extpoint_test.go` checks missing driver errors and successful registered-driver retrieval. Store tests with fake plugins cover create failure dereference behavior.
