<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.c

## Purpose

`enic_pp.c` implements ENIC port-profile request handling for dynamic vNICs and SR-IOV VFs. It translates netlink VF port operations into Cisco VIC provisioning TLVs and firmware devcmd sequences for preassociate, associate, disassociate, and status query.

## Important APIs, Types, and Functions

Public functions are `enic_is_valid_pp_vf`, `enic_process_set_pp_request`, and `enic_process_get_pp_request`. Internal operations include `enic_set_port_profile`, `enic_unset_port_profile`, `enic_are_pp_different`, and request handlers `enic_pp_preassociate`, `enic_pp_disassociate`, `enic_pp_preassociate_rr`, and `enic_pp_associate`.

`enic_set_port_profile` allocates `vic_provinfo`, adds TLVs for profile name, client MAC, cluster UUID string, optional instance/host UUIDs, and Linux OS type, then calls `vnic_dev_init_prov2` through the proxy macro. Association handlers call `vnic_dev_enable2`, `vnic_dev_add_addr`, `vnic_dev_del_addr`, and deinit/done commands as appropriate.

## Control Flow

VF validation accepts `PORT_SELF_VF` only for dynamic vNICs and numbered VFs only when SR-IOV is enabled. Set request dispatch indexes `enic_pp_handlers` by request type. `PREASSOCIATE` is unsupported. `PREASSOCIATE_RR` optionally disassociates first, sets provisioning data, and enables the device as standby unless it is part of a later associate. `ASSOCIATE` disassociates if the previous state was not a matching preassociate, performs preassociate-RR, enables the device active, and registers the MAC. `DISASSOCIATE` removes registered MACs and deinitializes the profile.

Get request maps firmware completion status from enable/deinit done commands into `PORT_PROFILE_RESPONSE_*` values.

## State and Persistence Behavior

State lives in `enic->pp` entries, one for self or per VF, and in firmware provisioning/device state. The file updates request status indirectly; caller code in `enic_main.c` copies/clears profile entries and marks `ENIC_PORT_REQUEST_APPLIED`. There is no disk persistence.

## Dependencies and Integration Points

The file depends on rtnetlink VF port attributes handled by `enic_main.c`, `vnic_vic` provisioning helpers, `enic_dev.h` proxy macro, firmware devcmds, and SR-IOV state from `enic.h`.

## Risks and Edge Cases

TLV construction has multiple failure exits that must free `vic_provinfo`. MAC source differs for self, VF, and explicit port-profile MACs; missing VF MAC rejects provisioning. Request transitions use `restore_pp` to tell callers whether to restore previous in-memory state, so handler return semantics are important. `PREASSOCIATE` unsupported behavior must be acceptable to userspace tooling.

## Test Signals

Exercise dynamic self port-profile associate/disassociate, SR-IOV VF profiles, missing/invalid profile name or UUID lengths, missing MAC, firmware init/enable/deinit failures, get-status responses, repeated associate with same/different profiles, and cleanup resetting address lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_pp.c -->
