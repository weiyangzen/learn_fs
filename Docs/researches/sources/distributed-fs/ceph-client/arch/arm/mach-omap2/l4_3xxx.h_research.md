<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_3xxx.h

## Purpose
`l4_3xxx.h` defines OMAP3 L4 firewall region and protection-group IDs for I2C and DSS modules.

## Important APIs, Types, and Functions
Important macros include `OMAP3_L4_CORE_FW_I2C1_REGION`, `OMAP3_L4_CORE_FW_I2C*_TA_REGION`, `OMAP3_L4_CORE_FW_DSS_PROT_GROUP`, `OMAP3_L4_CORE_FW_DSS_DSI_REGION`, `OMAP3ES1_L4_CORE_FW_DSS_CORE_REGION`, and DSS DISPC/RFBI/VENC/TA region IDs.

## Control Flow
No runtime control flow exists. These constants feed L4 firewall configuration or documentation.

## State and Persistence Behavior
No local state exists. Hardware firewall registers persist the actual access rules.

## Dependencies and Integration Points
It integrates with OMAP3 I2C and display firewall code. The ES1-specific DSS core region constant captures a silicon revision difference.

## Risks
Confusing ES1 and later DSS region IDs can break register access on one revision. I2C firewall mistakes can prevent bus probe or mask security faults.

## Test Signals
Compile OMAP3 I2C/DSS firewall users and boot on ES1 and later where available. Exercise I2C transfers and DSS register access while monitoring interconnect/firewall errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_3xxx.h -->
