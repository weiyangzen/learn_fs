# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_nvm.c

## Purpose
`ice_nvm.c` implements the ICE driver's low-level NVM/flash access and version discovery path. It wraps Admin Queue NVM commands, provides flat flash and Shadow RAM readers, discovers flash bank geometry, extracts active/inactive NVM, Option ROM, and netlist version data, validates checksums, and exposes firmware update staging/activation commands.

## Important APIs, Types, and Functions
- AdminQ wrappers: `ice_aq_read_nvm()`, `ice_aq_update_nvm()`, `ice_aq_erase_nvm()`, `ice_nvm_write_activate()`, `ice_aq_nvm_update_empr()`, `ice_nvm_set_pkg_data()`, and `ice_nvm_pass_component_tbl()`.
- Locking helpers: `ice_acquire_nvm()` and `ice_release_nvm()` acquire/release `ICE_NVM_RES_ID`, except in blank NVM mode.
- Read helpers: `ice_read_flat_nvm()`, `ice_read_sr_word_aq()`, `ice_read_sr_word()`, `ice_read_flash_module()`, `ice_read_nvm_module()`, `ice_read_nvm_sr_copy()`, and `ice_read_netlist_module()`.
- Discovery/version helpers: `ice_discover_flash_size()`, `ice_determine_active_flash_banks()`, `ice_determine_css_hdr_len()`, `ice_get_nvm_ver_info()`, `ice_get_orom_civd_data()`, `ice_get_orom_ver_info()`, and `ice_get_netlist_info()`.
- Public version readers: `ice_get_inactive_nvm_ver()`, `ice_get_inactive_orom_ver()`, and `ice_get_inactive_netlist_ver()`.
- PFA/PBA helpers: `ice_get_pfa_module_tlv()` walks Preserved Field Area TLVs and `ice_read_pba_string()` decodes the part number string.

## Control Flow
Initialization enters through `ice_init_nvm()`: it reads `GLNVM_GENS` for Shadow RAM size, checks `GLNVM_FLA_LOCKED_M` to reject unsupported blank mode, discovers flash size by bisection, determines active banks and module sizes from Shadow RAM control words, computes CSS header lengths for active/inactive NVM banks, then fills `hw->flash.nvm`, `hw->flash.orom`, and `hw->flash.netlist` from active bank contents. Reads are serialized through `ice_acquire_nvm()`, split by `ice_read_flat_nvm()` into 4 KiB AdminQ/sector-sized commands, and dispatched by `ice_aq_read_nvm()`.

Inactive version reads are bank-relative: `ice_get_flash_bank_offset()` maps active vs inactive NVM/OROM/netlist modules from cached `hw->flash.banks` pointers and sizes, and the specific version helpers read from that computed offset. Option ROM versioning reads the full OROM bank into a `vzalloc()` buffer and scans 512-byte boundaries for a valid `$CIV` record with a zero modulo checksum. Netlist versioning validates the link topology module and reads the netlist ID block in one flash read.

## State and Persistence
The code does not persist data itself, but it mutates the in-memory hardware state in `hw->flash`: Shadow RAM word count, blank mode flag, total flash size, active-bank selection, module pointers/sizes, CSS header lengths, and active version structures. Firmware update functions modify device NVM state through AdminQ commands and may trigger activation or EMP reset behavior. The caller must treat flash writes/activation as persistent hardware changes.

## Dependencies and Integration Points
This file depends on `ice_common.h`, AdminQ descriptor layouts/opcodes, `ice_osdep.h` register and debug helpers, Linux allocation APIs (`kcalloc`, `vzalloc`, `vfree`), endianness helpers, overflow helpers, and `ice_hw_to_dev()` for warnings. It integrates with probe/init through `ice_init_nvm()`, devlink/ethtool style version display through version readers, PBA access through `ice_read_pba_string()`, and firmware update flows through package/component/activate AdminQ commands.

## Risks
NVM access is hardware-stateful and timing-sensitive. Incorrect bank pointer/size interpretation can read the wrong bank or expose inactive pending firmware incorrectly. `ice_read_flat_nvm()` may partially update caller buffers before returning an error. Several parsers assume firmware-provided layouts and use raw casts to little-endian data, so malformed flash data can lead to rejected initialization or misleading version data. OROM scanning allocates the full OROM bank and can fail under memory pressure. Update commands have persistent device impact and must be sequenced with firmware expectations.

## Test Signals
Good signals include successful `ice_init_nvm()` on supported hardware, correct active/inactive version reporting before and after staged updates, checksum validation success/failure coverage, PBA TLV parsing including malformed TLV length/overflow cases, flat NVM reads crossing 4 KiB boundaries, and firmware update command error propagation. Fault injection around AdminQ failures, invalid Shadow RAM control words, missing CIVD records, and short netlist modules would exercise the main defensive paths.
