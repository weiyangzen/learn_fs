<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/lvs.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/lvs.rs

Purpose: URI-backed test/benchmark support for creating an LVS pool and an lvol in one bdev URI.

Important APIs/types: `Lvol` stores lvol name, size, and an `Lvs` spec. `Lvs` stores pool name, backing disk URI, mode, and optional encryption key. `TryFrom<&Url>` parses `lvol:///$name?size=...&lvs=...&disk=...`; nested `Lvs::try_from` parses pool `disk` and `mode`. `LvsMode` supports create, import, create_import, and purge. `CreateDestroy::create()` creates/imports the pool, destroys any existing lvol of the same name, and creates a new lvol. `destroy()` destroys the lvol and pool.

Control flow: purge wipes the first 8 MiB of the parsed backing bdev with write-zeroes before creating/importing. The code intentionally does not destroy the parsed bdev after wipe due to async NVMe deletion concerns.

State and dependencies: mutates pool metadata, backing disk contents, optional crypto vbdev settings, and lvol state. Depends on byte-unit parsing and `crate::lvs`.

Risks and test signals: defaulting unknown mode to import can mask typos. The URI shape is complex and testing-oriented. Validate create/import/purge modes, lvol replacement, and wipe behavior on disposable disks.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/lvs.rs -->
