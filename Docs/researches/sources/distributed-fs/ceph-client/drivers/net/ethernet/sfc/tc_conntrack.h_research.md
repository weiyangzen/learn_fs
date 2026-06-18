# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_conntrack.h

Purpose: defines conntrack offload state shared between the SFC TC parser, MAE programming layer, and netfilter flowtable callback code.

Important types/APIs: `struct efx_tc_ct_zone` stores zone id, rhashtable linkage, refcount, `nf_flowtable`, owning NIC, a mutex, and the list of CT entries in that zone. `struct efx_tc_ct_entry` stores cookie, protocol tuple, NAT direction and translated fields, zone pointer, CT mark, attached counter, and zone-list linkage. Public functions initialize/finalize tables and register/unregister CT zones.

State and integration: the header exists only under `CONFIG_SFC_SRIOV` and includes `nf_flow_table.h` and refcount support. The structures are runtime-only and are mirrored into firmware by `tc_conntrack.c` and MAE helpers.

Risks and tests: structure fields are key material for rhashtable lookup, so changes must stay consistent with `efx_tc_ct_ht_params`. Build and runtime tests need SR-IOV-enabled TC CT coverage plus teardown with non-empty zone lists.
