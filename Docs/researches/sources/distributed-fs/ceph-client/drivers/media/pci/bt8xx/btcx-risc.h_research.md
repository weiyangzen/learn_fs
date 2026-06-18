# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/btcx-risc.h

## Purpose
`btcx-risc.h` declares the shared RISC DMA memory descriptor and allocator/free APIs for bt8xx/cx-style RISC engines.

## Important APIs, Types, and Functions
`struct btcx_riscmem` stores the allocated byte size, little-endian instruction CPU pointer, optional jump pointer, and DMA address. `struct btcx_skiplist` describes a start/end range for RISC generation helpers outside this file. The declared functions are `btcx_riscmem_alloc()` and `btcx_riscmem_free()`.

## Control Flow
The header has no executable control flow. It defines the contract used by source files that allocate coherent RISC instruction buffers before programming the capture engine.

## State and Persistence
The structs describe runtime DMA memory and generation metadata only. No persistent state is represented.

## Dependencies and Integration Points
Consumers must include Linux types that define `__le32`, `dma_addr_t`, and `struct pci_dev`. The header is included by `btcx-risc.c` and capture code that builds bt8xx RISC instruction lists.

## Risks and Edge Cases
The header does not enforce initialization; callers must zero descriptors before first allocation and avoid using stale `jmp` pointers after realloc/free. The CPU pointer is little-endian instruction memory, so writers must use appropriate endian conversion for hardware opcodes.

## Test Signals
Compile users with the header, allocate/free descriptors through the declared functions, and confirm generated RISC programs use DMA addresses and little-endian instruction stores consistently.
