# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c

## Purpose
Implements the AMDGPU SDMA v4.0 family IP block for Vega/Raven/Arcturus/Aldebaran-era devices. It manages firmware, SoC15 register programming, gfx and optional page SDMA rings, VM PTE emitters, buffer copy/fill, interrupts, RAS, power/clock gating, and debug register dumps.

## APIs, Types, And Functions
The primary exported objects are `sdma_v4_0_ip_funcs` and `sdma_v4_0_ip_block`. Internal function tables include `sdma_v4_0_ring_funcs`, `sdma_v4_0_page_ring_funcs`, `sdma_v4_0_vm_pte_funcs`, `sdma_v4_0_buffer_funcs`, `sdma_v4_4_buffer_funcs`, IRQ source handlers, and `sdma_v4_0_ras`. Major functions cover register offset mapping, firmware init/load, golden register programming, ULV setup, ring pointer access, gfx/page resume, microcode loading, IP lifecycle, trap/ECC/VM-hole/doorbell/poll-timeout/SRBM-write interrupt handling, clock/power gating, RAS count/reset, and IP state dump/print.

## Control Flow
`early_init` loads firmware through shared SDMA helpers, decides whether firmware supports a page queue, then installs ring, buffer, VM, IRQ, and RAS hooks. `sw_init` registers per-instance trap and ECC IRQs, optionally registers extra fault/debug IRQs for five/eight-instance devices, initializes gfx rings and optional page rings with 64-bit doorbells, assigns VM hubs, initializes RAS, and allocates an IP dump buffer. `hw_init` disables APU SDMA power gating, programs golden registers outside SR-IOV, and calls `sdma_v4_0_start()`. Start loads microcode directly unless PSP loading is active, unhalts engines, enables context switching, programs gfx/page rings, enables UTC L1, resumes RLC/power-gating support, and tests all active rings.

## State And Persistence
State is kept in `adev->sdma.instance[]`, per-ring writeback and doorbell fields, `adev->sdma.has_page_queue`, firmware instance contexts, RAS registration, and `adev->sdma.ip_dump`. Firmware context may be shared for Arcturus/Aldebaran. Page queue support is a persistent runtime capability selected from IP version and firmware version. RAS counters are hardware EDC counters read or read-cleared by the driver. IP dump state is an in-memory snapshot buffer allocated at `sw_init` and populated by `dump_ip_state`.

## Dependencies And Integration
The file depends on SoC15 register-offset macros, SDMA packet macros, AMDGPU firmware and ring infrastructure, NBIO HDP flush offsets, GMC VM flush helpers, DPM/SMU power-gating hooks, RAS helpers, and the v4.4 RAS helper exported by `sdma_v4_4.c`. It integrates with TTM through `adev->mman.buffer_funcs`, VM page-table scheduling through `amdgpu_sdma_set_vm_pte_scheds()`, scheduler fault handling through illegal-instruction IRQs, and RAS through `amdgpu_sdma_ras_sw_init()` and per-IP callbacks.

## Risks And Test Signals
Risks include numerous ASIC-specific golden setting paths, firmware-version gating for page queues, SR-IOV differences, page-queue doorbell offset differences between Vega10 and newer parts, Arcturus MMHUB1 routing for instances 5-7, unimplemented `soft_reset`, and subtle count-minus-one packet length encoding. Useful tests include firmware load on each supported IP version, gfx/page ring tests, IB scheduling, VM update workloads, TMZ copy paths, interrupt injection or fault logging for VM holes and bad doorbells, RAS EDC counter query/reset, suspend/resume including S0ix paths, power/clock gating toggles, and IP dump validation.
