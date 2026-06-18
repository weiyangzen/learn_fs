# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c

## Purpose
Implements the AMDGPU SDMA v4.4.2-family IP block for newer multi-AID/XCP-capable GPUs. It manages shared firmware, per-instance register mapping, gfx and optional page rings, queue stop/restore and per-queue reset support, XCP suspend/resume, VM and buffer packet emitters, interrupts, clock gating, debug dumps, and newer RAS/ACA integration.

## APIs, Types, And Functions
Exports `sdma_v4_4_2_ip_funcs`, `sdma_v4_4_2_ip_block`, and `sdma_v4_4_2_xcp_funcs`. Internal tables include `sdma_reg_list_4_4_2`, `sdma_v4_4_2_ring_funcs`, `sdma_v4_4_2_page_ring_funcs`, `sdma_v4_4_2_vm_pte_funcs`, `sdma_v4_4_2_buffer_funcs`, `sdma_v4_4_2_sdma_funcs`, IRQ source tables, RAS register/memory lists, and ACA bank ops. Key routines handle firmware init/load, instance-masked start/stop, ring pointer access through writeback offsets, ring/page resume with restore semantics, queue reset, trap/ECC/fault IRQ processing, reset mask updates, XCP callbacks, and RAS query/reset/late-init.

## Control Flow
`early_init` loads one shared firmware image for v4.4.2/4.4.4/4.4.5, disables page queues because firmware support currently returns false, and installs callbacks. `sw_init` registers IRQs for the number of SDMA instances per AID, initializes each SDMA instance with doorbells, AID-derived MMHUB routing, reset mutexes, guilty flags, ring names, and optional page rings, initializes RAS and sysfs reset-mask state, and allocates IP dump memory. `hw_init` builds a full instance mask, programs golden GB address registers outside SR-IOV, then starts all instances. Instance start optionally loads microcode, enables engines/context switch, programs rings, enables UTC L1 and context-empty interrupts for older v4.4.x revisions, runs RLC resume, and tests rings.

## State And Persistence
State is richer than earlier SDMA versions: each instance stores `aid_id`, reset mutex, guilty queue flags, function hooks, cached read pointers, firmware context, and ring/page structs. Queue stop caches rptr values before reset because registers are cleared; restore can skip bad commands for a guilty queue by setting rptr to current wptr or continue from cached rptr for non-guilty queues. Reset capabilities are accumulated in `adev->sdma.supported_reset` after checking GC IP, MEC firmware version, DPM support, and debug disable flags. RAS state is held in common RAS data structures; ACA binding adds cached bank-error reporting. IP dumps are in-memory snapshots.

## Dependencies And Integration
Depends on AMDGPU core, XCP, reset, firmware, ring, KFD suspend/resume, DPM SDMA reset, SoC15 register access, SDMA packet macros, NBIO HDP flush offsets, GMC VM flush helpers, RAS, SMUIO MCM topology, and ACA error-bank infrastructure. It integrates with `amdgpu_sdma_reset_engine()`, per-ring `.reset`, `amdgpu_sdma_sysfs_reset_mask_init()`, `amdgpu_xcp_ip_funcs`, `amdgpu_sdma_ras_late_init()`, and `amdgpu_ras_bind_aca()`.

## Risks And Test Signals
High-risk areas are logical-to-physical SDMA instance mapping via `GET_INST`, AID/node mapping in trap IRQ handling, SR-IOV client-ID remapping, restore behavior after queue reset, guilty queue detection via context status, firmware/PMFW/MEC gating for per-queue reset, and `soft_reset` still being a TODO at the IP-block level. `BUG_ON` in fence alignment is harsher than v4.0's warning. Test signals include firmware load, full and XCP instance-mask start/stop, ring/IB tests, queue reset under timeout with KFD suspend/resume, sysfs reset-mask exposure, trap IRQ routing for multi-AID nodes, VM-hole/doorbell/poll/SRBM/context-empty debug IRQ logs, RAS UE query/reset, ACA bank parsing, clock-gating toggles, and IP dump coverage.
