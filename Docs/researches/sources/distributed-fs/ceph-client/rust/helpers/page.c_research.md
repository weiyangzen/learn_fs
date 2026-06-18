# sources/distributed-fs/ceph-client/rust/helpers/page.c

## Purpose
Exposes page allocation, temporary mapping, unmapping, and optional NUMA-node lookup to Rust.

## APIs, Types, and Functions
APIs include `alloc_pages`, `kmap_local_page`, `kunmap_local`, and conditionally `page_to_nid`.

## Control Flow, State, and Persistence
State is allocated pages and per-thread local kmap stack state owned by MM/highmem code.

## Dependencies and Integration
Depends on `linux/gfp.h`, `linux/highmem.h`, `linux/mm.h`, and Rust page abstractions.

## Risks and Test Signals
Risks include allocation leaks, highmem mapping imbalance, using local mappings after unmap or migration, and config-dependent node lookup. Test signals are Rust page allocation/fill tests and highmem/NUMA config builds.
