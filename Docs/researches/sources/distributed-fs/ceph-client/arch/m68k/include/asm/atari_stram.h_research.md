<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stram.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stram.h

## Purpose
This header declares Atari ST-RAM allocation and address-translation services. ST-RAM is required by hardware with DMA addressing limitations.

## Important APIs, Types, And Functions
- `atari_stram_alloc()` and `atari_stram_free()` allocate/free ST-RAM by owner name.
- `atari_stram_to_virt()` and `atari_stram_to_phys()` convert between ST-RAM physical and virtual addresses.
- `atari_stram_init()` and `atari_stram_reserve_pages()` are initialization/reservation hooks used by platform memory setup.

## Control Flow
Boot code initializes and reserves ST-RAM pages. Device drivers allocate ST-RAM buffers for DMA and translate addresses when programming hardware.

## State And Persistence Behavior
Allocator state is implementation-owned and persists across driver lifetime. Allocations represent scarce low-memory/DMA-capable memory and must be explicitly freed.

## Dependencies And Integration Points
It integrates with Atari memory setup, DMA-capable drivers, framebuffer/audio/storage paths, and any device unable to DMA from general RAM.

## Risks And Edge Cases
Leaked ST-RAM depletes a limited resource. Incorrect physical/virtual conversion can program bad DMA addresses. Early reservation must happen before general memory allocation consumes DMA-required pages.

## Test Signals
Boot memory reservation, repeated allocate/free cycles, DMA transfers from allocated ST-RAM, and conversion round trips validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stram.h -->
