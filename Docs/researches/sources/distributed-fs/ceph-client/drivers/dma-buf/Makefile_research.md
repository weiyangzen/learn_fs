# sources/distributed-fs/ceph-client/drivers/dma-buf/Makefile

Purpose: wires the dma-buf core, optional heap/sync/misc drivers, and selftest objects into Kbuild.

Important APIs/types/functions: always builds `dma-buf.o`, `dma-fence.o`, `dma-fence-array.o`, `dma-fence-chain.o`, `dma-fence-unwrap.o`, `dma-resv.o`, and `dma-buf-mapping.o`. Optional objects include `dma-heap.o`, `heaps/`, `sync_file.o`, `sw_sync.o`, `sync_debug.o`, `udmabuf.o`, and the composite `dmabuf_selftests.o`.

Control flow: no runtime control flow. Kconfig symbols select which translation units are linked. The selftest object aggregates `selftest.o`, `st-dma-fence.o`, `st-dma-fence-chain.o`, `st-dma-fence-unwrap.o`, and `st-dma-resv.o`.

State and persistence behavior: none beyond build products.

Dependencies and integration points: connects core dma-buf primitives to optional heap and synchronization facilities. The always-built core objects provide exported symbols consumed by graphics, media, accelerator, and memory-sharing drivers.

Risks and test signals: core object ordering matters only through link inclusion, not initialization order, which is handled by initcalls in the source files. Test signals are symbol availability for namespace exports and successful builds across heap/sync/selftest combinations.
