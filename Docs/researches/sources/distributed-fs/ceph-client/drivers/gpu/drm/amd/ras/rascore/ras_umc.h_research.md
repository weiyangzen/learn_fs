# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.h

Purpose: this header defines UMC memory types, address structures, IP conversion callbacks, bad-page storage structures, UMC runtime state, and public UMC APIs.

Important types and macros: VRAM constants cover GDDR, DDR, HBM, LPDDR, and HBM3E. `enum umc_memory_partition_mode` defines NPS modes. `struct umc_mca_addr`, `umc_phy_addr`, and `umc_bank_addr` represent MCA, physical, and decoded bank forms. `struct ras_umc_ip_func` supplies IP-specific conversions between banks, SOC PA, EEPROM records, NPS records/pages, and MCA IPID parsing. `struct eeprom_store_record`, `ras_umc_err_data`, and `ras_umc` track persisted-style records, expanded RAM bad-page records, locks, radix tree, and pending ECC list.

Control flow and state: no implementation lives here. The exported APIs initialize/finalize UMC, convert addresses, log bad banks, load/save/clean bad-page data, query records/counts, and translate between SOC PA and bank fields.

Dependencies and integration: includes `ras.h`, `ras_eeprom.h`, and `ras_cmd.h`; interacts with ACA, EEPROM, PSP TA, NBIO NPS mode, and core notifications. Risks are contract-related: each supported UMC IP must implement all callbacks that generic code assumes, and record fields contain both serialized and runtime-only interpretations. Test signals should include callback-null handling, structure field population from firmware and physical EEPROM records, and public query behavior before and after `ras_umc_clean_badpage_data()`.
