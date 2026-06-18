# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.c

## Purpose
This file initializes the hardware abstraction table for Intel QAT 420xx devices. It defines firmware object layouts, acceleration-engine masks, feature capability calculation, rate-limit data, firmware object callbacks, error masks, and gen4 operation hooks assigned into `struct adf_hw_device_data`.

## Important APIs, Types, And Functions
- Firmware object tables: `adf_420xx_fw_objs[]` names sym/asym/DC/admin objects; `adf_fw_*_config[]` map AE groups to firmware objects for service modes such as SYM_ASYM, DC, DCC, SYM, ASYM, ASYM_DC, and SYM_DC.
- AE masks: `get_ae_mask()` masks off fused-out AE groups based on `ADF_FUSECTL4`; `update_ae_mask()` intersects physical AE availability with the selected firmware service layout.
- Firmware callbacks: `uof_get_num_objs()`, `get_fw_config()`, `uof_get_name_420xx()`, `uof_get_obj_type()`, and `uof_get_ae_mask()` describe firmware images and AE assignment to common QAT loader code.
- Capability calculation: `get_accel_cap()` reads `ADF_GEN4_FUSECTL1_OFFSET`, clears capabilities for fused-off slices, and filters the final mask by enabled service mode.
- Arbiter/ring helpers: `adf_get_arbiter_mapping()`, `get_rp_group()`, and `get_ena_thd_mask()` configure gen4 arbitration and thread masks.
- Rate limiting: `adf_init_rl_data()` fills token-bucket offsets, scale factors, max throughput, scan interval, slice reference, and service-AE counts.
- Error reporting: `adf_gen4_set_err_mask()` fills 420xx-specific parity/error masks.
- Public lifecycle: `adf_init_hw_data_420xx()` populates `struct adf_hw_device_data` with 420xx constants and many gen4 common function pointers; `adf_clean_hw_data_420xx()` decrements the class instance count.

## Control Flow
The 420xx PCI driver calls `adf_init_hw_data_420xx()` during device setup. That function sets counts, masks, firmware names, callbacks, reset/interrupt/admin/arbiter/PFVF/DC/RAS/TL/VF-migration/rate-limit hooks, and capability functions. Later common QAT code calls these hooks to derive AE masks, load the right firmware images, expose capabilities, configure ring services, manage power/heartbeat/timers, and handle resets/migration. Cleanup decrements the per-class instance counter.

## State And Persistence
The file writes runtime configuration into caller-owned `struct adf_hw_device_data`. Static firmware config arrays and the static `adf_420xx_class` persist for the module lifetime. Device capability state depends on PCI fuse registers and selected service configuration; it is not persisted outside runtime driver state.

## Dependencies And Integration Points
This file is tightly integrated with QAT common and gen4 infrastructure: `adf_accel_devices`, admin, bank state, cfg services, clock, firmware config, gen4 CSR/hardware/PFVF/PM/RAS/TL/VF migration, timers, and `icp_qat_hw` capability bits. It also relies on constants from `adf_420xx_hw_data.h`.

## Risks
- Capability reporting is fuse and service-mode sensitive; any mismatch between firmware layout and capability mask can expose unsupported services or hide working ones.
- `update_ae_mask()` assumes `get_fw_config()` returns non-NULL when `uof_get_num_objs()` is nonzero; unexpected service values must remain impossible or guarded by callers.
- `get_rp_group()` has special handling for AE group 2 depending on whether the config pointer equals `adf_fw_cy_config`; changes to config table identity may affect routing.
- `adf_clean_hw_data_420xx()` blindly decrements the class instance count; double cleanup would underflow logical instance accounting.

## Test Signals
- QAT 420xx probe tests for every service mode, verifying loaded firmware objects, AE masks, capabilities, and ring-to-service maps.
- Fuse simulation or hardware SKU coverage to ensure capability bits are cleared for disabled slices.
- Rate-limit tests for SYM/ASYM/DC throughput constants.
- Error injection/RAS tests to confirm the configured parity masks catch expected hardware errors.
