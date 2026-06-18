# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dma.c

## Purpose

`ni_dma.c` implements the Cayman-and-newer asynchronous DMA engine support for the Radeon driver. NI hardware has two DMA engines with a packet format distinct from PM4 graphics packets. This file manages DMA ring pointers, ring startup/shutdown, IB execution, lockup detection, and DMA-assisted GPU VM page-table updates.

## Important APIs and Functions

- `cayman_dma_get_rptr()`, `cayman_dma_get_wptr()`, and `cayman_dma_set_wptr()` translate between Radeon ring dword pointers and hardware byte-scaled DMA ring registers for DMA0/DMA1.
- `cayman_dma_ring_ib_execute()` emits a DMA indirect-buffer packet, pads to the required 8-DW alignment, and optionally writes the next read pointer to writeback memory.
- `cayman_dma_stop()`, `cayman_dma_resume()`, and `cayman_dma_fini()` stop, initialize/test, and tear down the two DMA rings.
- `cayman_dma_is_lockup()` maps a ring index to `RADEON_RESET_DMA` or `RADEON_RESET_DMA1` and combines `cayman_gpu_check_soft_reset()` with generic ring lockup testing.
- `cayman_dma_vm_copy_pages()`, `cayman_dma_vm_write_pages()`, `cayman_dma_vm_set_pages()`, `cayman_dma_vm_pad_ib()`, and `cayman_dma_vm_flush()` generate DMA IB commands for page table copies, PTE writes, contiguous PTE/PDE setup, padding, and VM TLB invalidation.

## Control Flow

Startup is handled by `cayman_dma_resume()`, which loops over DMA0 and DMA1. For each engine it disables semaphore timers, computes ring buffer size encoding, sets endian swap bits when needed, resets hardware read/write pointers, writes read-pointer writeback addresses, sets ring base, enables DMA IBs with forced VMID handling, disables context-empty interrupts, writes the initial write pointer, enables the ring, marks it ready, and runs `radeon_ring_test()`. If either ring test fails, that ring is marked not ready and the error propagates.

IB execution pads the current ring so the DMA indirect-buffer packet ends on an 8-DW boundary. When writeback is enabled it first writes a predicted next read pointer into writeback memory through a DMA write packet. It then writes the indirect-buffer packet containing the IB GPU address, length, high address bits, and VMID.

VM update helpers build commands into a caller-provided `struct radeon_ib`. Copy mode copies PTE data from GART memory to page-table memory. Write mode emits explicit PTE values, mapping system pages through `radeon_vm_map_gart()` when `R600_PTE_SYSTEM` is set. Set mode uses the DMA PTE/PDE packet for physically contiguous pages. VM flush writes the page-directory base register, flushes HDP, invalidates the selected VM context, and reads back `VM_INVALIDATE_REQUEST` through SRBM read polling.

## State and Persistence Behavior

The file mutates `rdev->ring[]` entries for DMA0 and DMA1, especially `wptr` and `ready`. It also uses `rdev->wb` for optional read-pointer writeback, `rdev->mc` for visible versus real VRAM size, and `rdev->asic->copy.copy_ring_index` to adjust the active VRAM aperture when DMA is used as the copy engine.

Hardware state is stored in DMA ring control/base/pointer registers and VM registers. Page-table update commands persist GPU VM mappings in VRAM or GART-backed page tables once executed by the DMA engine.

## Dependencies and Integration Points

`ni_dma.c` depends on Radeon ring helpers, writeback memory, VM helpers, reset-mask helpers from `ni.c`, DMA packet macros/registers from `nid.h`, and generic ASIC copy/TTM behavior. It is started and stopped from `ni.c` during Cayman startup, suspend, and finalization. Its VM functions are consumed by the Radeon VM manager when choosing DMA-based page-table updates.

## Risks and Edge Cases

- Ring pointer hardware uses byte addressing while Radeon rings use dword indices; the shifts and `0x3fffc` masks must stay consistent.
- DMA IB packets require strict 8-DW alignment. Missing padding can make the engine fetch malformed IBs.
- Writeback next-rptr prediction depends on packet sizes and padding; miscalculation can confuse software ring accounting.
- Page-table update chunk sizes are capped at `0xFFFFE` dwords; loops must reduce `count` correctly to avoid overruns or infinite loops.
- VM write mode truncates some 64-bit values into 32-bit IB slots intentionally as lower/upper dwords; changes must preserve packet layout.
- Lockup detection depends on `cayman_gpu_check_soft_reset()` correctly distinguishing DMA0 and DMA1.

## Test Signals

Important signals include successful DMA ring tests for both engines, working BO copy/fill operations when DMA is the copy ring, GPU VM page-table updates under system and VRAM memory, absence of VM faults after DMA flushes, and recovery behavior when either DMA ring is forced hung. Big-endian builds are a distinct build/runtime test because swap bits are conditionally programmed.
