# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.h

## Purpose
This header defines per-context VPU state and declares the legacy MDP VPU transport functions.

## Important APIs, Types, and Functions
`struct mtk_mdp_vpu` stores the VPU platform device, firmware instance address, failure status, and shared `mdp_process_vsi` pointer. Declared functions register the IPI handler and send init/process/deinit requests.

## Control Flow
The mem2mem frontend owns a `struct mtk_mdp_vpu` in each context and calls these functions during stream-on, job execution, and release.

## State and Persistence
The structure is per context and persists for the open file/streaming lifetime.

## Dependencies and Integration Points
It includes `mtk_mdp_ipi.h` for the shared-memory ABI and is included by the core context definition.

## Risks and Edge Cases
Callers must not use `vsi` before init succeeds. The header does not enforce send ordering.

## Test Signals
Compile/link checks and stream lifecycle tests validate the state contract.
