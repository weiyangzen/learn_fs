# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.h

## Purpose
`sec_drv.h` is the shared private header for the legacy HiSilicon SEC driver. It defines SEC hardware descriptor bitfields, queue/ring/device structures, algorithm transform/request state, hardware SGL formats, constants, and cross-file function prototypes used by `sec_algs.c` and `sec_drv.c`.

## Important APIs, types, and functions
The central hardware type is `struct sec_bd_info`, a 16-word block descriptor with extensive bit masks for cipher/auth mode, key sizes, granularity, DMA addresses, and completion/error flags. Queue and device types include `struct sec_queue_ring_cmd`, `struct sec_queue_ring_cq`, `struct sec_queue_ring_db`, `struct sec_queue`, `struct sec_dev_info`, `struct sec_hw_sge`, and `struct sec_hw_sgl`. Crypto state types include `enum sec_cipher_alg`, `struct sec_alg_tfm_ctx`, `struct sec_request`, and `struct sec_request_el`. Prototypes expose queue operations and algorithm registration callbacks between the two C files.

## Control flow
The header has no executable logic, but it encodes the control contract: algorithms build `sec_bd_info` and `sec_request_el` objects, submit them through `sec_queue_send()`, and receive completions through `sec_alg_callback()`. The driver uses queue/device definitions to allocate rings, map queue registers, maintain ordered completion, and free resources.

## State and persistence behavior
All state described by the header is runtime state. Keys live in coherent DMA memory attached to transform contexts; requests own DMA mappings and hardware SGL chains; queues own coherent rings and completion shadow pointers; devices own MMIO bases and DMA pools. There is no durable persistence.

## Dependencies and integration points
The header depends on Linux crypto API types, `kfifo`, scatterlists through users of the structures, DMA addresses, mutex/spinlock/list primitives, and hardware register definitions in the C files. It is the integration boundary between the platform queue driver and crypto algorithm implementation.

## Risks and edge cases
Descriptor bitfield definitions must match hardware documentation exactly. Duplicated `SEC_MAX_SGE_NUM` definition is benign but increases maintenance risk. Large structures combine hardware ABI fields and software-only pointers, so users must not DMA-map the wrong structure type. Request splitting and IV chaining rely on the semantics documented in comments for `struct sec_request` and `struct sec_queue`.

## Test signals
Compile coverage of both C files, descriptor field validation through successful encryption/decryption, SGL chain tests with more than 64 entries, queue pressure/backlog tests, and completion/error flag tests are the most relevant signals.
