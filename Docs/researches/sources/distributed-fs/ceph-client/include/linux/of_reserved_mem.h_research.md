<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_reserved_mem.h -->
# sources/distributed-fs/ceph-client/include/linux/of_reserved_mem.h

## Purpose
This header declares reserved-memory framework types and OF helpers that bind DT `reserved-memory` regions to devices and convert memory-region entries to resources.

## Important APIs, types, and functions
`struct reserved_mem` records name, ops, base, size, and private data. `struct reserved_mem_ops` supplies node validation/fixup/init and per-device init/release callbacks. `RESERVEDMEM_OF_DECLARE()` places reserved-memory handlers in OF init tables. APIs include `of_reserved_mem_device_init_by_idx()`, `of_reserved_mem_device_init_by_name()`, `of_reserved_mem_device_init()`, `of_reserved_mem_device_release()`, `of_reserved_mem_lookup()`, region-to-resource helpers by index/name, and region count.

## Control flow
Early reserved-memory scanning matches compatible regions to declared ops, validates/fixes/initializes them, and later device setup attaches a referenced memory region by index or name. Device release calls the region's release operation. Disabled `CONFIG_OF_RESERVED_MEM` returns `-ENOSYS`, `NULL`, or no-op while preserving declarations as stubs.

## State and persistence
Reserved regions persist as physical memory excluded from normal allocation or managed by special allocators such as CMA/shared-dma-pool. Device attachment state is maintained by reserved-memory implementation and device-specific ops.

## Dependencies and integration points
It depends on OF declaration macros, device model, resources, and reserved-memory boot scanning. It integrates with DMA mapping, CMA, carveouts, remoteproc, framebuffer, and other devices with `memory-region` bindings.

## Risks and test signals
Risks include wrong region index/name, invalid alignment/base/size fixups, device release omissions, overlapping reserved regions, and disabled-config failures hidden by stubs. Test reserved-memory compatible declarations, named and indexed memory-region references, resource conversion, DMA/CMA attachment, release paths, and malformed/overlapping reserved-memory DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_reserved_mem.h -->
