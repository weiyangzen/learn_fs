# sources/cloud-native/nydus/utils/src/filemap.rs

Purpose: safe-ish wrapper for memory mapping file regions and reading/writing typed data from mapped bytes.

Important APIs/types/functions: `FileMapState` stores base/end pointers, size, and owned fd. `new(file, offset, size, writable)` maps with `mmap(MAP_NORESERVE | MAP_SHARED)` and takes ownership of the fd. Accessors include `size`, `get_ref<T>`, `get_mut<T>`, `get_slice<T>`, `get_slice_mut<T>`, `validate_range`, unsafe `offset`, and `sync_data`. `clone_file(fd)` duplicates a raw fd into a `File`.

Control flow: `new` maps the requested file region and converts the `File` into a raw fd only after mmap success. Drop unmaps and closes the fd. Range accessors compute start/end pointers with wrapping arithmetic and reject ranges outside `[base,end)`. Slice accessors check multiplication and address overflow and use dangling pointers for zero-length slices. `sync_data` temporarily reconstructs a `File` from the owned fd, calls `sync_data`, then forgets it to avoid closing.

State and persistence: owns an mmap and fd. Writes through mutable accessors can persist to the mapped file; `sync_data` flushes file data.

Dependencies and integration points: depends on `libc`, `nix::unistd::close`, Unix fd traits, and project error macros. Used by bootstrap/image metadata readers needing typed access to mapped files.

Risks: typed reference methods do not check alignment for `T`, so unaligned offsets can cause undefined behavior. `get_mut` can produce mutable references even if the mapping was created read-only; writing through them would fault or violate aliasing expectations. `MAP_NORESERVE`/`MAP_SHARED` are platform-specific to Unix/Linux assumptions. The `Send`/`Sync` impl assumes read-only data, but writable mappings can be created. `mmap` with size zero is not specially handled.

Test signals: tests map a RAFS bootstrap fixture and validate magic/range errors, default drop, mmap error on writable mapping of read-only file, slice overflow/out-of-range checks, and zero-length slice handling.
