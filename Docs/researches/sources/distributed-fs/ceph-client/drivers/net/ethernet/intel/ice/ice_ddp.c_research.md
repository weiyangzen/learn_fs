# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.c

## Purpose
`ice_ddp.c` implements Dynamic Device Personalization package handling. It validates package files, discovers the device-specific package segment and signing requirements, downloads package buffers to firmware under the global config lock, caches parser and tunnel metadata from package labels/sections, exposes package-buffer construction/update helpers, enumerates package sections and field vectors, derives switch profile metadata, and optionally applies Tx scheduler topology from runtime config segments.

## Important APIs, Types, And Functions
Public entry points include `ice_init_pkg()`, `ice_copy_and_init_pkg()`, `ice_free_seg()`, `ice_is_init_pkg_successful()`, `ice_pkg_enum_section()`, `ice_pkg_enum_entry()`, `ice_get_sw_fv_bitmap()`, `ice_get_sw_fv_list()`, `ice_init_prof_result_bm()`, `ice_pkg_buf_alloc()`, `ice_pkg_buf_free()`, `ice_pkg_buf_reserve_section()`, `ice_pkg_buf_alloc_section()`, `ice_pkg_buf_alloc_single_section()`, `ice_pkg_buf_get_active_sections()`, `ice_pkg_buf()`, `ice_update_pkg_no_lock()`, `ice_update_pkg()`, `ice_aq_upload_section()`, and `ice_cfg_tx_topo()`.

Major internal helpers validate package and buffer bounds, enumerate buffers/sections/entries, find segments, map AQ errors to DDP states, acquire/release global package locks, send signed/config package hunks, inspect active firmware package info, scan labels for tunnel and DVM/SVM hints, fill enabled PTYPE bitmaps, and classify switch field-vector profiles as tunnel/non-tunnel types.

## Control Flow
`ice_init_pkg()` verifies package format and segment bounds, extracts metadata through `ice_init_pkg_info()`, checks signing segment requirements for the MAC type, validates package version and NVM compatibility through `ice_chk_pkg_compat()`, scans hints, downloads the package, retrieves active package info, maps already-loaded cases to specific states, and on success sets `hw->seg`, initializes package-related registers, fills block tables, fills hardware PTYPE bitmap, and records the max used switch profile index.

Download flow differs by signed package support. Signed packages search signing segments matching `hw->pkg_seg_id` and `hw->pkg_sign_type`, download signature buffers, then the referenced config buffer range, and set the "last" bit according to signing segment flags. Unsigned packages download the config segment's buffer table directly. Both paths skip metadata buffers, use AdminQ download package commands, retry security/signature-related failures briefly, and call VLAN-mode post-download actions. Global config locking prevents multiple PFs from downloading conflicting packages; `-EALREADY` is treated as an already-loaded package condition.

Section enumeration is stateful: callers start with an `ice_seg`, then pass `NULL` to continue. Section and entry helpers validate section count, `data_end`, offsets, sizes, and handler-specific counts before returning package pointers. Tx topology flow validates firmware support and current flags, verifies runtime config package structure, extracts a 5-layer topology section when needed, acquires the global config lock, sends topology through AdminQ, triggers CORE reset, and reinitializes hardware.

## State And Persistence
The file mutates `struct ice_hw` package state: package versions/names, active package info, package copy pointer and size, `hw->seg`, signing identifiers, tunnel hint tables, DVM update tables, switch profile result bitmaps, hardware PTYPE bitmap, block tables, and scheduler topology. Firmware-visible persistence includes downloaded package state, package updates, VLAN mode configuration, and Tx topology changes that require CORE reset. `ice_copy_and_init_pkg()` owns a device-managed package copy until `ice_free_seg()`.

## Dependencies And Integration Points
It depends on AdminQ package opcodes, resource locks (`ICE_GLOBAL_CFG_LOCK_RES_ID`, change lock), `ice_common.h`, `ice_sched.h`, package structures from `ice_ddp.h`, parser/switch block table code (`ice_fill_blk_tbls()`), VLAN mode helpers, reset/deinit/init hardware paths, bitmap/list APIs, and device-managed allocation. Flow director, switch recipe, tunnel, VLAN, and scheduler code consume the package-derived field vectors, labels, PTYPEs, and result bitmaps.

## Risks
DDP package parsing is binary and bounds-sensitive; every segment, buffer, section, and handler count must remain validated before pointer arithmetic. Multi-PF races require correct global lock handling and already-loaded interpretation. Signed package behavior depends on matching segment ID and signing type by MAC family. Package load may succeed with a compatible but different package already active, which callers must distinguish. Tx topology update is disruptive because it issues CORE reset and reinitializes hardware. Metadata buffers intentionally terminate download sequences; mishandling this can send invalid data to firmware.

## Test Signals
Use package fixtures for invalid format versions, truncated segment arrays, bad section offsets/sizes, unsupported package versions, NVM mismatch, missing metadata, signed and unsigned packages, metadata-buffer termination, already-loaded package states, AQ security/signature failures, tunnel/DVM/SVM label scanning, switch field-vector lookup, package update/upload helpers, and Tx topology transitions including already-applied, lock contention, reset-in-progress, and hardware reinit failure.
