# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_processpptables.c

`vega12_processpptables.c` parses and materializes the Vega12 ATOM PowerPlay table. It allocates `hwmgr->pptable`, validates the VBIOS PPTable, applies platform capability bits, copies power/clock/OD limits, duplicates the embedded SMU `PPTable_t`, augments it with SMC DPM information from firmware control helpers, and exposes `vega12_pptable_funcs`.

The public API is `const struct pp_table_func vega12_pptable_funcs` with `.pptable_init = vega12_pp_tables_initialize` and `.pptable_fini = vega12_pp_tables_uninitialize`. Important internal functions are `get_powerplay_table()`, `check_powerplay_tables()`, `set_platform_caps()`, `init_powerplay_table_information()`, and `append_vbios_pptable()`.

Initialization allocates `struct phm_ppt_v3_information`, locates or reuses the ATOM `powerplayinfo` table through `hwmgr->soft_pp_table`, validates revision/size, sets `PHM_PlatformCaps_*` from VBIOS platform caps, initializes thermal and overdrive metadata, copies indexed limits, `kmemdup()`s the embedded `smcPPTable`, and appends extra VBIOS SMC DPM fields such as I2C, VR telemetry, voltage-step, GPIO, LED, and spread-spectrum settings. Finalization frees allocated arrays, the SMU PPTable copy, and `hwmgr->pptable`.

Persistent input is VBIOS firmware data; parsed output is volatile state in `hwmgr->pptable`, later uploaded by `vega12_init_smc_table()`. Dependencies include ATOM firmware lookup, `pp_atomfwctrl_get_smc_dpm_information()`, `phm_copy_*_limits_array()`, `phm_cap_*`, Linux allocation, and `vega12_pptable.h`.

Risks include leaks on partial initialization failure, trusting table sizes after minimal validation, duplicated assignment of `Vr2_I2C_address`, endian correctness, and platform-cap mismatch. Test signals include PPTable init/fini leak checks, malformed VBIOS rejection, OD limit visibility, thermal-controller and BACO caps, and SMU PPTable upload success.
