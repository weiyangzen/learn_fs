# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.c

## Purpose
This file implements legacy MDP communication with the MediaTek VPU over IPI. It registers the MDP IPI handler, sends init/process/deinit messages, maps VPU shared memory, and records firmware status.

## Important APIs, Types, and Functions
Public APIs are `mtk_mdp_vpu_register()`, `mtk_mdp_vpu_init()`, `mtk_mdp_vpu_process()`, and `mtk_mdp_vpu_deinit()`. Internal helpers convert `struct mtk_mdp_vpu` to its context, handle init acknowledgements by mapping the VPU instance address, dispatch IPI acks, and serialize sends under `mdp_dev->vpulock`.

## Control Flow
On first context open, the driver registers an IPI handler. Stream-on calls init, which sends `AP_MDP_INIT`; the ack stores the firmware instance address and maps `vsi`. Each job sends `AP_MDP_PROCESS`; release sends `AP_MDP_DEINIT`. All sends check immediate IPI errors and the latest firmware failure status.

## State and Persistence
`struct mtk_mdp_vpu` stores the VPU platform device, firmware instance address, last failure code, and mapped shared `mdp_process_vsi` pointer. This state is per context and lasts until deinit/release.

## Dependencies and Integration Points
The code depends on `mtk_vpu.h` APIs: `vpu_ipi_register()`, `vpu_ipi_send()`, and `vpu_mapping_dm_addr()`. It integrates with context/device state from `mtk_mdp_core.h` and message definitions in `mtk_mdp_ipi.h`.

## Risks and Edge Cases
The IPI handler trusts `ap_inst` from firmware to be a valid kernel pointer. `vpu->failure` is shared between asynchronous acks and send callers without an explicit completion object here, relying on VPU send semantics. Unknown ack IDs are logged but not fatal if status is zero. A missing `vpu->pdev` returns `-EINVAL`.

## Test Signals
Firmware load/register, init ack mapping, process/deinit ack status failures, concurrent contexts serialized by `vpulock`, and VPU reset behavior are key tests.
