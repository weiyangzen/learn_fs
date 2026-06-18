<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_if_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_if_regs.h

## Purpose
Auto-generated MMIO offset map for the Goya `CPU_IF` block, the host/CPU interface used for queue doorbells, AXI attribute overrides, outstanding transaction control, response behavior, CPU address extension, and AXI split interrupt signaling.

## Important APIs, Types, And Functions
- `mmCPU_IF_PF_PQ_PI` is the producer-index/doorbell register used by queue submission paths.
- `mmCPU_IF_ARUSER_OVR`, `ARUSER_OVR_EN`, `AWUSER_OVR`, and `AWUSER_OVR_EN` control AXI user override values and enables.
- `mmCPU_IF_AXCACHE_OVR`, `LOCK_OVR`, and `PROT_OVR` control other AXI attributes.
- `mmCPU_IF_MAX_OUTSTANDING`, `EARLY_BRESP_EN`, and `FORCE_RSP_OK` tune response and outstanding behavior.
- `mmCPU_IF_CPU_MSB_ADDR` supplies high address bits for CPU-visible transactions.
- `mmCPU_IF_AXI_SPLIT_INTR` exposes split-transaction interrupt status/control.

## Control Flow
The header has no functions. Goya code writes queue and AXI registers during device initialization, queue setup, MMU/kernel ASID override setup, and cleanup. Doorbell writes to `PF_PQ_PI` notify firmware/hardware that queue entries are available.

## State And Persistence Behavior
All state is volatile hardware register state. Queue producer index and AXI override values are runtime configuration and are reset or cleared during device reset and MMU teardown.

## Dependencies And Integration Points
Integrates with Goya command submission, CPU queue initialization, MMU setup, DMA/host access paths, and low-level register access macros. It is used together with broader Goya register maps and block base definitions.

## Risks And Edge Cases
Incorrect queue producer writes can hang submissions or notify the wrong queue state. Leaving AXI user override enables active after teardown can leak incorrect ASID/user attributes into later transactions. Address high-bit configuration errors can redirect CPU transactions.

## Test Signals
Signals include queue initialization success, command submissions advancing after `PF_PQ_PI` writes, MMU override setup/teardown tests, no stale AXI override state after reset, and expected behavior under high outstanding transaction load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_if_regs.h -->
