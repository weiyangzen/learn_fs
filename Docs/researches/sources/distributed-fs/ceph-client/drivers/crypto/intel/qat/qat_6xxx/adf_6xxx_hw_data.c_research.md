# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.c

## Purpose
This file defines Gen6 QAT hardware metadata. It maps service strings to ring pairs and AE thread masks, chooses firmware objects for standard and wireless-crypto SKUs, computes capability masks from fuses, initializes virtual channels, PM, RAS, telemetry, anti-rollback, rate limiting, compression request templates, and all common lifecycle callbacks in `struct adf_hw_device_data`.

## Important APIs, Types, And Functions
The exported functions are `adf_init_hw_data_6xxx()` and `adf_clean_hw_data_6xxx()`. Important local pieces are `struct adf_ring_config`, `services_supported()`, `wcy_services_supported()`, `get_rp_config()`, `adf_gen6_get_arb_mask()`, `get_ring_to_svc_map()`, `get_accel_cap()`, `get_accel_cap_wcy()`, `reset_ring_pair()`, `ring_pair_reset()`, `build_comp_block()`, `build_decomp_block()`, `adf_gen6_set_vc()`, `adf_init_device()`, `enable_pm()`, `dev_config()`, and `adf_gen6_init_*()` helpers.

## Control Flow
Initialization populates one accelerator, 64 Gen6 ring-pair banks, 2 rings per bank, Gen6 BAR callbacks, admin/arbiter/interrupt/reset hooks, firmware-loader accessors, bank-state save/restore, PM/init-device hooks, capability extension flags, DC ops, PF/VF ops, RAS/TL/RL, and anti-rollback data. Service mapping is dynamic: it parses `ServicesEnabled`, assigns all ring pairs for one service, alternating ring-pair groups for two services, and one or more ring pairs for three services. Standard SKUs load CY/DC/admin firmware; wireless SKUs load WCY/admin firmware and accept only symmetric service.

## State And Persistence Behavior
The file mutates only runtime `hw_data`, including masks, callback tables, RL/TL/RAS/anti-rollback substructures, and class instance count. Virtual-channel programming and power-up state are written to PCI config and CSR space during device init.

## Dependencies And Integration Points
It depends on Gen6 shared CSR helpers, admin messages, config services, firmware config, bank state, PM/RAS/TL, timer, compression firmware formats, QAT hardware masks, and common BAR helpers. It is consumed by the Gen6 PCI driver and common init/firmware paths.

## Risks
Ring/service/thread masks are tightly coupled; an incorrect map routes requests to incapable AE threads. WCY SKU detection depends on fuse semantics. VC and ring-mode programming must run after PF FLR. Capability masking drives algorithm exposure, so fuse-bit mistakes produce unsupported operations. Ring-pair reset has a 5-second polling timeout.

## Test Signals
Signals include valid `ServicesEnabled` parsing for one/two/three services, rejection of unsupported mixes and WCY non-sym service, correct firmware object load, functioning compression/ZSTD contexts, virtual-channel CSR programming after FLR, ring-pair reset, PM debugfs, anti-rollback SVN status, rate-limit values, and algorithm registration matching fuses.
