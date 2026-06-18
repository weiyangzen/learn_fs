<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_regs.h

## Purpose
Auto-generated MMIO offset map for the Goya `CPU_CA53_CFG` block. It names the registers used to configure and observe the embedded ARM Cortex-A53 subsystem.

## Important APIs, Types, And Functions
- `mmCPU_CA53_CFG_ARM_CFG` names the boot configuration register.
- `mmCPU_CA53_CFG_RST_ADDR_LSB_*` and `mmCPU_CA53_CFG_RST_ADDR_MSB_*` name reset vector registers for two cores.
- `mmCPU_CA53_CFG_ARM_RST_CONTROL`, `ARM_AFFINITY`, `ARM_DISABLE`, `ARM_GIC_PERIPHBASE`, and `ARM_GIC_IRQ_CFG` name reset, topology, feature-disable, and interrupt configuration registers.
- `mmCPU_CA53_CFG_ARM_PWR_MNG`, `ARM_PWR_STAT_*`, `ARM_DBG_*`, `ARM_MEM_ATTR`, and `ARM_PMU_*` name power, debug, memory attribute, and PMU registers.

## Control Flow
No functions are present. Driver and firmware bring-up code uses these offsets with register accessors such as `WREG32` and `RREG32` to program boot vectors, release resets, set GIC/debug configuration, and poll power/debug status.

## State And Persistence Behavior
Offsets identify volatile hardware registers. Values persist in the hardware block across normal operation and are reset according to ASIC reset domains. The header itself is static generated metadata.

## Dependencies And Integration Points
Pairs with `cpu_ca53_cfg_masks.h` for field extraction and update. Integrates with Goya boot sequencing, reset management, CPU debug, power management, and generated block definitions that provide the base address.

## Risks And Edge Cases
Wrong offsets can write control values into unrelated registers, causing boot failure or unstable reset behavior. This block is close to CPU bring-up, so small address mistakes have high blast radius. The offsets are not self-describing; consumers must use the matching masks from the same ASIC generation.

## Test Signals
Signals include successful boot after writing reset vectors, expected status bits in power/debug registers, correct response to reset control changes, and no MMIO faults or timeouts during early Goya initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_regs.h -->
