<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_2xxx.h

## Purpose
`l4_2xxx.h` names OMAP2420 L4 firewall regions for DSS submodules. It supports legacy display/firewall configuration.

## Important APIs, Types, and Functions
Macros include `OMAP2420_L4_CORE_FW_DSS_CORE_REGION`, `OMAP2420_L4_CORE_FW_DSS_DISPC_REGION`, `OMAP2420_L4_CORE_FW_DSS_RFBI_REGION`, `OMAP2420_L4_CORE_FW_DSS_VENC_REGION`, and `OMAP2420_L4_CORE_FW_DSS_TA_REGION`.

## Control Flow
There is no runtime control flow. Constants are consumed by any code configuring L4 firewall regions.

## State and Persistence Behavior
No state is stored in the header. Firewall programming state lives in hardware.

## Dependencies and Integration Points
It integrates with OMAP2 DSS and L4 firewall setup. Its values are tied to OMAP2420 region numbering.

## Risks
Wrong region numbers can deny DSS register access or open unrelated regions. Edits should be validated against the OMAP2420 TRM.

## Test Signals
Compile OMAP2420 display/firewall users and run DSS register access tests without L4 firewall faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l4_2xxx.h -->
