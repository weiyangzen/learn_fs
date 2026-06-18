# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_dma.c

Purpose: Southern Islands SDMA engine implementation. It initializes two DMA rings, emits SDMA packets for IBs, fences, VM updates, TLB flushes, buffer copy/fill, trap interrupts, and clock/power gating.

Important APIs, types, and functions: exports `si_dma_ip_block` and defines `sdma_offsets`, `si_dma_ring_funcs`, `si_dma_vm_pte_funcs`, `si_dma_buffer_funcs`, and trap IRQ callbacks. Key functions are `si_dma_start()/stop()`, ring pointer accessors, `si_dma_ring_emit_ib()`, `si_dma_ring_emit_fence()`, `si_dma_ring_test_ring()`, `si_dma_ring_test_ib()`, VM PTE writers, `si_dma_ring_emit_vm_flush()`, and lifecycle hooks `early_init`, `sw_init`, `hw_init`, `suspend`, and `resume`.

Control flow: early init sets two SDMA instances and installs ring, buffer, VM PTE, and IRQ function tables. Software init registers legacy IRQ IDs 224 and 244 and creates `sdma0`/`sdma1` rings. Hardware init programs ring buffer control, read-pointer writeback, base addresses, IB control, disables context-empty interrupts, enables rings, then runs ring tests. Command emission writes packet dwords directly into ring or IB buffers; VM updates are chunked to hardware packet limits.

State and persistence: persistent state lives in SDMA registers, ring BOs, writeback slots, `adev->sdma`, IRQ source tables, and memory-manager buffer callback pointers. Fence packets persist sequence values into GPU-visible memory. No disk state exists.

Dependencies and integration points: integrates with amdgpu ring scheduling, fences, IRQ core, VM/GMC TLB flush helpers, writeback memory, IB allocation/scheduling, and TTM buffer moves through `adev->mman.buffer_funcs`.

Risks and test signals: packet alignment is subtle: IB packets must start on an 8-DW boundary and IBs are padded to 8 DW. The ring supports only 40-bit-ish address high fields (`& 0xff`) and advertises no 64-bit pointers. Soft reset is not implemented. Test signals include ring and IB self-tests writing `0xDEADBEEF`, trap IRQ fence processing on both instances, VM update correctness, suspend/resume ring restart, and buffer copy/fill validation.
