# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_ipblock_data.c

## Purpose
`omap_hwmod_common_ipblock_data.c` defines common class descriptors for OMAP display subsystem IP blocks shared across OMAP2+ hwmod data: DSS core and RFBI.

## Important APIs, Types, and Functions
The file defines `omap2_dss_sysc`, `omap2_dss_hwmod_class`, `omap2_rfbi_sysc`, and `omap2_rfbi_hwmod_class`. The DSS class includes `.reset = omap_dss_reset`; both classes encode sysconfig offsets, reset status support, autoidle, sidle modes, and type1 sysconfig fields.

## Control Flow
No local control flow exists. SoC-specific hwmod tables attach these classes to DSS and RFBI hwmods. During hwmod reset/idle sequencing, the class metadata directs register access and optional DSS reset handling.

## State and Persistence Behavior
The data is static. Runtime persistence is limited to hardware state written through hwmod operations: DSS reset state, sysconfig autoidle, and idle mode settings.

## Dependencies and Integration Points
The file depends on `omap_hwmod.h` and `omap_hwmod_common_data.h`, especially `omap_hwmod_sysc_type1`. It integrates with DSS display drivers and legacy OMAP display init paths that still use hwmod reset and idle handling.

## Risks
Wrong offsets or flags can break display reset, leave DSS clocks active, or prevent RFBI from idling. Because display often participates in suspend/resume, mistakes can appear as blank panels or resume hangs rather than immediate boot failures.

## Test Signals
Build display-enabled OMAP2/3 configs. Boot with DSS/RFBI users, verify display probe, reset completion, idle transitions, suspend/resume, and lack of hwmod sysconfig warnings.
