# sources/distributed-fs/ceph-client/include/linux/kfifo.h

## Purpose

`kfifo.h` provides the generic typed kernel FIFO API. It supports in-place FIFOs, dynamically allocated FIFO buffers, fixed-size element queues, record FIFOs with 1- or 2-byte length fields, spinlocked wrappers, user-copy helpers, and DMA scatterlist preparation. The source was read as a complete 1000-line file.

## Important APIs, Types, and Functions

Core storage is `struct __kfifo` with `in`, `out`, `mask`, element size, and data pointer. Macro types include `STRUCT_KFIFO()`, `STRUCT_KFIFO_PTR()`, `STRUCT_KFIFO_REC_1()`, and `STRUCT_KFIFO_REC_2()`. Main APIs include `DECLARE_KFIFO`, `DEFINE_KFIFO`, `INIT_KFIFO`, `kfifo_alloc()`, `kfifo_alloc_node()`, `kfifo_init()`, `kfifo_free()`, `kfifo_in()`, `kfifo_out()`, `kfifo_put()`, `kfifo_get()`, `kfifo_peek()`, `kfifo_from_user()`, `kfifo_to_user()`, `kfifo_dma_*()`, `kfifo_out_linear()`, and many `__kfifo_*` backend declarations.

## Control Flow

Callers declare or allocate a power-of-two ring, initialize counters and element size, then push and pop by advancing monotonic `in` and `out` counters masked into the buffer. Record FIFOs route through `_r` helpers to prepend/read record lengths. Single producer plus single consumer needs no extra lock; multi-producer or multi-consumer paths wrap calls in spinlock variants.

## State and Persistence Behavior

FIFO state is entirely in memory. Dynamic FIFOs own allocated buffer memory until `kfifo_free()`. In-place FIFOs embed the buffer in the containing object. Counters are free-running `unsigned int` values, so correctness depends on size/mask arithmetic and the assumption that distance between `in` and `out` is bounded by FIFO size.

## Dependencies and Integration Points

It depends on spinlocks, barrier primitives, errno, typed macro extensions, user-copy implementations in the C backend, DMA scatterlists, and NUMA allocation. Drivers use it for byte streams, event queues, DMA staging, and control paths.

## Risks and Edge Cases

Compile-time negative array sizing catches non-power-of-two in-place sizes. `kfifo_reset()` is unsafe with concurrent access. DMA finish helpers do no bounds checking. Record FIFOs reserve length bytes, so availability can be zero even when raw free space exists. Return values are marked must-check in many paths and should not be ignored.

## Test Signals

Kernel kfifo tests, wraparound tests, typed put/get compile tests, record FIFO length boundary tests, spinlocked multi-thread stress, user-copy fault injection, DMA scatterlist preparation tests, and 32-bit counter wrap stress are relevant.
