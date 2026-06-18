# sources/distributed-fs/ceph-client/include/linux/io-mapping.h

Purpose: This header provides an abstraction for efficient CPU mappings of pages from an I/O device, especially write-combining mappings for large device apertures.

Important APIs, types, and functions: `struct io_mapping` records base, size, pgprot, and optionally a permanent `iomem` mapping. APIs include `io_mapping_init_wc`, `io_mapping_fini`, `io_mapping_create_wc`, `io_mapping_free`, `io_mapping_map_atomic_wc`, `io_mapping_unmap_atomic`, `io_mapping_map_local_wc`, `io_mapping_unmap_local`, `io_mapping_map_wc`, and `io_mapping_unmap`.

Control flow: On `CONFIG_HAVE_ATOMIC_IOMAP`, initialization reserves an iomap range and page mappings are created on demand through fixmap/local mapping helpers. Atomic map disables preemption or migration and page faults, then maps one PFN; unmap reverses this. Without atomic iomap, init creates one `ioremap_wc` covering the full range, and map helpers return offsets into it.

State and persistence: An `io_mapping` persists until `io_mapping_fini` or `io_mapping_free`. Atomic/local mappings are short-lived and must be paired with unmap calls in the same execution context.

Dependencies and integration points: Integrates with `ioremap_wc`, `iomap_create_wc`, `kunmap_local_indexed`, pagefault control, PREEMPT_RT migration rules, and device memory consumers such as graphics drivers.

Risks: Offset bounds are checked with `BUG_ON`, so invalid callers crash. Atomic mappings must not sleep and must be unmapped promptly. PREEMPT_RT changes preemption to migration disable. Permanent fallback can consume significant kernel virtual address space.

Test signals: Exercise both config branches, offset-at-end checks, atomic/local nesting, PREEMPT_RT builds, write-combining attributes, and cleanup after failed allocation or mapping initialization.
