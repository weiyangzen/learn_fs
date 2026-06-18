<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/loopback.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/loopback.rs

Purpose: URI adapter for exposing an already-existing SPDK bdev under a URI alias without creating a new backing device.

Important APIs/types: `Loopback` stores target bdev name, alias URI, and optional UUID. `TryFrom<&Url>` parses path segments and optional UUID, rejecting unknown params. `Probe` checks the named bdev exists. `create()` looks up the bdev, verifies UUID when provided, adds the alias, and returns the name. `destroy()` removes the alias and dispatches a loopback-removed event.

State and dependencies: mutates bdev alias list and device event dispatcher state. Depends on `UntypedBdev` lookup and `dispatch_loopback_removed`.

Integration points: dispatcher maps both `bdev` and `loopback` schemes here, so tests can use either URI style for existing bdevs.

Risks and test signals: destroy succeeds even if the bdev is absent, only warning. UUID mismatch is detected only on create. Test alias open/close behavior and event listeners that respond to loopback removal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/loopback.rs -->
