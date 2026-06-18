<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/dev.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/dev.rs

Purpose: Central URI dispatcher and generic block-device lookup/open/create/destroy facade for supported bdev schemes.

Important APIs: `uri::parse()` converts a URI into a boxed `BdevCreateDestroy`; `try_parse_or_aio()` falls back to `aio://{uri}` when plain paths are supplied; `parse_url()` dispatches schemes including aio, bdev/loopback, ftl, malloc, null, nvmf variants, pcie, uring, nexus, and lvol. `reject_unknown_parameters()` enforces strict query parsing. Top-level `device_lookup`, `device_name`, `device_create`, `device_destroy`, and `device_open` expose scheme-neutral operations.

Control flow: device lookup/open prefer NVMf (`nvmx`) devices first, then native SPDK bdevs. URI parse errors are converted through `BdevError`.

State and dependencies: creation/destruction delegates state mutation to concrete device modules. Depends on `url`, concrete bdev modules, `SpdkBlockDevice`, and `BlockDevice` traits.

Risks and test signals: adding a new scheme requires implementing traits and updating this dispatcher. Strict unknown-parameter rejection is useful for safety but can break old URIs. Test each scheme parse plus plain-path AIO fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/dev.rs -->
