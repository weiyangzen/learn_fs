# sources/distributed-fs/ceph-client/net/openvswitch/vport-internal_dev.h

## Purpose
`vport-internal_dev.h` declares the public helpers for OVS internal netdevices.

## Important APIs
`ovs_is_internal_dev()` identifies netdevices backed by OVS internal device ops. `ovs_internal_dev_get_vport()` returns the owning vport for an internal netdevice. `ovs_internal_dev_rtnl_link_register()` and `ovs_internal_dev_rtnl_link_unregister()` register/unregister both the rtnl link kind and the internal vport ops.

## Control Flow and Integration
`vport-netdev.c` uses `ovs_is_internal_dev()` to prevent adding an internal device as a normal netdev vport. Datapath module init/exit uses the rtnl registration helpers. Internal-device implementation provides the definitions.

## State and Persistence
No state is declared here. The API exposes lookups into runtime netdevice private data.

## Dependencies
It depends on `datapath.h` and `vport.h` for core OVS and vport types.

## Risks
Callers must pass valid netdevices. The registration helpers must be paired during module init/cleanup to avoid stale rtnl link kinds or vport ops.

## Test Signals
Build coverage, internal port creation, rejection of internal devices as external netdev vports, and module cleanup are relevant signals.
