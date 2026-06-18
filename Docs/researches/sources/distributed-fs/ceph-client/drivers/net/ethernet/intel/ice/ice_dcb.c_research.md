# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.c

## Purpose
`ice_dcb.c` is the firmware-facing DCB/DCBX and LLDP MIB implementation. It reads LLDP/DCBX state from firmware, parses IEEE 802.1Qaz, CEE, and DSCP-oriented organizational TLVs into `struct ice_dcbx_cfg`, builds LLDP TLVs from local configuration, starts/stops LLDP and DCBX firmware agents, configures MIB change events, sets PFC mode, and queries port ETS scheduling topology.

## Important APIs, Types, And Functions
Public functions include `ice_aq_get_dcb_cfg()`, `ice_get_dcb_cfg()`, `ice_set_dcb_cfg()`, `ice_get_dcb_cfg_from_mib_change()`, `ice_init_dcb()`, `ice_cfg_lldp_mib_change()`, `ice_aq_stop_lldp()`, `ice_aq_start_lldp()`, `ice_aq_start_stop_dcbx()`, `ice_aq_set_pfc_mode()`, and `ice_query_port_ets()`.

Parser helpers include `ice_lldp_to_dcb_cfg()`, `ice_parse_org_tlv()`, IEEE ETS/PFC/APP parsers, and CEE PG/PFC/APP parsers. Serializer helpers include `ice_dcb_cfg_to_lldp()`, `ice_add_dcb_tlv()`, IEEE TLV builders, and DSCP TLV builders. `ice_cee_to_dcb_cfg()` converts firmware CEE operational responses into the common DCBX model. Port scheduler helpers query ETS through AdminQ and update the software scheduler tree.

## Control Flow
Initialization through `ice_init_dcb()` first checks DCB capability, reads firmware DCBX status from `PRTDCB_GENS`, and either fetches current DCB config when the firmware agent is active/progressing or returns `-EBUSY` when DCBX is disabled. If requested, it enables LLDP MIB change ARQ events; failure switches the QoS state toward software LLDP handling.

Configuration read flow starts with `ice_get_dcb_cfg()`. It attempts the CEE operational AQ command; if present, it fetches desired/local and remote LLDP MIBs and translates CEE operational fields. If CEE is absent (`LIBIE_AQ_RC_ENOENT`), it switches to IEEE mode and parses local/remote LLDP MIBs. LLDP parsing skips the Ethernet header, iterates TLVs until END or `ICE_LLDPDU_SIZE`, dispatches organizational TLVs by OUI, and fills ETS, PFC, app, DSCP map, and mode fields.

Configuration write flow uses `ice_set_dcb_cfg()`: allocate an LLDPDU buffer, choose local MIB flags, serialize the local DCB config into IEEE or DSCP TLVs depending on `pfc_mode`, and call `ice_aq_set_lldp_mib()`. ETS queries go through `ice_query_port_ets()`, which locks `pi->sched_lock`, issues the query, then reconciles root TC nodes with returned TEIDs.

## State And Persistence
Persistent driver state is stored in `pi->qos_cfg`: local, remote, and desired DCBX configs; DCBX status; and `is_sw_lldp`. Firmware persistence is controlled by LLDP start/stop `persist` flags and by setting the local LLDP MIB. PFC mode changes affect firmware hardware behavior. Scheduler tree updates mutate the in-memory port scheduling tree after querying firmware.

## Dependencies And Integration Points
The file depends on AdminQ command descriptors, `ice_common.h`, `ice_sched.h`, LLDP/DCBX constants from `ice_dcb.h`, endian and bitfield helpers, device-managed allocation, and scheduler-tree helpers. It integrates with the ARQ event path via `ice_get_dcb_cfg_from_mib_change()`, with DCB runtime policy in `ice_dcb_lib.c`, and with DCBNL userspace control through `ice_set_dcb_cfg()`/`ice_get_dcb_cfg()`.

## Risks
Risks concentrate around TLV bounds and format assumptions: APP TLV count truncation, CEE sub-TLV traversal, LLDPDU offset accounting, and DSCP TLV fixed lengths. CEE conversion has special handling for strict priority, FCoE/iSCSI/FIP, and iSCSI port variants; regressions can silently mis-advertise application priorities. `ice_aq_set_pfc_mode()` must verify firmware wrote back the requested mode because disabled DCB can cause firmware to echo zero.

## Test Signals
Test with firmware LLDP enabled and disabled, IEEE and CEE peer configurations, absent remote MIBs, DSCP mode, VLAN mode, pending MIB events, PFC mode changes, and reset/rebuild paths. Packet-level LLDP fixtures for ETS/PFC/APP/DSCP TLVs, scheduler TEID reconciliation checks, and AQ fault injection for `ENOENT`, `EIO`, invalid buffer sizes, and unsupported DCB capability are strong coverage points.
