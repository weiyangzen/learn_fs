# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.c

## Purpose
`ksz_dcb.c` implements DSA DCB priority controls for KSZ switches. It manages default port priority, global DSCP-to-internal-priority mapping, and apptrust selector configuration for PCP and DSCP priority sources across KSZ8 and KSZ9477-like register layouts.

## Important APIs, Types, and Functions
Public functions are `ksz_port_get_default_prio()`, `ksz_port_set_default_prio()`, `ksz_port_get_dscp_prio()`, `ksz_port_add_dscp_prio()`, `ksz_port_del_dscp_prio()`, `ksz_port_set_apptrust()`, `ksz_port_get_apptrust()`, `ksz_dcb_init_port()`, and `ksz_dcb_init()`. Internal helpers select family-specific registers (`ksz_get_default_port_prio_reg()`, `ksz_get_dscp_prio_reg()`, `ksz_get_apptrust_map_and_reg()`), initialize DSCP maps, and validate apptrust order.

## Control Flow
Global setup calls `ksz_dcb_init()`, which initializes every DSCP entry to a deterministic mapping and enables DSCP remapping on non-KSZ8 parts. Per-port setup calls `ksz_dcb_init_port()`, which sets Best Effort as the default priority and sets default apptrust to PCP. User DCB calls then read or update the relevant port or global registers through common `ksz_*` helpers. DSCP add writes a global table entry; DSCP delete restores that DSCP to Best Effort when the current entry matches the requested priority.

## State and Persistence
State is hardware-register backed: default priority bits live in per-port control registers; DSCP maps live in global TOS/DSCP registers; apptrust state lives in per-port priority-source enable bits. No software cache persists the DCB map, and no disk state exists. The DSA flag `dscp_prio_mapping_is_global` in common setup matches the global DSCP table behavior here.

## Dependencies and Integration Points
The file depends on DSA DCB callbacks, `net/dscp.h`, `net/ieee8021q.h`, common KSZ helpers, and KSZ8 family predicates. It is integrated into `ksz_switch_ops` through DSA callbacks and is initialized from `ksz_common.c` setup and port setup paths.

## Risks and Edge Cases
Register packing differs: KSZ8-style chips map four DSCP values per byte with two-bit priorities, while KSZ9477-style chips map two DSCP values per byte with three-bit priorities. Non-KSZ8 DSCP remapping must be enabled or the hardware falls back to DSCP bits 3-5. Apptrust order is fixed by hardware, and validation rejects reordered or unsupported selector lists. `ksz_init_global_dscp_map()` writes all DSCP entries but only returns the last write result, so an intermediate failure would be overwritten by later success.

## Test Signals
Test by reading default priority after init, setting boundary priorities around `num_ipms`, validating all 64 DSCP entries, toggling DSCP remap on KSZ9477-like parts, checking KSZ8 queue conversion, verifying apptrust accepts empty/PCP/DSCP/PCP+DSCP in fixed order and rejects reversed order, and confirming DSA DCB callbacks surface expected `-EINVAL`, `-ERANGE`, or register errors.
