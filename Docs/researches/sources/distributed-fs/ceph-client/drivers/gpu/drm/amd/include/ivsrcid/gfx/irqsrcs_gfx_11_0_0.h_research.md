# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_11_0_0.h

## Purpose
This header defines GFX 11.0.0 interrupt source IDs for graphics, SDMA-as-reported-through-GFX client paths, memory access, poisoning, command processor, RLC, GRBM, and SQ events.

## Important APIs, Types, And Data
It introduces low source IDs for `UTCL2_FAULT`, `UTCL2_DATA_POISONING`, and `MEM_ACCES_MON`. SDMA-related IDs occupy `0x30` through `0x43`, including atomic return, trap, SRBM write protection, context empty, preempt, IB preempt, invalid doorbell, queue hang, atomic timeout, poll timeout, page timeout/null/fault, VM hole, ECC, frozen, SRAM ECC, semaphore timeouts, and user fence.

Graphics-side IDs include `RLC_GC_FED_INTERRUPT` at `0x80`, CP generic/fault/EOP/preempt/query/doorbell/ECC sources around `0xB1`-`0xCA`, GRBM read timeout and GUI idle, and SQ interrupt `0xEF`.

## Control Flow
There are no functions. `amdgpu/gfx_v11_0.c`, `gfx_v11_0_3.c`, and `sdma_v6_0.c` use these macros while registering IRQ IDs and identifying poison/fault/SDMA events in IH entries.

## State And Persistence
The header is immutable. Runtime state is built in AMDGPU's IRQ registration tables and per-IP fault handling logic.

## Dependencies And Integration Points
It integrates with SOC15 IH clients for GFX/SDMA reporting, GFX 11 CP setup, RLC poison/FED handling, SDMA v6 IRQ setup, VM fault reporting, and reset/RAS paths.

## Risks
GFX 11 extends the table beyond older CP-only IDs, so using GFX 9/10 constants would miss SDMA and UTCL2 events. `RLC_GC_FED_INTERRUPT` has poisoning semantics in some paths; handling it as a generic perf event can hide data-poisoning conditions.

## Test Signals
Build GFX 11 and SDMA v6 paths. Runtime signals include EOP/fence completion, CP fault interrupts, SDMA trap/fence/page-fault interrupts, UTCL2 fault reporting, poisoning/RAS interrupt handling, and recovery after queue hang or GPU reset.
