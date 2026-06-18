# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.c

`otx2_devlink.c` registers devlink support for OcteonTX2 PF/VF netdevs. It exposes runtime parameters for MCAM ntuple count and unicast filter count, and optionally eswitch mode operations when representor support is enabled.

The lifecycle APIs are `otx2_register_dl` and `otx2_unregister_dl`. The driver parameters are `mcam_count` and `unicast_filter_count`, backed by `otx2_dl_mcam_count_*` and `otx2_dl_ucast_flt_cnt_*` get/set/validate callbacks. Optional `otx2_devlink_eswitch_mode_get/set` switches between legacy and switchdev by calling representor create/destroy helpers.

Probe allocates a devlink with private `struct otx2_devlink`, links it to `pfvf`, registers parameter metadata, and registers the instance. Parameter validation requires `flow_cfg` and blocks changes while active rules exist. `mcam_count` updates `ntuple_cnt` and calls `otx2_alloc_mcam_entries`; `unicast_filter_count` updates `ucast_flt_cnt`, deletes MCAM flows, and reinitializes default MCAM entries.

State is runtime-only and lives in `pfvf->dl` plus `pfvf->flow_cfg`. Dependencies are Linux devlink, flow management, and optional representor/eswitch helpers. Risks include setters assuming initialized flow state, hardware filter disruption during reinitialization, and `mcam_count_set` not reporting short allocation as a hard setter failure. Test with `devlink dev param show/set`, active ntuple-rule validation, MCAM count changes, unicast filter rebuild, remove cleanup, and eswitch mode transitions when configured.
