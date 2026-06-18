# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.h

## Purpose
`ice_nvm.h` is the public NVM interface for the ICE driver. It declares the packed Option ROM CIVD structure and the NVM, Shadow RAM, version, checksum, erase/write, package-data, and activation APIs implemented by `ice_nvm.c`.

## Important APIs, Types, and Functions
- `struct ice_orom_civd_info` describes the `$CIV` Option ROM combo-image version record: signature, checksum, combo version, name length, and UTF-16 combo name.
- Resource APIs: `ice_acquire_nvm()` and `ice_release_nvm()`.
- Read APIs: `ice_aq_read_nvm()`, `ice_read_flat_nvm()`, `ice_read_sr_word()`, `ice_get_pfa_module_tlv()`, and `ice_read_pba_string()`.
- Version/init APIs: `ice_init_nvm()`, `ice_get_inactive_orom_ver()`, `ice_get_inactive_nvm_ver()`, and `ice_get_inactive_netlist_ver()`.
- Write/update APIs: `ice_aq_update_nvm()`, `ice_aq_erase_nvm()`, `ice_nvm_validate_checksum()`, `ice_nvm_write_activate()`, `ice_aq_nvm_update_empr()`, `ice_nvm_set_pkg_data()`, and `ice_nvm_pass_component_tbl()`.

## Control Flow
The header is included by ICE common and update code that needs NVM access. It separates direct AdminQ command wrappers from higher-level helpers, so callers can either perform raw module operations or use parsed version/PBA/init routines. The update declarations indicate a multi-stage flow: set package data, pass component tables, write/update/erase as needed, validate checksum, activate, and optionally request EMP reset.

## State and Persistence
The header declares functions that mutate `struct ice_hw` flash cache and, for update paths, persistent device NVM. It does not define storage. Persistent state is entirely in hardware flash and Shadow RAM, while runtime state is held in `hw->flash`.

## Dependencies and Integration Points
The declarations rely on ICE core types from surrounding headers: `struct ice_hw`, AdminQ resource access enums, `struct ice_sq_cd`, and version structures such as `struct ice_orom_info`, `struct ice_nvm_info`, and `struct ice_netlist_info`. It is the integration point between NVM implementation and driver initialization, diagnostics, and firmware update paths.

## Risks
Because the API exposes both safe parsed helpers and raw AdminQ update/erase commands, caller misuse can cause persistent NVM changes. Buffer lengths and pointer validity are caller responsibilities for low-level read/write functions. `struct ice_orom_civd_info` is packed and hardware-layout-dependent, so changes must match firmware layout exactly.

## Test Signals
Compile coverage should ensure all callers include this header without incomplete type issues. Runtime tests should exercise every public declaration through initialization, version read, checksum validation, and firmware update error paths. ABI-sensitive tests should verify `sizeof(struct ice_orom_civd_info)` and field offsets against firmware documentation.
