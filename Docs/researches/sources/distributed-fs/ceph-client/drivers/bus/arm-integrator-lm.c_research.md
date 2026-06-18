# sources/distributed-fs/ceph-client/drivers/bus/arm-integrator-lm.c

## Purpose
Implements the ARM Integrator AP Logical Module bus driver. It discovers installed logic modules through the Integrator system controller and populates matching device-tree child nodes for occupied slots.

## Important APIs, Types, And Functions
`integrator_ap_lm_probe()` is the platform probe entry point. It finds the `arm,integrator-ap-syscon` regmap, reads `INTEGRATOR_SC_DEC_OFFSET`, and loops over four slot bits. `integrator_lm_populate()` computes the expansion slot base address and calls `of_platform_default_populate()` for child nodes whose first resource starts at that slot base.

## Control Flow
Probe obtains the syscon regmap, reads the decode register, then for each detected module bit calls `integrator_lm_populate()`. Population scans available children below the LM bus node, resolves child address resources, compares against `0xc0000000 + slot * 0x10000000`, and populates only the matching module subtree.

## State And Persistence
The driver keeps no long-lived private state. It reads hardware presence bits and creates platform child devices, which then persist in the Linux device model until driver removal or reboot.

## Dependencies And Integration Points
It depends on OF, syscon/regmap, platform bus population, and the `arm,integrator-ap-lm` compatible. It integrates with child device-tree descriptions for actual devices hosted on the logical modules.

## Risks And Test Signals
Risks include stale/missing syscon nodes, wrong address resources in child nodes, slot-bit interpretation errors, and duplicate/missing child population. Test signals are module detection logs, created platform devices under the LM bus, and child driver probes for each installed module.
