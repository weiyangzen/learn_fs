# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_ipi.h

## Purpose
This header defines the packed AP-to-VPU IPI message ABI and shared MDP process configuration for the legacy driver.

## Important APIs, Types, and Functions
Message IDs cover AP init/deinit/process and VPU acknowledgements. `struct mdp_ipi_init`, `struct mdp_ipi_comm`, and `struct mdp_ipi_comm_ack` are the transport messages. `struct mdp_config`, `struct mdp_buffer`, `struct mdp_config_misc`, and `struct mdp_process_vsi` describe source/destination crop/format/buffers and rotation/flip/alpha settings. `MTK_MDP_MAX_NUM_PLANE` fixes the plane count at three.

## Control Flow
The AP sends init to allocate/map a VPU instance, fills the shared `mdp_process_vsi`, then sends process/deinit messages. The VPU replies with ack messages containing status and instance address.

## State and Persistence
The packed structures represent shared memory and mailbox payload state. They persist only while the VPU instance exists and must match firmware layout exactly.

## Dependencies and Integration Points
This ABI is included by `mtk_mdp_vpu.h`, `mtk_mdp_vpu.c`, and register helper code. It couples the kernel driver to the MediaTek VPU firmware implementation.

## Risks and Edge Cases
Packed structure layout, field sizes, and message IDs are firmware ABI; changing them breaks AP/VPU communication. Buffer addresses are 64-bit MVA values even when other fields are 32-bit, so alignment and endian assumptions matter.

## Test Signals
IPI init/process/deinit round trips, firmware status failures, shared-memory dump comparisons, and cross-architecture structure-size checks are useful signals.
