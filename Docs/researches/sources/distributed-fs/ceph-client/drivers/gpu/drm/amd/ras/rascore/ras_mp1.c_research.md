# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.c

Purpose: this is the generic MP1 RAS dispatch layer. It selects an IP-specific MP1 function table and forwards valid-bank count and bank-dump requests used by ACA/ECC collection and firmware EEPROM feature discovery.

Important APIs: `ras_mp1_hw_init()` records `mp1_ip_version`, installs `mp1_sys_fn` from config, selects `mp1_ras_func_v13_0` for supported MP1 v13 variants, and fails if callbacks or IP support are absent. `ras_mp1_get_bank_count()` and `ras_mp1_dump_bank()` forward to the selected IP functions. `ras_mp1_hw_fini()` is a no-op.

Control flow and state: state is limited to configured IP version, system callbacks, and selected function table in `ras_core->ras_mp1`. No persistence is owned here.

Dependencies and integration: `ras_eeprom_fw.c` also uses `ras_mp1.sys_func` for EEPROM firmware messages, while ACA paths use bank count/dump operations. Risks include wrapper calls with null `ip_func` if initialization failed, unsupported MP1 IP versions halting `ras_core_hw_init()`, and system callback implementations having firmware-specific side effects. Test signals should initialize supported and unsupported IP versions, missing `mp1_sys_fn`, missing specific MP1 callbacks, CE/DE/UE bank queries, and firmware feature discovery using the same MP1 system function block.
