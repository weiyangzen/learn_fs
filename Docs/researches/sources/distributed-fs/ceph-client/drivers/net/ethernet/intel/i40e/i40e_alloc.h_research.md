# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_alloc.h

## Purpose

`i40e_alloc.h` is the small shared allocation contract for i40e common code. It gives hardware/shared modules a driver-local abstraction for coherent DMA memory and ordinary virtual memory without embedding allocation implementation details in common Admin Queue, HMC, NVM, or DCB code.

## Important APIs, Types, And Functions

- `struct i40e_dma_mem` tracks DMA-backed memory through virtual address `va`, bus/DMA address `pa`, and `size`.
- `struct i40e_virt_mem` tracks non-DMA virtual memory through `va` and `size`.
- `i40e_allocate_dma_mem()` allocates DMA memory for shared code consumers.
- `i40e_free_dma_mem()` releases DMA memory.
- `i40e_allocate_virt_mem()` allocates normal driver memory.
- `i40e_free_virt_mem()` releases virtual memory.

The implementations are in `i40e_main.c`, while callers include Admin Queue ring setup, ARQ/ASQ buffer info arrays, HMC page/table management, DCB buffers, and NVM update helpers.

## Control Flow

The header itself only declares contracts. A subsystem prepares an empty `i40e_dma_mem` or `i40e_virt_mem`, calls an allocation helper, stores `va`/`pa`/`size` into queue or HMC/NVM/DCB structures, and calls the matching free helper during unwind, shutdown, reset cleanup, or error handling.

## State And Persistence Behavior

The state is in the memory tracking structs. DMA allocations back hardware-visible descriptor rings and command buffers, so stale `pa`/`va` fields can cause hardware access to freed memory if cleanup ordering is wrong. Virtual allocations carry driver-only buffers. No allocation state persists across driver unload.

## Dependencies And Integration Points

- Includes Linux types and forward-declares `struct i40e_hw`.
- Integrates with `i40e_adminq.h`, `i40e_hmc.h`, `i40e_type.h`, and `i40e_main.c`.
- The abstraction keeps common code independent of exact Linux allocator calls.

## Risks

- DMA allocation accepts `u64 size`, while virtual allocation uses `u32 size`; callers must avoid truncating large virtual allocations.
- Missing matched frees can leak coherent DMA or virtual memory. Double frees or stale pointers can corrupt queue/HMC teardown.
- Alignment is caller-specified for DMA and must match hardware requirements.
- Because the structs are minimal, ownership and lifetime are implicit in caller code.

## Test Signals

- Error-unwind tests around Admin Queue and HMC initialization should verify every successful allocation is freed.
- Fault injection on allocation failures should leave tracking fields in a safe state.
- DMA API debug and KASAN/KMEMLEAK are strong signals for misuse.
- Reset/unload/reload loops can expose stale DMA or virtual allocation lifetime bugs.
