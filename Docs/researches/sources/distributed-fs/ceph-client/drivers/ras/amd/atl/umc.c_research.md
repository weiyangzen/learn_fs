# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/umc.c

Purpose: handles UMC-specific address translation inputs, especially MI300. It maps MCA UMC error addresses and IPIDs to normalized addresses, coherent-station instances, socket/die IDs, and ultimately system physical addresses. It also supports MI300 DRAM row retirement.

Important APIs and functions: `get_umc_info_mi300()` caches MI300 hash and bit-placement registers. `convert_umc_mca_addr_to_sys_addr(struct atl_err *err)` is the main translation entry used via RAS ATL registration. `amd_retire_dram_row(struct atl_err *a_err)` is exported. Important helpers include `get_coh_st_inst_id_mi300()`, `convert_dram_to_norm_addr_mi300()`, `_retire_row_mi300()`, `retire_row_mi300()`, `get_die_id()`, `get_coh_st_inst_id()`, and `get_addr()`.

Control flow: MI300 initialization reads UMC address hash, address configuration, column selection, and address selection registers from node 0 UMC 0, then stores decoded XOR and bit-shift values globally. For translation, the function derives socket from topology, die from topology or MI300 IPID high bits, coherent-station ID from IPID or MI300 map, and normalized address from MCA_ADDR or MI300 DRAM reconstruction. It tries PRM first and falls back to software `norm_to_sys_addr()` unless the platform is PRM-only.

State and persistence: `addr_hash` and `bit_shifts` are global runtime caches. No persistent storage is owned. Row retirement mutates the input address while iterating column permutations and row bit 13.

Dependencies and integration: depends on SMN register reads, topology helpers, page lookup, `memory_failure()`, PRM wrapper in `prm.c`, DF config from `system.c`, and the software ATL translation path.

Risks: MI300 tables and bit shifts are hardware-specific. `WARN_ON_ONCE()` catches unknown UMC IDs but still returns an index value. Row retirement can be expensive because it checks all column permutations twice. PRM return handling must distinguish valid high physical addresses from error values.

Test signals: MI300 SMN-read failure, known MI300 IPID-to-coherent-station mappings, hash enabled/disabled conversions, PRM success, software fallback, PRM-only failure, invalid/offline pages during row retirement, and duplicate row-bit coverage.
