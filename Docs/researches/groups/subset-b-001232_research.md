# Research: subset-b-001232

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_drv.c

## Purpose
This is the PCI physical-function driver for Intel QAT 420xx devices. It binds the `PCI_DEVICE_ID_INTEL_QAT_420XX` device, allocates an `adf_accel_dev`, initializes 420xx-specific Gen4 hardware metadata, maps device BARs, seeds the in-kernel QAT configuration table, and brings the accelerator up through the common `adf_dev_up()` lifecycle.

## Important APIs, Types, And Functions
The local entry points are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, and `adf_cleanup_accel()`. Probe calls `adf_devmgr_add_dev()`, `adf_init_hw_data_420xx()`, `adf_cfg_dev_add()`, `adf_gen4_cfg_dev_init()`, `adf_dbgfs_init()`, `adf_dev_up()`, and `adf_sysfs_init()`. The PCI driver also exposes `adf_sriov_configure` and `adf_err_handler` through the common QAT framework.

## Control Flow
Probe rejects invalid NUMA placement, allocates device and hardware-data objects with `devm_kzalloc()`, reads PCI revision and Gen4 fuse state, computes accelerator/AE masks, creates config, enables PCI, installs a 64-bit DMA mask, initializes Gen4 default services, obtains capability masks, maps memory BARs selected by `ADF_GEN4_BAR_MASK`, saves PCI state, initializes debugfs, starts the device, and adds sysfs. Error paths stop the device if needed, remove debugfs/config/device-manager state, and clean 420xx hw data.

## State And Persistence Behavior
All state is volatile kernel state anchored in `struct adf_accel_dev`, its `hw_device`, PCI BAR mappings, config table, debugfs directory, sysfs entries, and common framework status bits. Firmware names are advertised with `MODULE_FIRMWARE()` but no data is persisted by this file.

## Dependencies And Integration Points
The file depends on PCI core, DMA mapping, Gen4 config/hardware helpers, the common QAT device manager, debugfs, sysfs, AER, SR-IOV, and the 420xx hardware-data module. It imports the `CRYPTO_QAT` namespace and soft-depends on `crypto-intel_qat`.

## Risks
The AE-mask validation assumes AE0/admin availability semantics inherited from Gen4 code. Any mismatch between BAR order, 420xx hardware metadata, or firmware files can fail probe. `adf_shutdown()` assumes `adf_devmgr_pci_to_accel_dev()` returns a device and does not null-check before `adf_dev_down()`.

## Test Signals
Useful signals are successful PCI probe, firmware load of `qat_420xx.bin` and `qat_420xx_mmp.bin`, `qat_dev*` sysfs/debugfs creation, crypto/compression registration depending on configured services, SR-IOV enable/disable, FLR/AER recovery, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/Makefile

## Purpose
This Kbuild fragment builds the QAT 4xxx PCI physical-function module. It connects `CONFIG_CRYPTO_DEV_QAT_4XXX` to the `qat_4xxx.o` kernel object and declares that object as the combination of the PCI driver (`adf_drv.o`) and generation-specific hardware metadata (`adf_4xxx_hw_data.o`).

## Important APIs, Types, And Functions
There are no runtime APIs in the Makefile. The important build contract is `obj-$(CONFIG_CRYPTO_DEV_QAT_4XXX) += qat_4xxx.o` plus `qat_4xxx-y := adf_drv.o adf_4xxx_hw_data.o`.

## Control Flow
Kbuild includes this module only when the matching config symbol is enabled. At link time it combines the probe/remove module and the hardware-data callbacks into one loadable or built-in kernel object.

## State And Persistence Behavior
The file has no runtime state. Its persistent effect is the compiled module membership and therefore which initialization functions and firmware declarations are present in the kernel build.

## Dependencies And Integration Points
It integrates with the top-level QAT Kconfig/Makefile and with `qat_common`, which provides the shared symbols imported by `adf_drv.o` and `adf_4xxx_hw_data.o`.

## Risks
If either object is omitted, the module will either lack PCI binding or lack required `adf_init_hw_data_4xxx()` symbols. Incorrect config gating can build a driver for unsupported kernels or omit support for 4xxx hardware.

## Test Signals
Build signals are successful compilation with `CONFIG_CRYPTO_DEV_QAT_4XXX`, a resulting `qat_4xxx` module/object, and module metadata that includes the 4xxx firmware declarations from `adf_drv.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.h

## Purpose
This header defines QAT 4xxx hardware constants used by the 4xxx hardware-data implementation and PCI driver. It names accelerator-engine limits, AE/admin masks, parity/error feature masks, firmware binaries for 4xxx and 402xx variants, rate-limiting constants, and AE frequency.

## Important APIs, Types, And Functions
The public functions are `adf_init_hw_data_4xxx(struct adf_hw_device_data *hw_data, u32 dev_id)` and `adf_clean_hw_data_4xxx(struct adf_hw_device_data *hw_data)`. Constants include `ADF_4XXX_MAX_ACCELENGINES`, `ADF_4XXX_ACCELENGINES_MASK`, `ADF_4XXX_ADMIN_AE_MASK`, firmware names such as `ADF_4XXX_FW`, `ADF_402XX_FW`, and RL constants such as `ADF_4XXX_RL_MAX_TP_SYM`.

## Control Flow
The header has no runtime control flow. Its values are read by `adf_4xxx_hw_data.c` during hardware-data initialization, firmware-object selection, error-mask setup, and rate-limiting setup.

## State And Persistence Behavior
There is no mutable state. The constants become compile-time ABI between device-specific code and the common QAT framework.

## Dependencies And Integration Points
It includes Linux unit helpers and `adf_accel_devices.h`. It is integrated with Gen4 common code, firmware loading, error handling, and the PCI driver's `MODULE_FIRMWARE()` declarations.

## Risks
Firmware-name or mask drift causes probe or firmware loading failures that may only appear on specific SKUs. Error-mask constants are hardware-contract values; wrong bits can hide parity faults or report false errors. Throughput/RL constants affect throttling behavior.

## Test Signals
Build coverage validates declarations. Runtime signals include successful 4xxx/402xx firmware requests, correct AE/admin masks, expected rate-limit capacities, and error/RAS handling that matches documented hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_4xxx_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_drv.c

## Purpose
This is the PCI PF driver for QAT 4xxx, 401xx, and 402xx devices. It handles PCI discovery, validates NUMA and fused accelerator presence, attaches device-specific hardware metadata, configures PCI/DMA/BAR resources, and starts the accelerator through the shared QAT framework.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, and `adf_cleanup_accel()`. The PCI table binds `PCI_DEVICE_ID_INTEL_QAT_4XXX`, `PCI_DEVICE_ID_INTEL_QAT_401XX`, and `PCI_DEVICE_ID_INTEL_QAT_402XX`. The `pci_driver` supplies SR-IOV and AER callbacks through `adf_sriov_configure` and `adf_err_handler`.

## Control Flow
Probe allocates `adf_accel_dev` and `adf_hw_device_data`, registers with `adf_devmgr_add_dev()`, initializes 4xxx hw data with the PCI device ID, reads revision and fuse data, computes masks/SKU, creates config, enables PCI, sets a 64-bit DMA mask, seeds Gen4 config, derives capability masks, requests and maps Gen4 memory BARs, saves PCI state, enables RAS accounting, initializes debugfs, calls `adf_dev_up(accel_dev, true)`, and initializes sysfs. Remove and shutdown call `adf_dev_down()` before cleanup.

## State And Persistence Behavior
Device state persists only while the PCI device is bound: `accel_dev`, its config table, debugfs/sysfs nodes, hardware callback table, PCI BAR mappings, and framework status bits. `pcim_*`/`devm_*` resources are tied to device lifetime, while common framework resources are explicitly cleaned.

## Dependencies And Integration Points
The driver relies on Linux PCI/DMA, Gen4 config, 4xxx hardware data, QAT device manager, debugfs/sysfs, AER, SR-IOV, common init/shutdown, and firmware files declared by `MODULE_FIRMWARE()`.

## Risks
Failure unwind must remove the device from the manager after it has been added. Capability validation happens before BAR mapping but after config, so config cleanup matters on early errors. `adf_shutdown()` lacks a null check on the device-manager lookup. Firmware declarations must match `adf_4xxx_hw_data.c` selection.

## Test Signals
Probe logs, BAR mappings, `qat_dev*` status via ioctl/sysfs, `dev_cfg` debugfs, algorithm registration, firmware load by SKU, SR-IOV VF creation/removal, AER/FLR restart, and clean unload are the main test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/Makefile

## Purpose
This Kbuild fragment defines the QAT Gen6 PF module. It compiles `qat_6xxx.o` when `CONFIG_CRYPTO_DEV_QAT_6XXX` is enabled and links the PCI driver with Gen6 hardware metadata.

## Important APIs, Types, And Functions
The build declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_6XXX) += qat_6xxx.o` and `qat_6xxx-y := adf_drv.o adf_6xxx_hw_data.o`. There are no runtime functions in this file.

## Control Flow
Kbuild conditionally includes the module in the kernel build. At module load, runtime control begins in the linked `adf_drv.c` PCI driver.

## State And Persistence Behavior
The Makefile has no runtime state. It persistently controls whether Gen6 probe, hardware data, firmware declarations, and callbacks are present in the built kernel/module.

## Dependencies And Integration Points
It integrates with top-level QAT Kconfig and `qat_common`, including Gen6 shared helpers, firmware loading, PF/VF communication, and common accelerator lifecycle code.

## Risks
Omitting either object breaks the module: the PCI object needs `adf_init_hw_data_6xxx()` and the hardware-data object depends on the PCI module to call it. Incorrect config wiring would silently omit Gen6 hardware support.

## Test Signals
Build output should include a `qat_6xxx` module/object with no unresolved common QAT symbols. Runtime confirmation is a Gen6 PCI ID binding and firmware requests for `qat_6xxx.bin` and `qat_6xxx_mmp.bin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.h

## Purpose
This header captures Gen6 QAT hardware constants: BAR layout, fuse offsets, bank/ring geometry, admin mailbox offsets, interrupt masks, watchdog timers, ring-pair reset CSRs, virtual-channel PCI config fields, error masks, firmware names, rate-limit constants, slice fuse bits, and the helper that detects wireless-crypto SKUs.

## Important APIs, Types, And Functions
Public declarations are `adf_init_hw_data_6xxx()` and `adf_clean_hw_data_6xxx()`. The important inline helper is `adf_6xxx_is_wcy()`, which tests `ICP_ACCEL_GEN6_MASK_WCP_WAT_SLICE` in `ADF_FUSECTL1`. The `enum icp_qat_gen6_slice_mask` names fuse bits used to remove advertised capabilities.

## Control Flow
The header itself has no runtime control flow except the inline WCY predicate. Its constants drive BAR mapping in `adf_drv.c`, CSR writes and polling in `adf_6xxx_hw_data.c`, admin mailbox setup in `adf_admin.c`, and firmware loader selections.

## State And Persistence Behavior
There is no mutable state. The values become compile-time hardware contracts. Runtime state arises when the implementation writes these offsets/masks into device CSRs or populates `hw_data`.

## Dependencies And Integration Points
It includes Linux bit/time/unit helpers plus QAT acceleration/config/DC definitions. It integrates Gen6 PCI probing, firmware loading, PM, ring reset, VC setup, RAS, anti-rollback, and rate limiting.

## Risks
Wrong CSR offsets or masks can hang reset polling, misroute interrupts, break VC setup, or expose unsupported slices. The WCY predicate is a compact fuse interpretation and is high risk if hardware documentation changes.

## Test Signals
Build coverage validates declarations. Runtime signals include correct BAR mapping, successful admin mailbox communication, ring reset completion, VC config writes, watchdog programming, firmware request names, and capability exposure that changes correctly when fuse bits are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_drv.c

## Purpose
This is the PCI PF driver for Intel QAT Gen6 devices. It differs from older QAT probe code by using devm cleanup actions heavily, mapping fixed 64-bit BAR numbers, reading multiple fuse registers before hardware-data setup, and selecting default services based on SKU and device ID parity.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_shutdown()`, `adf_gen6_cfg_dev_init()`, and devm cleanup callbacks (`adf_device_down()`, `adf_dbgfs_cleanup()`, `adf_cfg_device_remove()`, `adf_cleanup_hw_data()`, `adf_devmgr_remove()`). The PCI table binds `PCI_DEVICE_ID_INTEL_QAT_6XXX`.

## Control Flow
Probe rejects invalid NUMA placement, allocates device and hw-data objects, reads revision and Gen6 fuse registers, enables PCI, registers the device manager entry, installs devm cleanup actions, initializes Gen6 hw data, computes accelerator/AE masks and SKU, creates config, sets a 64-bit DMA mask, writes default `ServicesEnabled` (`sym` for WCY, otherwise `dc` on odd accel IDs and `sym;asym` on even IDs), reads capability masks, maps SRAM/PMISC/ETR BARs with `pcim_iomap_region()`, saves PCI state, enables RAS, creates debugfs, starts the device, and creates sysfs.

## State And Persistence Behavior
Runtime state is in `adf_accel_dev`, `hw_data`, devm-managed cleanup stack, BAR mappings, config table, debugfs/sysfs, and framework status bits. The service default is stored in the volatile config table and affects firmware/capability setup.

## Dependencies And Integration Points
It integrates Linux PCI/DMA, Gen6 shared and hardware-data modules, heartbeat config, QAT config/device/debug frameworks, AER, SR-IOV, firmware loading, and sysfs.

## Risks
The default service split by `accel_id % 2` is policy-sensitive. The no-`remove` driver relies on devm actions for cleanup. `adf_dev_up()` failure manually calls `adf_dev_down()` before the devm down action is installed. `adf_shutdown()` also lacks a null check on device-manager lookup.

## Test Signals
Signals include successful probe with fixed BAR map 0/2/4, correct default service based on WCY and accel ID, firmware load, PM/VC initialization, AER/FLR recovery, SR-IOV behavior, sysfs/debugfs creation, and clean unbind/shutdown via devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/Makefile

## Purpose
This Kbuild fragment defines the C3xxx QAT PF module. It compiles the PCI driver and C3xxx hardware-data implementation when `CONFIG_CRYPTO_DEV_QAT_C3XXX` is enabled.

## Important APIs, Types, And Functions
The file declares `obj-$(CONFIG_CRYPTO_DEV_QAT_C3XXX) += qat_c3xxx.o` and `qat_c3xxx-y := adf_drv.o adf_c3xxx_hw_data.o`. There are no runtime functions.

## Control Flow
Kbuild conditionally links `adf_drv.o` and `adf_c3xxx_hw_data.o` into one `qat_c3xxx` module/object. Runtime control starts in the module init function in `adf_drv.c`.

## State And Persistence Behavior
No runtime state exists in this file. Its persistent effect is build composition for C3xxx PF support.

## Dependencies And Integration Points
The resulting object depends on `qat_common` exports, Gen2 common helpers, firmware loading, PCI core, and Kconfig selection.

## Risks
Removing either object breaks symbol resolution or runtime probing. Incorrect config names would omit C3xxx support from builds.

## Test Signals
Build `CONFIG_CRYPTO_DEV_QAT_C3XXX=m/y` and confirm a `qat_c3xxx` object includes both the PCI module and hardware-data callbacks, then probe a C3xxx PCI device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.c

## Purpose
This file initializes hardware metadata for C3xxx Gen2 QAT PF devices. It computes accelerator and AE masks from fuse/softstrap registers, defines fixed arbiter thread mapping, identifies SKU, measures AE clock, configures SR-IOV thread ownership, and wires common Gen2 lifecycle callbacks into `struct adf_hw_device_data`.

## Important APIs, Types, And Functions
The exported functions are `adf_init_hw_data_c3xxx()` and `adf_clean_hw_data_c3xxx()`. Important helpers include `get_accel_mask()`, `get_ae_mask()`, `get_ts_clock()`, `measure_clock()`, BAR ID callbacks, `get_sku()`, `adf_get_arbiter_mapping()`, and `configure_iov_threads()`.

## Control Flow
Initialization sets class/instance, 16 ETR banks, 16 rings per bank, 3 accelerators, 6 AEs, Gen2 ring layout, IRQ callbacks, error correction, mask/capability callbacks, BAR callbacks, admin/arbiter hooks, firmware names, Gen2 PF/VF ops, SSM watchdog, SR-IOV disable, Gen2 config, clock measurement, heartbeat counters, and DC/CSR ops. AE mask calculation disables two AEs for each disabled accelerator.

## State And Persistence Behavior
The file mutates only runtime `hw_data` and the static C3xxx class instance count. Fuse/strap-derived masks persist in `hw_data` for the bound device lifetime.

## Dependencies And Integration Points
It depends on Gen2 config, Gen2 CSR and hardware-data helpers, Gen2 PF/VF ops, admin communication, common QAT clock measurement, heartbeat, and firmware loader paths using `qat_c3xxx.bin` and `qat_c3xxx_mmp.bin`.

## Risks
Fuse/strap interpretation drives both accelerator mask and AE mask; a wrong shift or disabled-accelerator propagation misrepresents hardware. Clock measurement accepts a min/max range and affects heartbeat timing. Static arbiter maps must match firmware thread roles.

## Test Signals
Probe on C3xxx hardware should report SKU4 for 6 AEs, load firmware, register algorithms, measure clock within range, run heartbeat checks, support SR-IOV thread configuration, and survive reset/arbiter restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.h

## Purpose
This header defines C3xxx PF hardware constants: BAR IDs, accelerator and AE limits/masks, softstrap offset, ETR bank count, AE-to-function mapping register counts, clock frequency bounds, firmware names, and hardware-data init/clean declarations.

## Important APIs, Types, And Functions
Public declarations are `adf_init_hw_data_c3xxx()` and `adf_clean_hw_data_c3xxx()`. Important constants include `ADF_C3XXX_MAX_ACCELERATORS`, `ADF_C3XXX_MAX_ACCELENGINES`, `ADF_C3XXX_ACCELERATORS_REG_OFFSET`, `ADF_C3XXX_ETR_MAX_BANKS`, `ADF_C3XXX_MIN_AE_FREQ`, `ADF_C3XXX_MAX_AE_FREQ`, `ADF_C3XXX_FW`, and `ADF_C3XXX_MMP`.

## Control Flow
The header has no executable flow. Its constants are consumed by `adf_c3xxx_hw_data.c` and the C3xxx PCI probe code when reading softstraps, mapping BARs, validating clock measurements, and loading firmware.

## State And Persistence Behavior
No mutable state exists. The constants compile into C3xxx runtime callbacks and module firmware metadata.

## Dependencies And Integration Points
It includes Linux unit helpers and integrates with Gen2 QAT common code, PCI probing, firmware loading, and SR-IOV AE-to-function mapping.

## Risks
Incorrect mask or BAR IDs can prevent probe or misroute CSR access. Clock bounds that do not match silicon can reject valid devices or hide invalid timings. Firmware names must match installed firmware packages.

## Test Signals
Build coverage, successful PCI probe, firmware request for C3xxx binaries, correct 6-AE SKU detection, valid BAR access, and Gen2 SR-IOV mapping are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_drv.c

## Purpose
This is the PCI PF driver for C3xxx QAT devices. It provides module registration, PCI probe/remove/shutdown, manual memory/BAR cleanup, 48-bit DMA setup, device-manager registration, and common QAT device startup.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. The PCI driver exposes SR-IOV and AER callbacks via `adf_sriov_configure` and `adf_err_handler`.

## Control Flow
Module init requests `intel_qat`, then registers the PCI driver. Probe validates PCI ID and NUMA node, allocates `adf_accel_dev` and hw data with `kzalloc_node()`, registers the device manager entry, initializes C3xxx hw data, reads revision/fuse/softstrap registers, validates masks, creates config, enables PCI, sets a 48-bit DMA mask, requests regions, computes capabilities, maps all memory BARs, saves PCI state, initializes debugfs, and starts the device. Remove stops the device, unmaps BARs, removes config/debugfs/device-manager entries, releases PCI resources, and frees memory.

## State And Persistence Behavior
Runtime state is manually allocated and must be explicitly freed. Config/debugfs/framework state exists only while bound. PCI state is saved for reset recovery. There is no disk persistence.

## Dependencies And Integration Points
The driver depends on Linux PCI/DMA, C3xxx hardware data, Gen2 common QAT framework, debugfs, config, AER, SR-IOV, firmware, and `intel_qat` base module aliasing.

## Risks
Manual cleanup has several unwind labels and requires correct ordering. BAR indexing uses every selected memory BAR and can leave partially mapped resources on failure. `adf_shutdown()` assumes lookup success. DMA is limited to 48 bits, unlike Gen4/Gen6.

## Test Signals
Probe/remove cycles, firmware load, 48-bit DMA operation, device-manager status ioctl, debugfs `dev_cfg`, SR-IOV enable/disable, AER reset, and memory-leak/DMA-debug clean runs are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/Makefile

## Purpose
This Kbuild fragment builds the C3xxx virtual-function driver. It gates `qat_c3xxxvf.o` on `CONFIG_CRYPTO_DEV_QAT_C3XXXVF` and links VF PCI code with VF hardware metadata.

## Important APIs, Types, And Functions
The declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_C3XXXVF) += qat_c3xxxvf.o` and `qat_c3xxxvf-y := adf_drv.o adf_c3xxxvf_hw_data.o`. No runtime code is present.

## Control Flow
Kbuild includes the VF module only when configured. Runtime control starts in `adf_drv.c`, which registers a PCI VF driver for `PCI_DEVICE_ID_INTEL_QAT_C3XXX_VF`.

## State And Persistence Behavior
There is no runtime state in this file. It persistently controls module composition.

## Dependencies And Integration Points
The linked module depends on `qat_common`, Gen2 VF CSR/PFVF helpers, Linux PCI, and the matching PF driver when VFs are hosted locally.

## Risks
Incorrect object composition would omit VF-specific callbacks such as `adf_vf2pf_notify_init()` or break PCI binding.

## Test Signals
Build with C3xxx VF config, create SR-IOV VFs from a C3xxx PF or pass a VF into a guest, and confirm the `qat_c3xxxvf` driver binds and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.c

## Purpose
This file initializes hardware metadata for C3xxx virtual functions. A VF exposes one accelerator, one AE, one ETR bank, fixed TX/RX ring layout, VF interrupt callbacks, no local admin/arbiter/error-correction work, and PF/VF messaging for init/shutdown notification.

## Important APIs, Types, And Functions
Public functions are `adf_init_hw_data_c3xxxiov()` and `adf_clean_hw_data_c3xxxiov()`. Local helpers return fixed masks and BAR IDs (`get_accel_mask()`, `get_ae_mask()`, `get_num_accels()`, `get_num_aes()`, `get_misc_bar_id()`, `get_etr_bar_id()`, `get_sku()`), plus noop callbacks for unsupported PF-only operations.

## Control Flow
Initialization sets VF class data, bank/ring counts, fixed masks, Gen2 service map, VF ISR allocation/free callbacks, noop admin/arbiter/error-correction callbacks, `send_admin_init = adf_vf2pf_notify_init`, `disable_iov = adf_vf2pf_notify_shutdown`, Gen2 config, class index update, Gen2 VF PFVF ops, CSR ops, and DC ops. Cleanup decrements class instances and updates class indexes.

## State And Persistence Behavior
State is runtime-only in `hw_data` and the static VF class instance count. The VF relies on PF-mediated state through PF/VF messages rather than local firmware/admin ownership.

## Dependencies And Integration Points
It depends on Gen2 config/hw CSR/DC helpers, VF interrupt allocation, and PF/VF messaging helpers. The PCI VF driver calls these callbacks during probe/remove.

## Risks
Noop admin and arbiter callbacks mean common code must not assume PF-only resources on a VF. Fixed one-bank geometry must match hardware virtualization. Class index updates rely on device-manager ordering.

## Test Signals
VF probe should initialize one AE/one accelerator, exchange init/shutdown PF/VF messages, allocate VF interrupts, register crypto/compression instances appropriate to VF services, and clean up class indexes after VF removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.h

## Purpose
This header defines the fixed hardware geometry for C3xxx VFs: BAR IDs, one accelerator/AE, ring offsets, TX ring mask, one ETR bank, and hardware-data init/clean declarations.

## Important APIs, Types, And Functions
It declares `adf_init_hw_data_c3xxxiov()` and `adf_clean_hw_data_c3xxxiov()`. Important constants include `ADF_C3XXXIOV_PMISC_BAR`, `ADF_C3XXXIOV_ETR_BAR`, `ADF_C3XXXIOV_ACCELERATORS_MASK`, `ADF_C3XXXIOV_ACCELENGINES_MASK`, `ADF_C3XXXIOV_RX_RINGS_OFFSET`, `ADF_C3XXXIOV_TX_RINGS_MASK`, and `ADF_C3XXXIOV_ETR_MAX_BANKS`.

## Control Flow
There is no executable flow. The constants drive VF metadata initialization and PCI BAR indexing in the C3xxx VF driver.

## State And Persistence Behavior
No mutable state exists. Values compile into the VF module and establish the common framework's view of the VF.

## Dependencies And Integration Points
It is consumed by `adf_c3xxxvf_hw_data.c` and the C3xxx VF PCI driver. It integrates with Gen2 VF CSR and transport setup.

## Risks
Because VFs expose a constrained resource subset, wrong geometry values can corrupt ring setup or interrupt handling. The TX/RX offset and mask must stay synchronized with firmware/PF resource assignment.

## Test Signals
Successful VF probe, one-bank transport setup, TX/RX ring operation, PF/VF init/shutdown messages, and clean VF removal validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_drv.c

## Purpose
This is the PCI virtual-function driver for C3xxx QAT VFs. It binds VF PCI IDs, associates a VF with its PF when present, initializes VF-specific hardware metadata, maps VF BARs, starts the common QAT device lifecycle without PF-only initialization, and notifies the PF through PF/VF messaging.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. It uses `adf_init_hw_data_c3xxxiov()`, `adf_vf2pf_notify_init()`, `adf_vf2pf_notify_shutdown()`, `adf_flush_vf_wq()`, and `adf_clean_vf_map(true)`.

## Control Flow
Probe validates VF ID, allocates the device, marks it `is_vf`, looks up the physical PF by `pdev->physfn`, adds the VF to the device manager, initializes hw data and config, enables PCI, sets a 48-bit DMA mask, requests regions, maps memory BARs, sets bus master, initializes `vf.msg_received` completion, creates debugfs, and calls `adf_dev_up(accel_dev, false)`. Remove flushes VF work, stops the device, cleans common and PCI resources, and frees memory. Module exit unregisters the PCI driver and cleans VF ID mappings.

## State And Persistence Behavior
VF state is volatile and manually allocated. PF/VF response state lives in the `accel_dev->vf` union, including completion and temporary response. Device IDs are tracked in the common VF map for stable user-visible numbering.

## Dependencies And Integration Points
It integrates Linux PCI/DMA, Gen2 VF hardware data, QAT config/debugfs/device manager, PF/VF messaging, VF workqueues, and the common start/stop path.

## Risks
PF lookup may be null in guest-like scenarios and device-manager logic handles that differently from host VFs. Manual cleanup ordering is sensitive. VF operation depends on PF responses; failure to flush work on removal can race with teardown.

## Test Signals
Create/remove C3xxx VFs, bind them on host or guest, observe successful PF/VF init notification, run crypto/compression requests, remove while idle and under load, and verify VF map cleanup after module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/Makefile

## Purpose
This Kbuild fragment builds the QAT C62x PF module when `CONFIG_CRYPTO_DEV_QAT_C62X` is enabled. It links the PF PCI driver with C62x hardware metadata.

## Important APIs, Types, And Functions
The declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_C62X) += qat_c62x.o` and `qat_c62x-y := adf_drv.o adf_c62x_hw_data.o`. There are no runtime APIs.

## Control Flow
Kbuild conditionally composes the module. Runtime control starts in `adf_drv.c` module init and PCI probe.

## State And Persistence Behavior
No runtime state exists. The file persistently controls object composition for C62x support.

## Dependencies And Integration Points
The module links against `qat_common`, Gen2 helpers, Linux PCI, firmware loader code, and top-level QAT Kconfig.

## Risks
Incorrect object membership causes missing PCI binding or missing `adf_init_hw_data_c62x()` callbacks.

## Test Signals
Build with C62x config and confirm a `qat_c62x` module/object exists and can bind `PCI_DEVICE_ID_INTEL_QAT_C62X`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.c

## Purpose
This file initializes Gen2 C62x PF hardware metadata. It is structurally similar to the C3xxx file but describes up to five accelerators, ten AEs, C62x BAR IDs, C62x SKU rules, fixed arbiter maps, SR-IOV thread mapping dimensions, clock measurement range, and firmware names.

## Important APIs, Types, And Functions
Public functions are `adf_init_hw_data_c62x()` and `adf_clean_hw_data_c62x()`. Important helpers include `get_accel_mask()`, `get_ae_mask()`, `get_ts_clock()`, `measure_clock()`, `get_misc_bar_id()`, `get_etr_bar_id()`, `get_sram_bar_id()`, `get_sku()`, `adf_get_arbiter_mapping()`, and `configure_iov_threads()`.

## Control Flow
Initialization populates class/instance, bank/ring geometry, accelerator/AE counts, Gen2 ring service map, IRQ callbacks, Gen2 error correction/capabilities/CSR/DC/PFVF ops, BAR ID callbacks, SKU logic, firmware names, admin/arbiter callbacks, Gen2 interrupts, FLR reset, SSM watchdog, SR-IOV disable, config, clock measurement, heartbeat, and arbiter mapping. AE mask calculation disables two AEs per disabled accelerator derived from fuses/straps.

## State And Persistence Behavior
The mutable state is the runtime `hw_data` object and static C62x class instance count. Fuse/strap-derived masks and measured clock persist in memory for the device lifetime.

## Dependencies And Integration Points
It depends on Gen2 config, CSR, PF/VF, admin, clock, heartbeat, common driver, firmware loader, and compression operations. It is called by the C62x PCI driver.

## Risks
SKU detection depends solely on AE count: 8 maps to SKU2 and 10 to SKU4. Wrong fuse/strap or BAR constants affect the whole device. Static thread-to-arbiter maps must match firmware scheduling assumptions.

## Test Signals
Probe should report expected SKU for 8/10 AEs, measure AE clock within 533-800 MHz, load `qat_c62x` firmware, register algorithms, support SR-IOV thread mapping, and survive reset/heartbeat checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.h

## Purpose
This header defines C62x PF hardware constants for BAR layout, accelerator/AE masks, softstrap offset, ETR bank count, AE-to-function mapping register counts, AE frequency limits, firmware names, and hardware-data lifecycle declarations.

## Important APIs, Types, And Functions
It declares `adf_init_hw_data_c62x()` and `adf_clean_hw_data_c62x()`. Important constants include `ADF_C62X_MAX_ACCELERATORS`, `ADF_C62X_MAX_ACCELENGINES`, `ADF_C62X_ACCELERATORS_MASK`, `ADF_C62X_ACCELENGINES_MASK`, `ADF_C62X_ETR_MAX_BANKS`, `ADF_C62X_AE_FREQ`, `ADF_C62X_MIN_AE_FREQ`, `ADF_C62X_MAX_AE_FREQ`, `ADF_C62X_FW`, and `ADF_C62X_MMP`.

## Control Flow
No executable flow exists. The constants are used by C62x probe and hardware-data code to map BARs, compute masks, configure SR-IOV AE mapping, validate clocks, and request firmware.

## State And Persistence Behavior
No mutable state exists. The header provides compile-time hardware contracts.

## Dependencies And Integration Points
It includes Linux units and integrates with Gen2 QAT common code, firmware loading, PCI probing, and SR-IOV configuration.

## Risks
Incorrect BAR IDs or masks can break CSR access or misreport hardware resources. Clock bounds directly affect `adf_dev_measure_clock()` validation. Firmware names must match the kernel firmware package.

## Test Signals
Build coverage, C62x PCI probe, firmware request success, correct 8/10 AE SKU detection, clock measurement, and SR-IOV operation validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_drv.c

## Purpose
This is the PCI PF driver for C62x QAT devices. It performs PCI binding, manual allocation and cleanup, fuse/softstrap reading, 48-bit DMA setup, BAR mapping, debugfs/config/device-manager integration, and common accelerator startup.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_shutdown()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. The PCI table binds `PCI_DEVICE_ID_INTEL_QAT_C62X`.

## Control Flow
Module init requests the base `intel_qat` module and registers the PCI driver. Probe validates device ID and NUMA placement, allocates device and hw-data objects, registers with the device manager, initializes C62x hardware metadata, reads revision/fuse/softstrap registers, computes masks/SKU, creates config, enables PCI, sets a 48-bit DMA mask, requests regions, reads capabilities, maps memory BARs with an index offset when a fuse bit is set, saves PCI state, initializes debugfs, and calls `adf_dev_up(accel_dev, true)`. Remove stops and cleans all resources.

## State And Persistence Behavior
State is volatile and manually managed. PCI BAR mappings, config/debugfs entries, device-manager registration, saved PCI state, and status bits persist only while bound.

## Dependencies And Integration Points
The driver integrates Linux PCI/DMA, C62x hardware metadata, Gen2 QAT framework, config/debugfs, firmware loading, AER, SR-IOV, and common crypto/compression services.

## Risks
BAR indexing is conditional on `ADF_DEVICE_FUSECTL_MASK`, making resource mapping device-variant sensitive. Manual unwind paths must avoid leaks and double free. `adf_shutdown()` assumes the device-manager lookup succeeds.

## Test Signals
Probe/remove cycles, firmware load, C62x algorithm registration, 48-bit DMA, status ioctl, debugfs config, SR-IOV creation, AER reset, and DMA/memory sanitizer runs are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/Makefile

## Purpose
This Kbuild fragment builds the C62x virtual-function module. It gates `qat_c62xvf.o` on `CONFIG_CRYPTO_DEV_QAT_C62XVF` and links VF PCI code with C62x VF hardware metadata.

## Important APIs, Types, And Functions
The declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_C62XVF) += qat_c62xvf.o` and `qat_c62xvf-y := adf_drv.o adf_c62xvf_hw_data.o`. There are no runtime functions.

## Control Flow
Kbuild conditionally composes the VF module. Runtime control starts in `adf_drv.c` when a matching VF PCI device is probed.

## State And Persistence Behavior
No runtime state exists. The file controls module composition.

## Dependencies And Integration Points
The module depends on `qat_common`, Gen2 VF helpers, PCI core, and PF/VF messaging support.

## Risks
Incorrect composition can omit the VF metadata required by probe or PF/VF notifications.

## Test Signals
Build with C62x VF config, create or assign VFs, confirm `qat_c62xvf` binds, and run basic crypto/compression operations through the VF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.c

## Purpose
This file initializes C62x VF hardware metadata. It describes the VF as one accelerator, one AE, one ETR bank, fixed Gen2 ring layout, VF interrupt resources, no local admin/arbiter/error-correction operations, and PF/VF notification based startup/shutdown.

## Important APIs, Types, And Functions
Public functions are `adf_init_hw_data_c62xiov()` and `adf_clean_hw_data_c62xiov()`. Local fixed-return helpers provide masks, counts, BAR IDs, and `DEV_SKU_VF`. Noop functions are used for PF-only lifecycle callbacks.

## Control Flow
Initialization fills `hw_data` with VF class, bank/ring geometry, fixed service map, VF ISR callbacks, noops for admin/arbiter/error correction/interrupt enabling, PF/VF init and shutdown notifications, fixed resource callbacks, Gen2 device config, class index updates, VF PFVF ops, CSR ops, and DC ops. Cleanup decrements class instances and updates class indexes.

## State And Persistence Behavior
Runtime state is limited to `hw_data` and class instance count. Actual PF-owned state is coordinated over PF/VF messages rather than local admin firmware calls.

## Dependencies And Integration Points
It depends on Gen2 config, CSR/DC helpers, VF ISR code, and PF/VF VF-message helpers. It is used by the C62x VF PCI driver.

## Risks
The common framework must tolerate noops for PF-only operations. Any mismatch in one-bank ring geometry or TX/RX offset breaks VF transport. Class index updates depend on device-manager list consistency.

## Test Signals
Successful VF probe, PF/VF init/shutdown messaging, one-bank transport setup, interrupt delivery, algorithm registration, and class index cleanup on VF removal validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.h

## Purpose
This header defines fixed C62x VF geometry: PMISC and ETR BAR IDs, one accelerator/AE masks and counts, TX/RX ring placement, one ETR bank, and hardware-data init/clean declarations.

## Important APIs, Types, And Functions
It declares `adf_init_hw_data_c62xiov()` and `adf_clean_hw_data_c62xiov()`. Important constants include `ADF_C62XIOV_PMISC_BAR`, `ADF_C62XIOV_ETR_BAR`, `ADF_C62XIOV_ACCELERATORS_MASK`, `ADF_C62XIOV_ACCELENGINES_MASK`, `ADF_C62XIOV_RX_RINGS_OFFSET`, `ADF_C62XIOV_TX_RINGS_MASK`, and `ADF_C62XIOV_ETR_MAX_BANKS`.

## Control Flow
There is no executable flow. The constants are read by C62x VF metadata initialization and PCI BAR setup.

## State And Persistence Behavior
No mutable state exists. Values compile into the VF module.

## Dependencies And Integration Points
The header integrates with Gen2 VF CSR/transport setup and the C62x VF PCI driver.

## Risks
Wrong fixed geometry can corrupt ring programming or prevent interrupts. Since VFs have no firmware names here, the common framework relies on PF/VF coordination rather than local firmware state.

## Test Signals
VF bind/start, one-bank ring traffic, PF/VF notifications, and clean removal are indirect validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_drv.c

## Purpose
This is the PCI VF driver for C62x QAT virtual functions. It binds C62x VF PCI IDs, creates a VF `adf_accel_dev`, initializes VF metadata, maps PCI resources, starts the common QAT framework without PF-only init, and coordinates with the PF over PF/VF messages.

## Important APIs, Types, And Functions
Key functions are `adf_probe()`, `adf_remove()`, `adf_cleanup_accel()`, `adf_cleanup_pci_dev()`, `adfdrv_init()`, and `adfdrv_release()`. Important common calls include `adf_devmgr_add_dev()`, `adf_init_hw_data_c62xiov()`, `adf_cfg_dev_add()`, `adf_dev_up()`, `adf_flush_vf_wq()`, and `adf_clean_vf_map(true)`.

## Control Flow
Probe validates the VF device ID, allocates the VF, marks `is_vf`, locates the PF via `pdev->physfn`, adds it to the device manager, initializes hardware data, adds config, enables PCI, sets 48-bit DMA, requests regions, maps all memory BARs, enables bus mastering, initializes the PF/VF completion, initializes debugfs, and calls `adf_dev_up(accel_dev, false)`. Remove flushes VF work, stops the device, unmaps BARs, removes config/debugfs/device-manager state, releases PCI resources, and frees memory.

## State And Persistence Behavior
Runtime state is manually allocated and volatile. PF/VF messaging state is stored in `accel_dev->vf`; stable VF numbering is tracked by the common device manager's VF map.

## Dependencies And Integration Points
It integrates Linux PCI/DMA, C62x VF hardware data, Gen2 VF PFVF callbacks, debugfs, config, common QAT lifecycle, and the base `intel_qat` module.

## Risks
The VF depends on PF presence and response timing. Manual cleanup and workqueue flushing are race-sensitive. Like the C3xxx VF driver, it uses 48-bit DMA and maps all memory BARs in order.

## Test Signals
SR-IOV VF creation/removal, host and guest VF binding, PF/VF init/shutdown messages, crypto/compression traffic, hot-remove, and module unload with clean VF map are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/Makefile

## Purpose
This Kbuild fragment defines the shared `intel_qat` base module. It links the common accelerator framework, firmware loader, transport, algorithm providers, config/control paths, generation helpers, optional debugfs features, optional SR-IOV PF/VF messaging, and optional heartbeat error injection.

## Important APIs, Types, And Functions
The main declaration is `obj-$(CONFIG_CRYPTO_DEV_QAT) += intel_qat.o`. `intel_qat-y` includes core files such as `adf_init.o`, `adf_transport.o`, `adf_admin.o`, `adf_accel_engine.o`, `adf_ctl_drv.o`, crypto/compression algorithm files, HAL/UOF loader, and generation data helpers. Conditional lists add debugfs telemetry/heartbeat files, SR-IOV PF/VF code, and error injection.

## Control Flow
Kbuild assembles different common-module capabilities according to `CONFIG_DEBUG_FS`, `CONFIG_PCI_IOV`, and `CONFIG_CRYPTO_DEV_QAT_ERROR_INJECTION`. Runtime module initialization is in `adf_ctl_drv.c`, which creates the control character device and registers crypto/compression services.

## State And Persistence Behavior
No runtime state exists in the Makefile. Its persistent effect is which code is compiled into the common base module and which symbols are exported in the default `CRYPTO_QAT` namespace.

## Dependencies And Integration Points
It integrates all device-specific QAT modules with one shared base module. `ccflags-y` sets the default symbol namespace to `CRYPTO_QAT`, so PF/VF device modules import common exports explicitly.

## Risks
Conditional compilation changes behavior substantially: no debugfs removes diagnostics, no PCI_IOV stubs SR-IOV functions, and missing files can cause unresolved symbols in device modules. The base module also owns algorithm registration, so build composition affects user-visible Crypto API support.

## Test Signals
Build matrix coverage with debugfs on/off, PCI_IOV on/off, and error injection on/off; successful `intel_qat` module load; `/dev/qat_adf_ctl` creation; crypto/compression registrations; and no unresolved namespace imports from device modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_devices.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_devices.h

## Purpose
This central header defines QAT device identity, hardware capability enums, BAR/MSI-X/PCI/device structures, callback tables, and the main `struct adf_accel_dev` and `struct adf_hw_device_data` used by all QAT PF/VF drivers and common framework code.

## Important APIs, Types, And Functions
Important types include `struct adf_bar`, `struct adf_accel_pci`, `struct adf_hw_device_class`, `struct adf_hw_csr_ops`, `struct adf_pfvf_ops`, `struct adf_dc_ops`, `struct adf_ras_ops`, `struct qat_migdev_ops`, `struct adf_hw_device_data`, `struct adf_accel_vf_info`, `struct adf_dc_data`, `struct adf_pm`, `struct adf_sysfs`, and `struct adf_accel_dev`. It also defines PCI IDs, device names, capability bits, fuse indexes, state enums, CSR read/write macros, and accessor macros such as `GET_HW_DATA()`, `GET_CSR_OPS()`, and `GET_DC_OPS()`.

## Control Flow
The header has only inline data classification such as `get_sku_info()` and CSR accessor macros. Runtime control is indirect: each hardware-data file fills callback fields in `adf_hw_device_data`, and common lifecycle code invokes those callbacks for probe, init, firmware load, transport, reset, PM, RAS, PF/VF messaging, compression context build, and migration.

## State And Persistence Behavior
The defined structs are volatile kernel state. `adf_accel_dev` persists for one bound PF/VF device and anchors transport, config, firmware loader, admin, telemetry, PM, PF/VF state, status bits, reference counts, debugfs, PCI info, timers, heartbeat, rate limiting, sysfs, and RAS counters.

## Dependencies And Integration Points
It includes Linux interrupt/module/list/io/pci/rate-limit/types headers plus QAT migration, anti-rollback, config, compression, telemetry, PF/VF, and hardware firmware definitions. Nearly every QAT source file depends on it.

## Risks
This is a high-blast-radius contract. Layout and callback changes affect all generations. CSR macros perform raw MMIO and require correct BAR/offset selection. Status bits and refcount/module ownership must stay synchronized with lifecycle paths.

## Test Signals
Build coverage across all QAT modules, probe/start/stop for PF and VF generations, SR-IOV, AER reset, firmware load, transport operations, debugfs/sysfs, compression/crypto algorithms, PM/RAS/anti-rollback, and migration paths validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_devices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_engine.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_engine.c

## Purpose
This file owns QAT accelerator-engine firmware loading, reset, start, stop, and release. It bridges Linux firmware blobs to the QAT UOF/MMP loader and hardware abstraction layer.

## Important APIs, Types, And Functions
Public functions are `adf_ae_init()`, `adf_ae_shutdown()`, `adf_ae_fw_load()`, `adf_ae_fw_release()`, `adf_ae_start()`, and `adf_ae_stop()`. The key helper `adf_ae_fw_load_images()` loads multi-object firmware by calling hardware-data callbacks `uof_get_num_objs()`, `uof_get_name()`, and `uof_get_ae_mask()`.

## Control Flow
`adf_ae_init()` allocates `adf_fw_loader_data`, initializes HAL, resets AEs, waits any chip-specific reset delay, and clears reset. `adf_ae_fw_load()` requests MMP and UOF firmware, loads MMP, then either loads per-object images for newer hardware or a single UOF image for older hardware. `adf_ae_start()` starts firmware through HAL and logs AE count. `adf_ae_stop()` stops all enabled AEs. Release/deinit frees mapped UOF objects, deinitializes HAL, and releases firmware.

## State And Persistence Behavior
State persists in `accel_dev->fw_loader` while the device is initialized/loaded. Firmware buffers are kernel firmware references and are released during `adf_ae_fw_release()`. No persistent storage is written.

## Dependencies And Integration Points
It depends on Linux firmware loading, PCI device context, QAT HAL, UOF loader, hardware-data firmware callbacks, and common lifecycle status bits set elsewhere in `adf_init.c`.

## Risks
Error paths call `adf_ae_fw_release()`, so partial loader state must be valid. Multi-object firmware selection depends on correct AE masks and object names. Missing firmware files or bad MMP/UOF contents prevent device start. Reset delay and HAL deinit ordering are hardware-sensitive.

## Test Signals
Signals include successful firmware requests, MMP/UOF load logs, per-object load for Gen4/Gen6, AE start/stop counts matching `ae_mask`, failure behavior for missing firmware, and clean reload after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.c

## Purpose
This file implements synchronous admin-message communication between the host driver and QAT firmware. It allocates DMA mailboxes, writes admin request/response addresses to CSRs, serializes messages, initializes firmware constants, reads capabilities/counters/PM/CNV/TL/RL/SVN data, and sends firmware init commands.

## Important APIs, Types, And Functions
Key public APIs include `adf_init_admin_comms()`, `adf_exit_admin_comms()`, `adf_send_admin_init()`, `adf_init_admin_pm()`, `adf_get_pm_info()`, `adf_get_fw_timestamp()`, `adf_get_ae_fw_counters()`, `adf_send_admin_tim_sync()`, `adf_send_admin_hb_timer()`, `adf_get_cnv_stats()`, `adf_send_admin_tl_start()`, `adf_send_admin_tl_stop()`, rate-limit commands, and anti-rollback SVN query/commit helpers. `struct adf_admin_comms` stores DMA buffers, constant-table buffer, mailbox MMIO address, and a mutex.

## Control Flow
`adf_init_admin_comms()` allocates coherent pages for request/response messages and a 1 KiB constants table, copies `const_tab`, gets generation-specific admin CSR offsets, and programs admin message address registers. `adf_put_admin_msg_sync()` locks, writes one 32-byte request for a target AE, signals mailbox ownership, polls for firmware clearing, then copies the response. `adf_send_admin()` iterates over an AE mask. `adf_send_admin_init()` sets constants, optionally initializes DC chaining, gathers DC/FW capabilities, then initializes AEs.

## State And Persistence Behavior
Admin state is per-device volatile memory in `accel_dev->admin`. Coherent DMA buffers persist from admin init to exit. Firmware capability fields and extended DC capabilities are cached in `hw_device`.

## Dependencies And Integration Points
It depends on hardware-data admin offsets, MMIO CSR macros, DMA APIs, QAT firmware admin message structures, config services, heartbeat, anti-rollback, PM/TL/RL users, and the common init sequence.

## Risks
The admin mutex serializes all admin commands; timeouts or firmware status failures return coarse errors. AE masks must avoid targeting absent/admin-only engines incorrectly. The constant table is large static data and must remain aligned. SVN retry behavior affects anti-rollback workflows.

## Test Signals
Successful device init, firmware capabilities populated, DC capabilities visible, AE counters in debugfs, heartbeat timer programming, PM info reads, CNV stats reads, TL/RL admin operations, anti-rollback SVN query/commit, and timeout handling on broken firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.h

## Purpose
This header declares the QAT admin-message API used by common lifecycle, PM, heartbeat, telemetry, rate limiting, compression diagnostics, and anti-rollback code.

## Important APIs, Types, And Functions
It forward-declares `struct adf_accel_dev` and includes firmware admin message definitions. Declared functions include admin comms init/exit, firmware init, AE counters, PM init/info, timer sync, heartbeat timer, RL init/add/update/delete, firmware timestamp, CNV stats, TL start/stop, and anti-rollback SVN query/commit.

## Control Flow
No executable control flow exists. The declarations define which subsystems can synchronously send admin commands after `accel_dev->admin` is initialized.

## State And Persistence Behavior
No state is declared here beyond the opaque device pointer. Runtime state is maintained by `adf_admin.c`.

## Dependencies And Integration Points
It integrates with `icp_qat_fw_init_admin.h` and every caller that needs firmware control or status data. It is part of the `CRYPTO_QAT` common internal interface.

## Risks
Changing prototypes has broad impact. Admin functions generally assume the device is initialized and firmware/admin AE masks are valid; callers must sequence them correctly.

## Test Signals
Build coverage across admin callers plus runtime exercise of init, PM, heartbeat, telemetry, rate limiting, CNV, and anti-rollback commands validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_aer.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_aer.c

## Purpose
This file implements QAT PCI Advanced Error Reporting and reset recovery support. It handles PCI error callbacks, secondary bus reset/FLR helpers, asynchronous and synchronous device restart scheduling, SR-IOV reenablement, PF-to-VF fatal/restarted notifications, and fatal-error workqueue handling.

## Important APIs, Types, And Functions
Public objects/APIs include `adf_err_handler`, `adf_reset_sbr()`, `adf_reset_flr()`, `adf_dev_restore()`, `adf_notify_fatal_error()`, `adf_init_aer()`, and `adf_exit_aer()`. Internal worker data types are `struct adf_reset_dev_data`, `struct adf_sriov_dev_data`, and `struct adf_fatal_error_data`.

## Control Flow
`adf_error_detected()` sets restarting state, disables arbitration, notifies services/VFs, clears bus mastering, and stops the device. `adf_slot_reset()` restores PCI state, restarts the device, reenables SR-IOV, notifies VFs/services, and clears restarting. `adf_dev_aer_schedule_reset()` queues reset work and optionally waits. The reset worker restarts the device, queues SR-IOV reenablement, sends PF2VF restarted notification, and completes. Fatal error work notifies services, disables arbitration when autoreset is enabled, notifies VFs, and schedules reset.

## State And Persistence Behavior
State is runtime-only in status bits, workqueue items, completions, and global reset/SR-IOV workqueues. It does not persist across module unload.

## Dependencies And Integration Points
It depends on Linux PCI error handlers, workqueues, completions, common device lifecycle, PF/VF messaging, SR-IOV helpers, arbitration callbacks, and service notification hooks.

## Risks
Reset races are central: the code guards with `ADF_STATUS_RESTARTING`, but in-flight users and VFs must quiesce correctly. Sync reset has a 10-second timeout. Fatal autoreset depends on `autoreset_on_error`. Workqueue allocation failure disables recovery.

## Test Signals
PCI AER injection, fatal error notification, FLR/SBR recovery, VF fatal/restarted messages, SR-IOV reenablement after PF reset, service restarting/restarted callbacks, and timeout handling are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_aer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.c

## Purpose
This file implements anti-rollback helpers for QAT firmware security version number (SVN) handling. It wraps admin SVN query/commit commands and checks hardware SVN status CSRs for pass/fail/retry/no-status outcomes.

## Important APIs, Types, And Functions
Public APIs are `adf_anti_rb_commit()`, `adf_anti_rb_query()`, and `adf_anti_rb_check()`. `adf_anti_rb_check()` uses `GET_ANTI_RB_DATA()` to access generation-specific anti-rollback offsets and enablement callbacks.

## Control Flow
Query and commit delegate to admin commands. `adf_anti_rb_check()` looks up the QAT device from a PCI device, skips if the generation does not enable anti-rollback, reads the configured SVN status CSR, extracts `ADF_SVN_STS_MASK`, and returns success, `-EIO`, `-EAGAIN`, `-ETIMEDOUT`, or `-EINVAL` depending on status and retry count.

## State And Persistence Behavior
State is volatile in `hw_device->anti_rb_data.svncheck_retry` and `sysfs_added` managed elsewhere. Retry count resets on pass or timeout.

## Dependencies And Integration Points
It depends on admin SVN commands, generation-specific anti-rollback metadata, PCI device manager lookup, CSR access to PMISC, and likely sysfs code outside this file.

## Risks
Retry behavior sleeps 250 ms per retry and permits 60 retries, so checks can span a significant time. Incorrect CSR offset or enablement predicate causes false pass/fail. Unknown status values return `-EINVAL`.

## Test Signals
SVN pass, fail, retry-to-pass, retry-timeout, and disabled-fuse scenarios; sysfs query/commit behavior; and Gen6 anti-rollback hardware with valid admin AE communication are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.h

## Purpose
This header defines the anti-rollback data contract for QAT SVN enforcement. It provides SVN status constants, retry delay, status mask, command enum, per-generation hardware-data structure, and query/commit/check declarations.

## Important APIs, Types, And Functions
Important definitions are `enum anti_rb`, `struct adf_anti_rb_hw_data`, `GET_ANTI_RB_DATA()`, and APIs `adf_anti_rb_commit()`, `adf_anti_rb_query()`, and `adf_anti_rb_check()`. The hardware-data struct supplies an enablement callback, SVN status CSR offset, retry count, and sysfs state flag.

## Control Flow
No executable flow exists in the header. Implementations and sysfs code use the enum to select SVN query type and the hardware-data struct to read status.

## State And Persistence Behavior
The only state described is per-device volatile anti-rollback metadata inside `struct adf_hw_device_data`.

## Dependencies And Integration Points
It integrates Gen6 hardware data, admin SVN messaging, sysfs anti-rollback files, and PCI probe/init paths that initialize the struct.

## Risks
The status constants are hardware ABI. If status masks or retry timing change, `adf_anti_rb_check()` behavior changes across all users. The `sysfs_added` flag must be maintained consistently by sysfs code.

## Test Signals
Build coverage, anti-rollback sysfs presence on supported devices, correct pass/fail/retry status handling, and admin SVN query/commit tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.c

## Purpose
This file saves and restores QAT transport bank/ring CSR state across bank reset or migration-related flows. It snapshots ring base/config/head/tail registers plus interrupt/status/coalescing/arbiter state and verifies selected status registers after restore.

## Important APIs, Types, And Functions
Public APIs are `adf_bank_state_save()` and `adf_bank_state_restore()`. Important helpers are `bank_state_save()`, `bank_state_restore()`, and `check_stat()`. The implementation uses `struct adf_hw_csr_ops` callbacks and `struct adf_bank_state` from the companion header.

## Control Flow
Save validates bank number, obtains ETR base and CSR ops, then reads bank-level status/interrupt/control registers and each ring's head/tail/config/base. Restore writes ring bases/configs, restores TX and RX head/tail with TX/RX gap handling, restores interrupt/coalescing/exception/arbiter registers, rewrites interrupt source selection with rise/fall masks, then verifies key status registers with `check_stat()`.

## State And Persistence Behavior
State is caller-owned in `struct adf_bank_state`; this file only fills/restores it. The saved state is volatile and valid only for matching device generation/bank geometry.

## Dependencies And Integration Points
It depends on `adf_accel_devices.h` CSR callback table, common BAR helpers, bank geometry in `hw_data`, and callers such as Gen4/Gen6 hardware-data callbacks.

## Risks
CSR ordering matters. Restoring stale ring base/head/tail values can corrupt transport queues. TX/RX gap logic must match hardware ring layout. Verification covers selected registers but not every side effect.

## Test Signals
Bank state save/restore across ring-pair reset, transport traffic before/after reset, DMA debug, interrupt coalescing preservation, and failure injection with altered expected status values are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.h

## Purpose
This header defines the in-memory snapshot structure for QAT transport bank state and declares save/restore helpers used by hardware-data callbacks.

## Important APIs, Types, And Functions
Important types are `struct adf_bank_state_ring` for per-ring head/tail/config/base values and `struct adf_bank_state` for bank-level status, interrupt, coalescing, exception, service arbiter, and per-ring arrays sized by `ADF_ETR_MAX_RINGS_PER_BANK`. Public APIs are `adf_bank_state_save()` and `adf_bank_state_restore()`.

## Control Flow
No executable flow exists. The layout determines what `adf_bank_state.c` saves/restores.

## State And Persistence Behavior
The structures hold volatile snapshots. They are not stable persistent data and should be used only while the relevant device/bank configuration remains unchanged.

## Dependencies And Integration Points
It includes Linux types and is referenced by `struct adf_hw_device_data` callback members in `adf_accel_devices.h`, plus Gen4/Gen6 hardware-data implementations.

## Risks
The array size assumes the maximum per-bank ring count. Adding CSR fields without updating save/restore can lose state across resets. Layout changes affect any migration or reset users.

## Test Signals
Compile coverage and runtime ring-pair reset or migration tests that preserve queue/interrupt state validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.c

## Purpose
This file implements the per-device QAT configuration database. It stores named sections and key/value pairs in kernel lists, exposes them through debugfs `dev_cfg`, and provides add/get/delete helpers for PCI probe defaults and user ioctl configuration.

## Important APIs, Types, And Functions
Public APIs are `adf_cfg_dev_add()`, `adf_cfg_dev_remove()`, `adf_cfg_dev_dbgfs_add()`, `adf_cfg_dev_dbgfs_rm()`, `adf_cfg_del_all()`, `adf_cfg_del_all_except()`, `adf_cfg_section_add()`, `adf_cfg_add_key_value_param()`, and `adf_cfg_get_param_value()`. Debugfs iteration uses `qat_dev_cfg_*()` seq operations.

## Control Flow
Device add allocates `adf_cfg_device_data`, initializes section list and lock. Section add creates or reuses a section. Key add formats decimal/string/hex values, then under the config write lock replaces an existing key if value differs or discards duplicate values. Get uses the read lock. Delete paths walk lists backwards and free section/key nodes. Debugfs seq operations lock a global read mutex while iterating the section list.

## State And Persistence Behavior
Config state is volatile in `accel_dev->cfg` and persists for the device lifetime or until reconfiguration/deletion. It stores strings, not parsed typed values. It does not persist to disk.

## Dependencies And Integration Points
It depends on Linux list/seq/debugfs/rwsem, QAT config strings/common definitions, and common driver status bits. It is used by PCI probes, control ioctl, Gen4/Gen6 service parsing, heartbeat config, and debugfs.

## Risks
Config stores fixed 64-byte strings, so truncation/length constraints matter. `ADF_HEX` treats `val` as an integer encoded through a pointer-shaped argument. Updates delete then append, changing list order. The debugfs reader uses a global mutex separate from per-device rwsem.

## Test Signals
Add/get/update/delete unit coverage, ioctl configuration, debugfs `dev_cfg` output, duplicate key behavior, invalid type rejection, config clearing on stop/reconfigure, and service parsing from stored values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.h

## Purpose
This header defines the kernel-side QAT configuration database structures and declares config-management functions.

## Important APIs, Types, And Functions
Important structures are `struct adf_cfg_key_val`, `struct adf_cfg_section`, and `struct adf_cfg_device_data`. Declared functions cover device config allocation/removal, debugfs add/remove, section add, full/partial deletion, key/value add, and value lookup.

## Control Flow
No executable flow exists. The structures are manipulated by `adf_cfg.c` and consumed by control/ioctl and generation config code.

## State And Persistence Behavior
The header defines volatile per-device config state: linked sections, linked key values, optional debugfs dentry, and a read/write semaphore.

## Dependencies And Integration Points
It includes Linux list/rwsem/debugfs and QAT config common/string/device headers. It is included by most configuration-aware QAT code.

## Risks
Fixed-size key/value/section arrays impose truncation boundaries. Exposing `struct adf_cfg_device_data` lets callers assume list layout, so changes need broad review.

## Test Signals
Build coverage plus config ioctl, generated defaults, debugfs `dev_cfg`, and config deletion/rebuild tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_common.h

## Purpose
This header defines common configuration sizes, device-selection constants, service encoding shifts, config value types, QAT device type IDs, user-visible device status shape, and ioctl command numbers for `/dev/qat_adf_ctl`.

## Important APIs, Types, And Functions
Important definitions include `ADF_CFG_MAX_*`, `ADF_CFG_ALL_DEVICES`, `ADF_MAX_DEVICES`, `enum adf_cfg_service_type`, `enum adf_cfg_val_type`, `enum adf_device_type`, `struct adf_dev_status_info`, and ioctls `IOCTL_CONFIG_SYS_RESOURCE_PARAMETERS`, `IOCTL_STOP_ACCEL_DEV`, `IOCTL_START_ACCEL_DEV`, `IOCTL_STATUS_ACCEL_DEV`, and `IOCTL_GET_NUM_DEVICES`.

## Control Flow
There is no executable flow. The constants drive config parsing, ring-to-service map encoding, device-manager limits, and control-device ioctl dispatch.

## State And Persistence Behavior
No state exists in the header. `struct adf_dev_status_info` is a copied user/kernel data shape for transient status queries.

## Dependencies And Integration Points
It includes Linux types and ioctl helpers. It is shared by kernel config code and user-facing control structures, so it is part of a UAPI-adjacent contract despite living under driver sources.

## Risks
Changing struct layout or ioctl numbers can break user tools. `ADF_MAX_DEVICES` sizes internal bitmaps and device IDs. Service shift constants must match ring-to-service encoding used by hardware-data files.

## Test Signals
Compatibility tests for control ioctls, 32/64-bit compat ioctl, status output, device count, and service map decoding validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.c

## Purpose
This file parses and normalizes QAT `ServicesEnabled` configuration values, converts service strings to bitmasks and back, reports composed service modes, and checks whether a base service is active in the ring-to-service map.

## Important APIs, Types, And Functions
Public APIs are `adf_parse_service_string()`, `adf_get_service_mask()`, `adf_get_service_enabled()`, `adf_srv_to_cfg_svc_type()`, and `adf_is_service_enabled()`. Internal helpers are `adf_service_string_to_mask()` and `adf_service_mask_to_string()`. The string table maps `SVC_ASYM`, `SVC_SYM`, `SVC_DC`, `SVC_DCC`, and `SVC_DECOMP` to config strings.

## Control Flow
Parsing copies the input into a fixed buffer, splits on `;`, matches known service strings, rejects duplicates, rejects too many services, and asks hardware data's `services_supported()` callback when present. Mask-to-string reserializes in enum order. `adf_get_service_enabled()` maps parsed masks to composed service identifiers such as `SVC_SYM_ASYM`, `SVC_SYM_DC`, or `SVC_ASYM_DC`; otherwise it returns the single service.

## State And Persistence Behavior
No long-lived state is stored here. It reads volatile config from `accel_dev->cfg` and returns transient masks or normalized strings.

## Dependencies And Integration Points
It depends on config storage, service string constants, hardware-data service support callbacks, and ring-to-service maps in `hw_data`. Gen4/Gen6 capability and firmware selection depend on its outputs.

## Risks
Service enum order affects normalized strings and composed-mode selection. `SVC_DCC` is extended and excluded from some multi-service mixes by hardware callbacks. Empty masks are rejected only in the public parse path.

## Test Signals
Valid/invalid service strings, duplicate tokens, too many tokens, hardware unsupported masks, Gen6 WCY rejection, ring-to-service active checks, and capability/firmware selection for each service mix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.h

## Purpose
This header defines QAT service enums and parsing/query APIs for `ServicesEnabled` configuration.

## Important APIs, Types, And Functions
Important enums are `enum adf_base_services` (`SVC_ASYM`, `SVC_SYM`, `SVC_DC`, `SVC_DECOMP`), `enum adf_extended_services` (`SVC_DCC`), and `enum adf_composed_services` (`SVC_SYM_ASYM`, `SVC_SYM_DC`, `SVC_ASYM_DC`). It also defines `ADF_ONE_SERVICE`, `ADF_TWO_SERVICES`, `ADF_THREE_SERVICES`, `MAX_NUM_CONCURR_SVC`, and declares service parse/query helpers.

## Control Flow
No executable flow exists. The enum values are used as bit positions by `adf_cfg_services.c` and hardware-data callbacks.

## State And Persistence Behavior
No state exists. The header provides compile-time service identity and limits.

## Dependencies And Integration Points
It includes service string definitions and is consumed by Gen4/Gen6 hardware-data code, config parsing, capability calculation, and ring-to-service checks.

## Risks
Enum ordering is ABI inside the driver because masks use enum values as bit indexes. Changing `MAX_NUM_CONCURR_SVC` affects Gen6 ring-pair assignment assumptions.

## Test Signals
Build coverage plus service parsing, Gen4/Gen6 firmware selection, capability masks, and ring service matching validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_strings.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_strings.h

## Purpose
This header centralizes string keys and section names used by QAT configuration storage, generated defaults, user configuration, and debugfs display.

## Important APIs, Types, And Functions
Important constants include section names `ADF_GENERAL_SEC`, `ADF_KERNEL_SEC`, `ADF_ACCEL_SEC`; service strings `ADF_CFG_DC`, `ADF_CFG_DECOMP`, `ADF_CFG_CY`, `ADF_CFG_SYM`, `ADF_CFG_ASYM`, `ADF_CFG_DCC`; key names such as `ADF_SERVICES_ENABLED`, ring names, coalescing keys, core-affinity formats, heartbeat timer, and SR-IOV enabled flag. There are no functions.

## Control Flow
No runtime flow exists. Other code uses these constants to write and read exact key strings.

## State And Persistence Behavior
No mutable state exists. The strings become the stable names visible through debugfs and user config paths.

## Dependencies And Integration Points
It is included by config storage, service parsing, user config structs, Gen2/Gen4/Gen6 config generation, and control-device code.

## Risks
Renaming strings breaks user tools, default config lookup, and service parsing. Format strings for bank-specific settings must remain aligned with config generation code.

## Test Signals
Config ioctl round trips, debugfs `dev_cfg` output, service parsing, generated ring configuration, heartbeat config, and SR-IOV config are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_strings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_user.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_user.h

## Purpose
This header defines packed user-to-kernel configuration structures accepted by the QAT control ioctl for setting device resource parameters.

## Important APIs, Types, And Functions
Important types are `struct adf_user_cfg_key_val`, `struct adf_user_cfg_section`, and `struct adf_user_cfg_ctl_data`. The key/value and section structs contain user pointers expressed through unions with `__u64` padding to support compat layouts. There are no functions.

## Control Flow
No executable flow exists. `adf_ctl_drv.c` walks linked user-space section and key/value lists using these layouts and copies each node with `copy_from_user()`.

## State And Persistence Behavior
These structures describe transient ioctl input. Once copied, values are converted into kernel `adf_cfg` sections and keys. No persistent storage is created by the header.

## Dependencies And Integration Points
It includes config common and string headers and is used by `/dev/qat_adf_ctl` ioctl handling. It is part of the user-facing ABI.

## Risks
Packed layout and pointer padding are ABI-sensitive. The kernel limits traversal to 512 sections and 256 keys per section; malformed user pointers cause ioctl failure and config rollback.

## Test Signals
32-bit compat ioctl tests, config of nested sections/key values, invalid user pointer handling, maximum section/key bounds, and status after rollback validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.c

## Purpose
This file measures QAT accelerator-engine clock frequency by synchronizing with firmware timestamp counters over the admin interface. Older Gen2 devices use this to calibrate heartbeat timestamp behavior.

## Important APIs, Types, And Functions
The public API is `adf_dev_measure_clock()`. Internal helpers include `timespec_to_us()`, `timespec_to_ms()`, and `measure_clock()`. Constants define retry count, delay, ME clock divider, and acceptable time delta threshold.

## Control Flow
`measure_clock()` reads system monotonic time, sends an admin timestamp sync, waits 10 ms, reads firmware timestamp, reads system time again, and computes frequency from firmware counter delta and elapsed time if the measurement window is stable. `adf_dev_measure_clock()` retries up to 10 times and validates that the resulting frequency lies within caller-provided min/max bounds.

## State And Persistence Behavior
No state is stored here. Callers store the measured frequency in `hw_device->clock_frequency`.

## Dependencies And Integration Points
It depends on admin timestamp commands, Linux timekeeping, delays, and device logging. C3xxx/C62x hardware data calls it during setup.

## Risks
System scheduling jitter can make measurements fail; the threshold controls this. Admin communication must already be functional. Wrong min/max bounds reject valid hardware or accept bad measurements.

## Test Signals
Clock measurement on Gen2 devices, retry behavior under load, failure with broken admin firmware, and heartbeat timing stability validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.h

## Purpose
This header declares the common QAT clock-measurement helper used by device-specific hardware-data files.

## Important APIs, Types, And Functions
The only public API is `adf_dev_measure_clock(struct adf_accel_dev *accel_dev, u32 *frequency, u32 min, u32 max)`.

## Control Flow
No executable flow exists. The implementation performs admin timestamp synchronization and range validation.

## State And Persistence Behavior
The header defines no state. Callers pass an output pointer and store results elsewhere.

## Dependencies And Integration Points
It depends on `struct adf_accel_dev` from the common device model. It is included by Gen2 hardware-data files that need measured AE frequency.

## Risks
Callers must invoke it only after admin communication is available and must provide correct min/max frequencies.

## Test Signals
Build coverage and successful C3xxx/C62x clock measurement validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.c

## Purpose
This file implements debugfs reporting for compression CNV errors. It queries firmware for per-AE CNV error counts and latest error codes, decodes error fields, and exposes either a populated `cnv_errors` file or an explanatory no-compression message.

## Important APIs, Types, And Functions
Public functions are `adf_cnv_dbgfs_add()` and `adf_cnv_dbgfs_rm()`. Internal types include `struct ae_cnv_errors` and `struct cnv_err_stats`. Helpers include `get_err_info()`, seq operations `qat_cnv_errors_seq_*()`, `cnv_err_stats_alloc()`, file open/release handlers, and `no_comp_file_read()`.

## Control Flow
When added, if compression service is available, it creates a debugfs file backed by seq operations; otherwise it creates a read-only file saying compression is unavailable. Opening the file allocates stats, iterates service AEs, sends `adf_get_cnv_stats()` admin commands, stores error data, and then seq-show formats AE, count, latest error type, and decoded info. Release frees allocated stats.

## State And Persistence Behavior
Persistent per-device state is only `accel_dev->cnv_dbgfile`. Per-open stats are allocated and freed for each file read. Firmware counters live in firmware and are queried on demand.

## Dependencies And Integration Points
It depends on debugfs, seq_file, admin CNV stats, service/capability checks, and `adf_dbgfs_add()` for non-persistent debugfs entry creation.

## Risks
Admin query failures can make debugfs reads fail. Error decoding is tied to firmware bit layout and sign extension fields. Large or changing AE masks must be reflected in allocation and iteration.

## Test Signals
Reading `cnv_errors` on compression-enabled devices, no-compression text on crypto-only devices, injected CNV errors, admin unsupported status, open/release leak checks, and debugfs remove on device down validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.h

## Purpose
This header declares CNV compression-error debugfs add/remove hooks.

## Important APIs, Types, And Functions
It forward-declares `struct adf_accel_dev` and declares `adf_cnv_dbgfs_add()` and `adf_cnv_dbgfs_rm()`.

## Control Flow
No executable flow exists. The hooks are called by `adf_dbgfs_add()` and `adf_dbgfs_rm()` for PF devices when debugfs support is compiled.

## State And Persistence Behavior
The header defines no state. Runtime state is `accel_dev->cnv_dbgfile` in the implementation.

## Dependencies And Integration Points
It integrates CNV diagnostics with the broader QAT debugfs lifecycle.

## Risks
Prototype changes affect debugfs orchestration. Calls should only happen when debugfs is enabled and the device is in a suitable state for admin queries.

## Test Signals
Build coverage with `CONFIG_DEBUG_FS`, debugfs file creation/removal, and CNV stats reads validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cnv_dbgfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_common_drv.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_common_drv.h

## Purpose
This header is the shared internal driver interface for QAT common code and device-specific modules. It defines version/status bits, event/reset enums, service-handler structure, lifecycle prototypes, device-manager APIs, firmware-engine APIs, AER/reset APIs, transport/crypto/compression interfaces, ISR hooks, SR-IOV stubs or declarations, workqueue helpers, HAL/UOF loader APIs, and BAR accessor inlines.

## Important APIs, Types, And Functions
Key definitions include `ADF_DRV_VERSION`, status bits such as `ADF_STATUS_STARTED`, `enum adf_dev_reset_mode`, `enum adf_event`, and `struct service_hndl`. Important APIs include `adf_dev_up/down/restart()`, `adf_service_register/unregister()`, device-manager functions, reset/AER functions, `adf_ae_*()` firmware helpers, `adf_init_etr_data()`, `qat_crypto_*()`, `qat_compression_*()`, ISR allocation, workqueue helpers, SR-IOV/PFVF helpers, HAL/UOF loader functions, and inline `adf_get_pmisc_base()`, `adf_get_etr_base()`, and `adf_get_aram_base()`.

## Control Flow
The header itself has only inline BAR accessors and stubbed SR-IOV functions when `CONFIG_PCI_IOV` is disabled. Runtime control is implemented across common source files and invoked by PF/VF PCI modules.

## State And Persistence Behavior
No state is stored here, but the status bit assignments define `accel_dev->status` semantics and service handler bitmaps track per-device init/start states in implementations.

## Dependencies And Integration Points
It includes list/PCI headers, `adf_accel_devices.h`, firmware loader handle, and HAL definitions. It is included broadly by every QAT module.

## Risks
This is a high-impact internal ABI. Status-bit ordering, function prototypes, and SR-IOV stubs affect multiple generations. BAR accessor inlines rely on hardware-data callback correctness.

## Test Signals
Full QAT build matrix, PF/VF probe/start/stop/restart, crypto/compression algorithms, transport operations, SR-IOV on/off builds, AER reset, and firmware load validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_common_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_ctl_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_ctl_drv.c

## Purpose
This file implements the `intel_qat` base module entry/exit and the `/dev/qat_adf_ctl` character device used to configure, start, stop, and query QAT devices. It also initializes global workqueues/AER and registers QAT crypto/compression services.

## Important APIs, Types, And Functions
Important functions include `adf_chr_drv_create()`, `adf_chr_drv_destroy()`, `adf_ctl_ioctl()`, ioctl handlers for config/stop/start/status/device-count, `adf_copy_key_value_data()`, `adf_ctl_stop_devices()`, `adf_register_ctl_device_driver()`, and `adf_unregister_ctl_device_driver()`. `struct adf_ctl_drv_info` holds char-device major/cdev state.

## Control Flow
Module init creates the char device/class, initializes misc/AER/PF/VF workqueues, registers crypto and compression services, and unwinds in reverse on failure. Ioctl dispatch is serialized by `adf_ctl_lock`. Config ioctl copies user-linked sections/keys into kernel config if the device is stopped. Stop verifies IDs and busy/reset state, stops VFs first, then PFs/all matching devices. Start calls `adf_dev_up(accel_dev, false)`. Status copies hardware counts, state, device type, instance, and BDF to user space.

## State And Persistence Behavior
Global runtime state includes the char-device major/cdev and class. Device config written by ioctl is volatile in `accel_dev->cfg`. Crypto/compression registration persists until module unload.

## Dependencies And Integration Points
It depends on Linux char device/uaccess/mutex, QAT config/user structs, device manager, common lifecycle, workqueues, AER, PF/VF code, and algorithm registration.

## Risks
User-pointer traversal must be bounded and rollback on error. Stop/start races are guarded by `adf_ctl_lock` and device busy checks, but external users can still hold references. Module init unwind must mirror registration order. Device status ABI must remain stable.

## Test Signals
`/dev/qat_adf_ctl` creation, compat ioctl tests, config copy/rollback, start/stop all devices with VFs, busy-device rejection, status/device-count output, algorithm registration/unregistration, and module load/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_ctl_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.c

## Purpose
This file coordinates QAT debugfs directory and file creation. It separates persistent entries that survive device up/down transitions from non-persistent runtime diagnostics.

## Important APIs, Types, And Functions
Public functions are `adf_dbgfs_init()`, `adf_dbgfs_exit()`, `adf_dbgfs_add()`, and `adf_dbgfs_rm()`. Persistent init creates the device directory and config dump; non-persistent add/remove manages firmware counters, heartbeat, PM, CNV, and telemetry/debug files for PFs.

## Control Flow
`adf_dbgfs_init()` builds a directory name from `qat_`, device class name, and PCI name, creates the directory, and adds `dev_cfg`. `adf_dbgfs_exit()` removes config and directory. `adf_dbgfs_add()` skips VFs and adds runtime PF diagnostics. `adf_dbgfs_rm()` removes runtime diagnostics in reverse-ish dependency order.

## State And Persistence Behavior
Persistent state is `accel_dev->debugfs_dir` and config debugfs dentry. Runtime diagnostic file pointers are stored in feature-specific fields such as `fw_cntr_dbgfile` and `cnv_dbgfile`.

## Dependencies And Integration Points
It depends on Linux debugfs, config debugfs, firmware counters, heartbeat debugfs, PM debugfs, CNV debugfs, and telemetry debugfs.

## Risks
Debugfs calls can return error dentries but are generally non-fatal. Runtime diagnostics are PF-only; accidentally enabling on VFs can call unsupported admin paths. Removal order must tolerate partially created files.

## Test Signals
Debugfs tree creation/removal, `dev_cfg`, firmware counters, heartbeat, PM, CNV, TL files on PFs, absence on VFs, device up/down cycles, and debugfs-disabled build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.h

## Purpose
This header declares QAT debugfs lifecycle hooks and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled.

## Important APIs, Types, And Functions
APIs are `adf_dbgfs_init()`, `adf_dbgfs_add()`, `adf_dbgfs_rm()`, and `adf_dbgfs_exit()`. In non-debugfs builds, static inline stubs do nothing.

## Control Flow
The header controls build-time flow: callers can invoke debugfs hooks unconditionally while compiled code either performs debugfs operations or no-ops.

## State And Persistence Behavior
No state is stored here. Runtime state is in `adf_dbgfs.c` and feature-specific debugfs modules.

## Dependencies And Integration Points
It integrates PCI drivers and common lifecycle code with optional debugfs support.

## Risks
The stubs mean tests must cover both debugfs-enabled and disabled builds. Function signatures must remain identical across branches.

## Test Signals
Build with and without `CONFIG_DEBUG_FS`, probe devices, and confirm debugfs files exist only in enabled builds while probe still succeeds in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.c

## Purpose
This file builds QAT compression/decompression request context templates shared by compression algorithms. It fills common firmware request headers, compression flags, CRC initialization, slice chaining IDs, and delegates generation-specific compression/decompression config blocks to `adf_dc_ops`.

## Important APIs, Types, And Functions
The public API is `qat_comp_build_ctx(struct adf_accel_dev *accel_dev, void *ctx, enum adf_dc_algo algo)`. It operates on two adjacent `struct icp_qat_fw_comp_req` templates: compression first, decompression second.

## Control Flow
The function clears the first template, initializes common request header flags for stateless compression with SGL pointers, calls `GET_DC_OPS(accel_dev)->build_comp_block()`, sets legacy Adler/CRC and request parameter flags including SOP/EOP/BFINAL/CNV recovery, sets current/next slice IDs, copies the compression template to the next slot, advances the template pointer, and calls `build_decomp_block()`.

## State And Persistence Behavior
The caller owns the context buffer. The initialized templates persist as transform or instance state in compression code outside this file. No global state is modified.

## Dependencies And Integration Points
It depends on QAT firmware compression request structures and generation-specific `adf_dc_ops` implementations from Gen2/Gen4/Gen6 hardware data. It is used by QAT compression algorithm setup.

## Risks
The buffer must be large enough for two templates. Unsupported algorithms return errors through generation ops. Header flag mismatches can make firmware reject requests or produce wrong compression output.

## Test Signals
Compression/decompression selftests for DEFLATE, ZSTD where supported, invalid algorithm rejection, CNV recovery behavior, and generation-specific config block verification validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.h

## Purpose
This header defines QAT data-compression algorithm identifiers and declares the common compression context builder.

## Important APIs, Types, And Functions
`enum adf_dc_algo` names `QAT_DEFLATE`, `QAT_LZ4`, `QAT_LZ4S`, and `QAT_ZSTD`. The public function is `qat_comp_build_ctx(struct adf_accel_dev *accel_dev, void *ctx, enum adf_dc_algo algo)`.

## Control Flow
No executable flow exists. The enum selects algorithm-specific config in generation-specific DC ops.

## State And Persistence Behavior
No state is defined. Callers allocate and retain context buffers.

## Dependencies And Integration Points
It forward-declares `struct adf_accel_dev` and is used by hardware-data files and compression algorithm code.

## Risks
Enum additions require updates in every generation's `build_comp_block()` and `build_decomp_block()` implementation. Unsupported algorithms should return errors consistently.

## Test Signals
Build coverage and compression selftests for each advertised algorithm validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dev_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dev_mgr.c

## Purpose
This file maintains the global QAT device registry and user-visible device IDs. It tracks PFs, guest VFs, host VFs, detached VF ID mappings, device reference counts, class indexes, reset/started status queries, and total device count.

## Important APIs, Types, And Functions
Public APIs include `adf_devmgr_add_dev()`, `adf_devmgr_rm_dev()`, `adf_devmgr_pci_to_accel_dev()`, `adf_devmgr_get_dev_by_id()`, `adf_devmgr_verify_id()`, `adf_devmgr_get_num_dev()`, `adf_devmgr_update_class_index()`, `adf_clean_vf_map()`, `adf_dev_in_use()`, `adf_dev_get()`, `adf_dev_put()`, `adf_devmgr_in_reset()`, and `adf_dev_started()`. Internal state includes `accel_table`, `vfs_table`, `table_lock`, `num_devices`, and `id_map`.

## Control Flow
Add-dev assigns IDs differently for PFs/guest VFs versus host VFs with a PF. PF-like devices get a free ID and a synthetic VF map entry. Host VFs either reuse detached mappings or allocate new mappings based on BDF-derived VF number. Remove-dev frees PF-like IDs but keeps detached host VF mappings for stable numbering. Lookup by user ID first maps fake VF IDs to real IDs. Refcount helpers also pin/unpin the owning module on first/last use.

## State And Persistence Behavior
Registry state is global and volatile for the loaded base module. Detached VF mappings can persist after VF removal until `adf_clean_vf_map()` is called, preserving user-visible numbering across VF detach/reattach.

## Dependencies And Integration Points
It depends on PCI BDF data, common config constants, module refcounting, and all PCI PF/VF drivers. Control ioctl status/start/stop paths use it heavily.

## Risks
ID-map accounting must stay balanced with list operations. Host VF fake-ID shifting is subtle and can affect user tools. Returning device pointers after unlocking assumes lifecycle synchronization by callers. `adf_dev_put()` assumes balanced gets.

## Test Signals
Probe/remove PFs and VFs, detach/reattach host VFs, query device count/status, start/stop by ID/all devices, refcount/module pin behavior under active crypto users, and cleanup on module unload validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dev_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_config.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_config.h

## Purpose
This header defines the compact firmware-object mapping format used by Gen4 and Gen6 hardware-data files to load the right UOF image onto the right AE mask.

## Important APIs, Types, And Functions
`enum adf_fw_objs` names firmware object roles: symmetric, asymmetric, compression, admin, combined crypto, and wireless crypto. `struct adf_fw_config` pairs an `ae_mask` with one enum object. There are no functions.

## Control Flow
No executable flow exists. Hardware-data files build static arrays of `struct adf_fw_config`, then common firmware loading iterates through hardware-data callbacks to map object IDs to firmware names and AE masks.

## State And Persistence Behavior
No mutable state exists. Static firmware config arrays persist as read-only module data.

## Dependencies And Integration Points
It integrates `adf_accel_engine.c` firmware loading with generation-specific service layouts in 4xxx and 6xxx hardware-data files.

## Risks
Enum ordering must match firmware-name arrays in hardware-data files. Missing or incorrect object roles can load the wrong firmware image or leave service/admin AEs unloaded.

## Test Signals
Firmware load for each service mix, invalid object handling, AE mask coverage, and algorithm exposure matching loaded firmware validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_config.h -->
