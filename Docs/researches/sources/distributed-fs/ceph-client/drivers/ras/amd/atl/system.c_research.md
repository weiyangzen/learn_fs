# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/system.c

Purpose: discovers and caches system-wide AMD Data Fabric topology data for ATL. It determines the DF revision, node/socket/die/component masks and shifts, number of coherent-station maps, DRAM hole base, MI300 quirks, and PRM-only operation.

Important APIs and functions: exports `const guid_t norm_to_sys_guid` and provides `determine_node_id()` and `get_df_system_info()`. Revision helpers include `determine_df_rev()`, `determine_df_rev_legacy()`, `df4_determine_df_rev()`, `df*_get_masks_shifts()`, `df4_get_fabric_id_mask_registers()`, `get_num_maps()`, `apply_node_id_shift()`, and `get_dram_hole_base()`.

Control flow: `get_df_system_info()` calls `determine_df_rev()`. Pre-DF4 detection probes legacy mask registers, DF4+ detection reads major/minor revision and device/vendor IDs. Zen4 server applies a socket-shift quirk. MI300 marks the platform heterogeneous and calls `get_umc_info_mi300()`. Unsupported future DF revisions require PRM handler availability and set `df_cfg.flags.prm_only`. Non-PRM paths then normalize ID shifts, set map count, read DRAM hole base, and dump the resulting config.

State and persistence: updates the global `df_cfg` cache. No durable persistence exists; data is collected at module/system initialization and reused by translation paths. `determine_df_rev()` is idempotent once `df_cfg.rev` is no longer `UNKNOWN`.

Dependencies and integration: uses DF indirect read helpers, masks from `reg_fields.h`, `<linux/prmt.h>`, AMD CPU/device IDs, ACPI PRM availability checks, and `get_umc_info_mi300()` from `umc.c`. Its output is consumed by `map.c`, `umc.c`, and the ATL decoder.

Risks: failed DF reads leave revision unknown and prevent software translation. The ID-shift quirk rewrites masks aggressively for a specific device ID. PRM-only systems require firmware handler support. MI300 initialization depends on SMN reads in `umc.c`.

Test signals: boot on DF2/DF3/DF3.5/DF4/DF4.5, Zen4 server quirk systems, MI300 systems, PRM-only future systems, PRM-absent failure, DRAM-hole read failure warning, and invalid socket/die inputs to `determine_node_id()`.
