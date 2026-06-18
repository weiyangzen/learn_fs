# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_rew.h

## Purpose
Defines Rewriter block register field macros for VLAN rewrite, tag behavior, port config, QoS mappings, PTP rewrite config, redundancy tags, sticky bits, and PPT stride.

## Important APIs/types/functions
Macro groups include `REW_PORT_VLAN_CFG`, `REW_TAG_CFG`, `REW_PORT_CFG`, `REW_PCP_DEI_QOS_MAP_CFG`, `REW_PTP_CFG`, `REW_RED_TAG_CFG`, DSCP remap registers, `REW_REW_STICKY_ES0_TAGB_PUSH_FAILED`, and `REW_PPT_RSZ`.

## Control flow, state, persistence
No executable flow. These macros encode state into rewriter registers used by VLAN/ES0/PTP/QoS code elsewhere. In this subset, flower prepares ES0 rewrite actions and PTP selects rewrite operations that eventually interact with the rewriter.

## Dependencies and integration
Integrates with Ocelot common rewriter setup, VLAN handling, ES0 VCAP actions, PTP one/two-step behavior, and QoS mapping. Depends on register maps accessed through `ocelot_io.c`.

## Risks and test signals
Risks are field-width mismatch, wrong TPID/tag selection, and ignored sticky ES0 push failures. Test VLAN push/modify, ES0 enable, PTP rewrite, PCP/DEI mapping, FCS update, and sticky-bit reporting.
