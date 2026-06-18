# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.h

## Purpose
This header defines the MDP3 firmware IPC message ABI and the runtime state object used by the VPU/SCP communication layer.

## Important APIs, Types, And Functions
`enum mdp_ipi_result` maps firmware result codes to kernel-visible statuses. `struct mdp_ipi_init_msg` carries status, driver data, work buffer address, and size. `struct mdp_ipi_deinit_msg` carries status, driver data, and work address. `struct mdp_vpu_dev` stores the SCP handle, completion, shared parameter/work/config buffers, DMA addresses, sizes, lock, and last status. Public functions are `mdp_vpu_shared_mem_free()`, `mdp_vpu_dev_init()`, `mdp_vpu_dev_deinit()`, and `mdp_vpu_process()`.

## Control Flow
The header defines the message payloads used by the C file's init, deinit, and frame-processing sequences. `drv_data` carries a kernel pointer through firmware acknowledgements so handlers can find the `mdp_vpu_dev`.

## State, Persistence, And Dependencies
All state is runtime memory and DMA memory. The header depends on platform device support and the MDP image IPI ABI.

## Integration Points
Included by MDP3 core and M2M code. Firmware-facing structs must match SCP firmware. The VPU device is embedded in `struct mdp_dev`.

## Risks
`drv_data` is a pointer encoded as `u64`, so firmware must preserve it exactly. `work_addr` fields are 32-bit despite `dma_addr_t` storage. Packed struct layout is ABI-sensitive.

## Test Signals
IPI ack routing to the correct device, successful firmware init on each platform, DMA address range validation, and repeated stream lifecycle tests.
