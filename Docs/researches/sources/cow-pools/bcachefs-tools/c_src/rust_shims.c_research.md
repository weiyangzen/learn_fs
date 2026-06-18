# File Research: sources/cow-pools/bcachefs-tools/c_src/rust_shims.c

- C shim layer for Rust access to bcachefs internals that are macros, static inlines, or complex kernel-style APIs.
- Wraps superblock checksum, allocation-info stripping, online device iteration/ref cleanup, journal replay collection, dump decrypt operations, atomic bit setting, and device ref get/put.
- Bridges Rust I/O futures to C bcachefs write/read setup with bio vectors, disk reservations, completion callbacks, and read flags.
- Provides `rust_link_data` for migrate/import use: creates extents pointing to existing physical data, splits at bucket boundaries, gets disk reservations, marks reconcile needs, and inserts extent bkeys.
- Exposes accounting memory read.
