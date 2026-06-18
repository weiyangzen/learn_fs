<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c_research.md`.

Purpose: defines kfilnd module parameters, validates defaults, translates traffic-class strings, and applies module/NI tunables to LNet common and kfilnd-specific configuration.

Important APIs/types/functions: module params `cksum`, `kfi_timeout`, `tx_scale_factor`, `rx_cq_scale_factor`, `tx_cq_scale_factor`, `eq_size`, `immediate_rx_buf_count`, `prov_cpu_exclusive`, workqueue flags, `credits`, `peer_credits`, reserve mins, `peer_buffer_credits`, `peer_timeout`, provider version, `auth_key`, and `traffic_class`. Public APIs are `kfilnd_tunables_setup()`, `kfilnd_tunables_init()`, `kfilnd_get_tn_reserve_min()`, `kfilnd_get_msg_reserve_min()`, and `kfilnd_get_peer_credits()`.

Control flow: init validates module params, clamps `wq_max_active`, converts traffic class, and fills `kfi_default_tunables`. NI setup fills unset common LNet tunables from module params, clamps peer credits to max credits, initializes unset provider/auth/traffic values, validates credit/key limits, provider major version, and traffic class, then stores timeout.

State and persistence behavior: module params are global runtime configuration; most are read-only after load, while timeout, provider CPU exclusivity, and reserve mins can be writable according to mode. `kfi_default_tunables` snapshots defaults for netlink export.

Dependencies and integration: depends on Linux module_param, LNet common/kfilnd tunable structs, KFI traffic-class constants, endpoint key limit, and transaction mempool sizing.

Risks: the zero-initialized provider check repeats `lnd_prov_major_version` instead of checking minor, likely a typo. Invalid traffic strings or excessive credits prevent startup. Reserve defaults derive from peer credits times CPT count, so high CPT counts can increase memory pressure. `auth_key` zero is rejected/replaced.

Test signals: load with invalid scale factors, too few receive buffers, bad/empty traffic class, excessive credits, provider major version mismatch, custom NI tunables, reserve-min overrides, and netlink export of default tunables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c -->
