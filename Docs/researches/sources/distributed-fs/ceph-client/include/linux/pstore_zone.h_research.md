# sources/distributed-fs/ceph-client/include/linux/pstore_zone.h

Purpose: declares the generic zoned pstore backend abstraction used by block and similar storage devices to expose read/write/erase/panic-write operations over fixed storage regions.

Important APIs and types: operation typedefs define read, write, and erase signatures using buffer, size, and storage-relative offset. `struct pstore_zone_info` carries module owner, backend name, total size, per-frontend zone sizes, max kmsg reason, regular read/write/erase callbacks, and optional `panic_write`. `register_pstore_zone()` and `unregister_pstore_zone()` manage the backend.

Control flow: a zone backend registers total and per-frontend sizes plus callbacks. Pstore/zone uses relative offsets to read/write records, retries on `-EBUSY`, advances zones on `-ENOMSG`, and can call `panic_write()` in panic contexts if provided.

State and persistence: persistent state is in the backing zone storage. Runtime state is the registered zone descriptor and backend device state.

Dependencies and integration points: integrates pstore core/frontends with block-like or MTD-like storage backends. Depends on module ownership and low-level storage drivers.

Risks and test signals: risks include violating required 4 KiB/sector-size multiples, panic-write using unsafe paths, offset arithmetic bugs, and wrong handling of `-EBUSY`/`-ENOMSG`. Test size validation, panic and normal writes, erase, backend removal, and multi-zone rollover.
