# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.h

Purpose: declares the SFC TC counter model and public counter-management functions.

Important types/APIs: `enum efx_tc_counter_type` aliases MAE counter types for action rules, conntrack, and outer rules. `struct efx_tc_counter` stores firmware id, type, rhashtable linkage, update lock, generation, packet/byte accounting, touched time, work item, and action-set users. `struct efx_tc_counter_index` maps a TC cookie to a refcounted counter. The header exports allocation, release, get/put/find-by-cookie helpers and `efx_tc_channel_type`.

State and integration: fields are consumed by `tc.c`, `tc_conntrack.c`, `tc_encap_actions.c`, and MAE channel setup. The rhashtable key layout depends on field ordering before `linkage`.

Risks and tests: changes need ABI-like coordination with rhashtable params and MAE counter formats. Compile SR-IOV TC and run offload add/delete/stats with counter streaming enabled.
