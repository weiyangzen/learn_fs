<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_2xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_2xxx.h

## Purpose
`l3_2xxx.h` defines OMAP2 L3 firewall connection IDs needed by legacy platform display/security setup.

## Important APIs, Types, and Functions
It defines `OMAP2_L3_CORE_FW_CONNID_DSS` for the display subsystem. There are no functions or types.

## Control Flow
No runtime control flow exists. The macro is used by code that configures or documents L3 firewall initiator/connection permissions.

## State and Persistence Behavior
No local state exists. The macro names a hardware firewall ID whose programmed state lives in L3 firewall registers.

## Dependencies and Integration Points
It integrates with OMAP2 L3/firewall and DSS-related platform code. The include guard is `__ARCH_ARM_PLAT_OMAP_INCLUDE_PLAT_L3_2XXX_H`.

## Risks
Wrong IDs can grant or deny the wrong L3 initiator, causing display access faults or security misconfiguration. Because the file is tiny, stale use sites are the primary maintenance risk.

## Test Signals
Compile OMAP2 DSS/firewall users and boot display-enabled OMAP24xx systems. Runtime signal is DSS access without L3 firewall violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/l3_2xxx.h -->
