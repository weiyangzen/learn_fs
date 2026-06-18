<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/ftl.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/ftl.rs

Purpose: URI-backed implementation for SPDK FTL bdevs layered over base and cache bdevs.

Important APIs/types: `Ftl` stores name, alias, optional UUID, base bdev URI, and cache bdev URI. `TryFrom<&Url>` parses `uuid`, percent-decodes required `bbdev` and `cbdev` query parameters, and rejects unknowns. `Probe` recursively probes both nested URIs. `ftl_bdev_init_fn_cb()` bridges SPDK FTL init callback into a oneshot. `CreateDestroy::create()` creates nested base/cache bdevs, fills `spdk_ftl_conf`, calls `bdev_ftl_create_bdev`, waits for callback, sets UUID/alias, and returns the device name. `destroy()` deletes the FTL bdev and then destroys cache/base children.

Control flow: cache creation failure cleans up base. Immediate FTL create failure cleans both. Destroy records base-destroy result but still tries cache destroy.

State and dependencies: mutates multiple SPDK bdevs and FTL state. Depends on percent-encoded nested URIs, libspdk FTL APIs, and bdev API create/destroy.

Risks and test signals: nested URI encoding is fragile. Success requires callback delivery after initial zero return. Test create failure cleanup, destroy order, alias/UUID assignment, and recursive probe diagnostics.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/ftl.rs -->
