# sources/distributed-fs/ceph-client/include/linux/dax.h

Purpose: Defines the kernel API for Direct Access devices and filesystem-DAX mappings, including direct PFN access, writeback, poison recovery, layout breaking, iomap I/O/fault integration, and hmem resource enumeration.

Important APIs, types, and functions: Key types are `dax_entry_t`, `struct dax_device`, `enum dax_access_mode`, `struct dax_operations`, and `struct dax_holder_operations`. Device APIs include `alloc_dax()`, `put_dax()`, `kill_dax()`, `dax_dev_get()`, cache/synchronous/nocache/nomc setters, `dax_direct_access()`, copy/zero/recovery helpers, holder failure notification, and read locking. Filesystem APIs include `fs_dax_get_by_bdev()`, `fs_dax_get()`, `fs_put_dax()`, `dax_writeback_mapping_range()`, busy-page queries, mapping-entry locks, `dax_iomap_rw()`, `dax_iomap_fault()`, `dax_finish_sync_fault()`, mapping entry deletion/invalidation, `dax_break_layout()`, dedupe/remap prep, and zero/truncate/unshare helpers.

Control flow: Device providers register operations that translate logical page offsets to physical addresses and optionally recover poisoned storage. Filesystems acquire a DAX device for a block device and holder, verify synchronous mapping support for `MAP_SYNC`, then use iomap-backed paths for reads, writes, faults, zeroing, and remap preparation. Layout-breaking helpers coordinate with pages or exceptional entries before operations that cannot race with DAX mappings.

State and persistence: The header exposes state owned elsewhere: DAX device lifetime, holders, cache policy, poison recovery ability, radix/xarray mapping entries, and hmem resources. Persistent data is the underlying pmem/block media; this API bypasses page cache persistence semantics and relies on flush/writeback hooks.

Dependencies and integration points: Integrates with VFS inodes, address spaces, iomap, block devices, writeback control, memory failure, folios/pages, VM faults, dev_dax/hmem, and filesystem reflink/dedupe paths. Config-gated stubs keep non-DAX builds compiling while returning `-EOPNOTSUPP`, `-ENODEV`, or inert defaults.

Risks and test signals: Risks include allowing synchronous mappings on non-synchronous devices, stale DAX mappings during truncate/reflink, incorrect poison error translation, missing cache flushes, and use-after-kill of `dax_device`. Test fs-DAX mount and `MAP_SYNC`, direct I/O and mmap faults, media poison recovery, truncate/hole-punch/remap races, writeback/invalidate paths, DAX-disabled builds, and hmem registration/enumeration.
