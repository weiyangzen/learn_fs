# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_dcb.h

## Purpose
`ice_dcb.h` defines the wire-format constants, packed TLV structures, DCBX status values, and public firmware-facing DCB APIs used by the ice DCB implementation. It is the shared contract for parsing/building IEEE 802.1Qaz, CEE DCBX, and Intel DSCP organizational TLVs.

## Important APIs, Types, And Functions
The header defines DCBX status constants (`ICE_DCBX_STATUS_*`), LLDP TLV type/length masks, IEEE OUI/subtype constants for ETS/PFC/APP, CEE OUI/subtypes, DSCP OUI/subtypes, TLV IDs and fixed lengths, and bit masks for ETS/PFC/app fields. Packed wire structures include `struct ice_lldp_org_tlv`, `struct ice_cee_tlv_hdr`, `struct ice_cee_ctrl_tlv`, `struct ice_cee_feat_tlv`, and `struct ice_cee_app_prio`.

Function declarations expose firmware control and configuration entry points: `ice_aq_set_pfc_mode()`, `ice_aq_get_dcb_cfg()`, `ice_get_dcb_cfg()`, `ice_set_dcb_cfg()`, `ice_get_dcb_cfg_from_mib_change()`, `ice_init_dcb()`, `ice_query_port_ets()`, LLDP start/stop, DCBX start/stop, and MIB change configuration. When `CONFIG_DCB` is disabled, LLDP/DCBX control functions are stubbed to no-op success or inactive status.

## Control Flow
The constants in this header drive parser switch statements and serializer TLV selection in `ice_dcb.c`. The `CONFIG_DCB` split also changes call behavior: core driver paths can call LLDP/DCBX helpers unconditionally while builds without DCB avoid firmware side effects for those optional controls.

## State And Persistence
This file defines no state itself. Its packed structures describe data as it appears in LLDP MIBs and CEE AQ responses. Persistent behavior is indirect: `persist` flags in declared LLDP functions and MIB serialization constants influence firmware state across reboot when callers request it.

## Dependencies And Integration Points
It includes `ice_type.h` for core device/DCB structures and `<scsi/iscsi_proto.h>` for iSCSI protocol constants used by CEE app translation. It is consumed by `ice_dcb.c`, `ice_dcb_lib.c`, `ice_dcb_nl.c`, and any code handling LLDP MIB-change events.

## Risks
The masks and fixed lengths must match firmware and standards exactly. Because structures are packed and parsed from firmware/network buffers, incorrect field sizes or endian handling can corrupt parsed DCB config. `CONFIG_DCB` stubs returning success can hide missing feature support if callers assume an action actually reached firmware.

## Test Signals
Build tests with and without `CONFIG_DCB`, parser fixture coverage for each OUI/subtype, static assertions or review against firmware specs for TLV lengths, and runtime DCB init on devices advertising different DCBX statuses are useful signals.
