# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.c

## Purpose
This file fills `struct adf_hw_device_data` for QAT 4xxx/401xx/402xx PF devices. It describes Gen4 AE grouping, firmware object layouts, capability masks, service-to-firmware selection, rate-limiting metadata, ring pair reset/bank state hooks, PF/VF messaging, telemetry, RAS, PM, compression operations, and firmware-loader callbacks.

## Important APIs, Types, And Functions
The exported functions are `adf_init_hw_data_4xxx()` and `adf_clean_hw_data_4xxx()`. Important helpers include `get_ae_mask()`, `get_accel_cap()`, `get_fw_config()`, `uof_get_name_*()`, `uof_get_obj_type()`, `uof_get_ae_mask()`, `get_rp_group()`, `get_ena_thd_mask*()`, `adf_get_arbiter_mapping()`, `adf_init_rl_data()`, and `adf_gen4_set_err_mask()`.

## Control Flow
Initialization populates common numeric limits, ring layout, IRQ callbacks, Gen4 BAR helpers, admin communication, arbiter, interrupts, reset, admin AE mask, firmware names, UOF object accessors, SR-IOV, bank-state save/restore, PM, timer, heartbeat, service support, and capability extension flags. It branches on PCI device ID so 402xx uses `qat_402xx_*` firmware and 401xx uses a wider asym thread mask. Capability calculation reads service config and fuse fields, then removes disabled cipher/auth/UCS/PKE/compression/SMX slices before returning only capabilities relevant to the configured service mix.

## State And Persistence Behavior
The file mutates only the runtime `hw_data` object and the static class instance count. Firmware configuration arrays are constant. The resulting callbacks persist for the device lifetime and drive later init/start/reset/firmware-load paths.

## Dependencies And Integration Points
It depends on Gen4 common helpers, admin messaging, config services, clock/timer, bank state, PF/VF communication, RAS, PM, telemetry, rate limiting, VF migration, compression, and firmware config definitions. It is consumed by the 4xxx PCI driver and common accelerator-engine loader.

## Risks
Incorrect service-to-firmware mapping can load the wrong UOF image onto an AE group. Capability masks must track fuse semantics exactly because advertised Crypto API and compression features derive from them. The 401xx asymmetric thread special case is easy to regress. Class instance accounting is simple decrement-on-clean and assumes balanced init/clean.

## Test Signals
Test signals include successful firmware load for 4xxx/401xx/402xx SKUs, correct `/proc/crypto` and compression algorithm exposure for each `ServicesEnabled` combination, rate-limiting sysfs behavior, PF/VF messaging, bank-state save/restore across reset, Gen4 PM/debugfs entries, and fault handling through RAS/AER.
