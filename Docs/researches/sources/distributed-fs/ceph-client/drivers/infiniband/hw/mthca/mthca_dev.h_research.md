# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_dev.h

## Purpose
`mthca_dev.h` is the central private header for the mthca driver. It defines driver identity, capability flags, hardware constants, shared state structures, logging/access macros, and cross-module function prototypes.

## Important APIs, types, and functions
Key types include `mthca_cmd`, `mthca_limits`, `mthca_alloc`, `mthca_array`, resource tables for UAR/PD/MR/EQ/CQ/SRQ/QP/AV/MCG, `mthca_catas_err`, and the top-level `struct mthca_dev`. It defines hardware opcodes, flags such as `MTHCA_FLAG_MEMFREE`, `MTHCA_FLAG_MSI_X`, and `MTHCA_FLAG_SRQ`, EQ indexes, object sizes, `MTHCA_GET`/`MTHCA_PUT` endian helpers, logging macros, `to_mdev()`, and `mthca_is_memfree()`.

## Control flow
All implementation files include this header to share the top-level device object. Probe fills `mthca_dev`, setup initializes its resource tables in order, event and command paths consult table fields, and teardown unwinds the same embedded state.

## State and persistence
`struct mthca_dev` persists runtime driver state for the life of a PCI device: `ib_device`, PCI pointer, flags, firmware/DDRx information, mapped MMIO bases, command state, resource limits, all object tables, catastrophic polling state, driver UAR/PD/MR, MAD agents, SM AHs, cached port rates, and active flag.

## Dependencies and integration points
It includes provider and doorbell headers and depends on Linux PCI/DMA/timer/mutex/list/semaphore APIs plus RDMA core types. It is the nexus connecting command, memory, queue, MAD, provider, and main modules.

## Risks
Because this header exposes many internals, changes have broad blast radius. `MTHCA_GET`/`MTHCA_PUT` rely on exact field sizes and offsets. Table sizes and masks must remain powers of two for allocators. `active` and catastrophic-reset state are shared across async paths. Logging macros compile away in non-debug builds, so side effects in debug arguments would be unsafe.

## Test signals
Full driver build coverage is the primary signal. Runtime tests should cover Tavor/mem-free flag paths, resource-table init and cleanup ordering, endian helpers against known firmware buffers, debug and non-debug builds, catastrophic restart, and all modules using the shared prototypes.
