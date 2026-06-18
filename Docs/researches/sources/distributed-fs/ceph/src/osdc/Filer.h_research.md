<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Filer.h -->
# sources/distributed-fs/ceph/src/osdc/Filer.h

## Purpose

`Filer.h` declares Ceph's file-to-object helper for clients that want logical inode byte-range I/O without hand-building object extents. The class wraps an `Objecter` and a `Finisher`, exposes asynchronous file operations, and hides the internal probe state used to discover logical file end and modification time across striped RADOS objects.

## Important APIs and Types

`class Filer` owns pointers to `CephContext`, `Objecter`, and `Finisher`. It is constructed from an existing `Objecter` and `Finisher`, and `is_active()` delegates liveness to the objecter.

The public async I/O API includes `read`, `read_trunc`, `write`, `write_trunc`, `zero`, `truncate`, and `purge_range`. Each takes an inode number and `file_layout_t`; read-like calls take a `snapid_t`, write-like calls take `SnapContext`, modification time, flags, and a completion `Context`. `read_trunc` and `write_trunc` include truncate size/sequence so callers can maintain ordered truncate semantics.

`probe` is overloaded for modern `ceph::real_time` and legacy `utime_t` mtime outputs. It searches forward or backward from `start_from` and writes the discovered logical end into the caller-provided `uint64_t *end`. The optional mtime output asks the implementation to continue scanning enough objects to report the maximum mtime observed in the searched region.

The private `Probe` struct is the main declared state. It has its own `std::mutex`, stores the immutable request fields, result pointers, current probing offset and length, extents being probed, per-object known sizes, max mtime, outstanding operations, accumulated error, and `found_size` flag. `C_Probe`, `_probe`, `_probed`, and `probe_impl` form the hidden asynchronous probe implementation.

`_do_purge_range` and `_do_truncate_range` are declared because their state structs are file-local implementation structs in `Filer.cc` while callbacks need to call back into `Filer`.

## Control Flow and Contracts

All public operations are asynchronous and complete a `Context`. The header's method signatures make the split clear: the caller supplies buffers and completion contexts, while the filer only maps logical ranges and delegates object execution. Callers retain responsibility for choosing snapshots, layout, flags, and truncate sequence values.

The probe contract is direction-sensitive. In forward mode it searches for the first short object relative to expected object extent size. In backward mode it searches earlier periods until it finds non-empty data or reaches the lower bound supplied through `end`. When an mtime pointer is provided, probe also reports the maximum object mtime observed while searching.

## State and Persistence Behavior

`Filer` itself does not own persistent metadata, caches, or journals. It relies on `file_layout_t` to derive object names and locators and on `Objecter` to submit durable RADOS mutations. The `Probe` state is heap allocated per request and freed after completion. Purge and truncate range state are declared as opaque implementation structs and similarly exist only for in-flight operations.

The persistent data affected by this API are file data objects, full-object removals, zeroed object ranges, object truncate metadata, and object mtimes. Snapshot persistence is entirely driven by `SnapContext` and read `snapid_t` values supplied by callers.

## Dependencies and Integration Points

The header depends on Ceph filesystem and OSD types: `file_layout_t`, `inodeno_t`, `ObjectExtent`, `SnapContext`, `object_t`, `snapid_t`, `ceph::buffer::list`, and Ceph time types. It forward-declares `Context`, `Messenger`, `Objecter`, and `Finisher` to keep compile dependencies lower.

`Journaler.h` includes `Filer.h` and embeds a `Filer` instance for journal storage. CephFS client/MDS-side code can use this API as the low-level object mapping layer, while `ObjectCacher` provides a separate cache/writeback path with similar file convenience wrappers.

## Risks and Edge Cases

The header exposes raw pointer completion and output parameters; callers must keep buffers and result pointers alive until completion. Copy constructor and assignment operator are declared private-ish without definitions in this header's public area, signaling copying should not be used even though the declarations are visible near public construction.

`probe` requires valid snapshots and sane `start_from`/`end` bounds. Multi-object purge/truncate completion assumes callback contexts are valid. Layout correctness is critical because every API trusts the supplied `file_layout_t`.

## Test Signals

Header-level users should be tested for callback lifetime, null/non-null completion behavior expected by each operation, real-time and `utime_t` probe overloads, truncating I/O propagation, and correct integration with layouts whose period is larger than one object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Filer.h -->
