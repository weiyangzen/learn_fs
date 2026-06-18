# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifc00d.h

## Purpose
Defines GP100 VMM ABI extensions, including newer mapping attributes used by Pascal/Volta-era page tables.

## Important APIs, Types, And Functions
Includes generic VMM definitions, `gp100_vmm_v0` with fault-replay capability flag, `gp100_vmm_map_v0` with volatile/read-only/privilege/kind fields, method IDs `GP100_VMM_VN_FAULT_REPLAY` and `GP100_VMM_VN_FAULT_CANCEL`, and `gp100_vmm_fault_cancel_v0` with hub/GPC/client/instance selector.

## Control Flow
No executable flow. Raw and normal VMM map paths pass these payloads into GP100 MMU backends. Fault-replay and fault-cancel methods control GPU fault handling for selected faulting instances/clients.

## State And Persistence
Payloads are transient; descriptor state persists in GPU page tables, while replay/cancel method effects apply to live fault handling state.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_GP100`, `nvif/vmm.h`, and GP100+ page descriptor construction.

## Risks
Descriptor attribute mismatch can cause faults, compression/kind issues, or coherency failures. Incorrect fault-cancel selectors can cancel the wrong fault context or fail to recover.

## Test Signals
GP100 VMM maps, sparse/raw maps, page faults, fault replay/cancel tests, and compression/kind tests validate behavior.
