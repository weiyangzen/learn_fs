# Research Group subset-b-001236

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.c

Purpose: implements the QAT data-compression service handler. It registers a `service_hndl` named `qat_compression`, creates per-device compression instances from ADF config, exposes NUMA-aware instance selection, and allocates shared compression overflow/skid DMA storage.

Important APIs and functions: `qat_compression_register()` and `qat_compression_unregister()` bind the service into the ADF service bus. `qat_compression_event_handler()` reacts to `ADF_EVENT_INIT` and `ADF_EVENT_SHUTDOWN`. `qat_compression_create_instances()` reads `ADF_NUM_DC` and per-instance `ADF_DC%d...` keys, creates DC TX/RX transport rings, initializes `qat_instance_backlog`, and attaches `accel_dev->dc_data`. `qat_compression_get_instance_node(node, alg)` chooses a started accelerator and least-used `qat_compression_instance`, filtering ZSTD/LZ4S requests through `accel_capabilities_ext_mask`. `qat_compression_put_instance()` releases both instance and device references.

Control flow: service init allocates `adf_dc_data` first, mapping a `QAT_COMP_MAX_SKID` overflow buffer with `dma_map_single()`, then creates rings. Runtime clients call `qat_compression_get_instance_node()`, submit through `dc_tx`, and receive completions through the RX ring callback `qat_comp_alg_callback`. Shutdown frees DMA data and removes all rings/instances.

State and persistence: state is in `accel_dev->compression_list`, per-instance atomic `refctr`, backlog list/lock, and `accel_dev->dc_data`. The overflow buffer persists for the accelerator service lifetime only. Device references are mirrored with instance references via `adf_dev_get()`/`adf_dev_put()`.

Dependencies and integration points: depends on ADF config, device manager, transport rings, QAT firmware request/response sizes, and compression algorithm callbacks declared outside this file. Integrates with capability masks and NUMA placement.

Risks: several error returns inside `qat_compression_create_instances()` occur after an instance has been linked; unlike the initial allocation failure path, not all of them jump to common cleanup. This can leave partially created rings/list entries for the caller to handle poorly. The ZSTD/LZ4S filter accepts either extended capability bit in a combined mask rather than requiring an algorithm-specific bit. Test focus should cover config parse failures after partial ring creation, DMA mapping failure cleanup, reference balancing, NUMA fallback, and unsupported extended-compression algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.h

Purpose: declares the per-instance state used by the QAT compression service and provides a capability helper for devices that expose compression.

Important APIs and types: `QAT_COMP_MAX_SKID` fixes the shared overflow/skid buffer size at 4096 bytes. `struct qat_compression_instance` contains DC TX/RX rings, owning `adf_accel_dev`, list linkage, state/id/refcount fields, per-instance backlog, and shared `adf_dc_data`. `adf_hw_dev_has_compression()` tests `accel_capabilities_mask` for `ADF_ACCEL_CAPABILITIES_COMPRESSION`.

Control flow and integration: this header is consumed by `qat_compression.c` and compression algorithm code. Algorithms obtain a `qat_compression_instance`, use its `dc_tx`/`dc_rx` rings and backlog, then return it through the exported put path. The capability helper is intended for higher-level service/config checks before enabling compression algorithms.

State and persistence: the header does not allocate state, but it defines the fields that survive across compression requests for an accelerator service lifetime. The `dc_data` pointer is shared from `accel_dev->dc_data`; the per-instance backlog is protected by its own spinlock.

Dependencies: includes Linux list/types, `adf_accel_devices.h`, and `qat_algs_send.h` for backlog definitions. It assumes ADF hardware capability masks use set bits for unavailable capabilities after inverting the mask.

Risks and test signals: callers must not assume the helper checks extended ZSTD/LZ4S capabilities; that filtering lives in `qat_compression_get_instance_node()`. Tests should validate capability-mask polarity and ensure users of `qat_compression_instance` respect refcount and backlog locking rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_compression.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.c

Purpose: implements QAT crypto service instance management for symmetric and asymmetric crypto rings. It registers the `qat_crypto` ADF service, builds ring pairs from config, and provides a NUMA/load-aware instance picker for crypto algorithms.

Important APIs and functions: `qat_crypto_register()`/`qat_crypto_unregister()` register the service. `qat_crypto_event_handler()` maps init/shutdown events to `qat_crypto_create_instances()` and `qat_crypto_free_instances()`. `qat_crypto_get_instance_node()` scans ADF devices for a started accelerator on the requested NUMA node, falls back to any started device, then chooses the least-used instance. `qat_crypto_vf_dev_config()` validates VF ring/service mapping before invoking hardware `dev_config()`.

Control flow: service initialization reads `ADF_NUM_CY`, then each instance reads sym/asym bank numbers and ring sizes. It halves configured message counts for TX/RX pairing, creates symmetric TX, asymmetric/PKE TX, symmetric RX, and asymmetric/PKE RX rings, and attaches callbacks `qat_alg_callback` and `qat_alg_asym_callback`. Shutdown drains references by repeatedly putting held instances, removes all rings, deletes the list node, and frees instance memory.

State and persistence: per-device state is `accel_dev->crypto_list`; per-instance state includes ring pointers, `refctr`, ID, owning device, and backlog. Device references are acquired in `qat_crypto_get_instance_node()` and released by `qat_crypto_put_instance()`.

Dependencies and integration points: depends on ADF config strings, transport ring creation/removal, gen2 default ring/service mapping for VFs, and QAT firmware request/response sizes. It integrates with all QAT symmetric/asymmetric algorithm implementations through `struct qat_crypto_instance`.

Risks: create-instance error handling consistently jumps to cleanup, but the free path decrements references by reading the current refcount while changing it in the loop; concurrent users must be quiesced before shutdown. `qat_crypto_init()` maps all create errors to `-EFAULT`, losing diagnostic precision. Tests should cover partial ring creation failures, VF config mismatch, NUMA fallback, async callback completion, and refcount balance under request churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.h

Purpose: defines QAT crypto instance and per-request state shared by QAT symmetric, AEAD, and asymmetric send paths.

Important APIs and types: `struct qat_crypto_instance` stores symmetric TX/RX rings, PKE TX/RX rings, owner accelerator, list linkage, ID, refcount, and backlog. `struct qat_crypto_request` embeds the firmware LA bulk request, points to AEAD or skcipher context/request, owns mapped buffer metadata, callback pointer, IV storage, encryption flag, and low-level algorithm request state. `adf_hw_dev_has_crypto()` checks symmetric, asymmetric, and authentication capability bits.

Control flow and integration: algorithm implementations allocate/fill `qat_crypto_request`, submit it on a selected `qat_crypto_instance`, and receive completion through the callback stored in the request. The IV union supports both structured 128-bit big-endian access and byte-array AES block access. The instance struct is populated by `qat_crypto.c`.

State and persistence: instance state lasts for the accelerator service lifetime; request state is per crypto operation and should be zeroed or freed by callers after callback completion. The backlog is shared across send paths and requires its lock.

Dependencies: depends on Linux crypto AES constants, QAT firmware LA structures, buffer-list support, and QAT algorithm send helpers. The capability helper assumes inverted `accel_capabilities_mask` semantics.

Risks and test signals: request unions require callers to keep the context/request type consistent with the algorithm path. Capability checks require all three crypto/auth bits, so devices with only symmetric crypto are rejected by this helper. Tests should cover IV preservation, request callback dispatch, buffer mapping cleanup, and capability mask combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_hal.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_hal.c

Purpose: provides the low-level hardware abstraction layer used by the QAT firmware loader. It programs accelerator-engine CSRs, resets and starts AEs, writes microstore/uStore words with ECC, initializes local/register state, and abstracts chip-generation differences.

Important APIs and functions: exported/internal entry points include `qat_hal_init()`, `qat_hal_deinit()`, `qat_hal_reset()`, `qat_hal_clr_reset()`, `qat_hal_start()`, `qat_hal_stop()`, `qat_hal_set_pc()`, `qat_hal_wr_uwords()`, `qat_hal_wr_umem()`, `qat_hal_batch_wr_lm()`, `qat_hal_init_gpr()`, `qat_hal_init_wr_xfer()`, `qat_hal_init_rd_xfer()`, and `qat_hal_init_nn()`. Mode setters configure AE context count, next-neighbor mode, local memory mode, and t-index mode.

Control flow: `qat_hal_init()` allocates the loader handle, HAL state, and chip info, then `qat_hal_chip_init()` fills chip-specific CSR offsets, reset masks, authentication flags, SRAM support, uStore size, AE masks, and revision data based on PCI device ID. It clears reset, initializes transfer registers, and clears GPRs for unauthenticated firmware devices. Start either sends FCU start for authenticated chips or enables contexts and wakeup events directly for legacy unauthenticated chips.

State and persistence: persistent loader state lives in `icp_qat_fw_loader_handle`, `chip_info`, and `hal_handle->aes[]`. The file writes device CSRs, AE context status, wakeup/signal events, timestamp registers, uStore, local memory, and SRAM. Temporary microcode execution saves and restores context registers, uStore words, PC, wakeup/signals, LM addresses, and context enables.

Dependencies and integration points: depends on ADF BAR mapping, PCI IDs, QAT UOF types, CSR macros, and firmware-loader handles. `qat_uclo.c` calls these APIs to load UOF/SUOF firmware and initialize symbols. Authenticated devices rely on FCU control/status registers configured here.

Risks: this code is hardware-stateful and timeout-heavy. Several loops use shared retry counters across AEs or return generic `-EFAULT`, making failure localization difficult. Incorrect chip-info selection can program wrong offsets. Microcode execution must restore saved state exactly; missed restoration can corrupt running firmware. Test signals include reset/start success, CSR timeout paths, ECC uword correctness, 4-context versus 8-context register addressing, authenticated versus legacy start behavior, and per-device PCI ID coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_hal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_mig_dev.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_mig_dev.c

Purpose: exposes a small exported wrapper API for QAT VF migration devices. It maps a parent PCI device to an ADF accelerator, validates that the hardware supplies a full `qat_migdev_ops` table, stores VF identity, and forwards lifecycle/state-transfer calls.

Important APIs and functions: `qat_vfmig_create()` allocates `struct qat_mig_dev` and validates required ops. `qat_vfmig_init()`, `cleanup()`, `reset()`, `open()`, `close()`, `suspend()`, `resume()`, `save_state()`, `save_setup()`, `load_state()`, and `load_setup()` dispatch through `GET_VFMIG_OPS(accel_dev)`. `qat_vfmig_destroy()` frees the wrapper. All are exported GPL symbols.

Control flow: users first call create with PF `pci_dev` and VF id. The wrapper stores `parent_accel_dev`; subsequent calls fetch migration ops from that parent each time and call the matching function. There is no internal sequencing beyond create-time ops validation.

State and persistence: persistent state is only `vf_id` and `parent_accel_dev` inside `qat_mig_dev`; migration buffers and device state are owned by device-specific ops. The object lifetime is explicit and heap allocated.

Dependencies and integration points: integrates with `adf_devmgr_pci_to_accel_dev()`, ADF hardware data migration ops, and the public `<linux/qat/qat_mig_dev.h>` interface used by migration/vfio code.

Risks and test signals: after create, ops are assumed stable and non-NULL; hot-unplug or hw-data teardown must not race with callers. There is no argument validation for NULL `mdev` in forwarding functions. Tests should cover missing op rejection, parent lookup failure, VF id propagation, each forwarded op, error propagation, and lifecycle ordering around cleanup/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_mig_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_uclo.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_uclo.c

Purpose: implements the QAT UOF/SUOF/MOF firmware object loader. It validates firmware containers, maps image/chunk tables, initializes AE memory/register symbols, authenticates signed firmware through FCU where required, and writes AE/MMP images to hardware through `qat_hal`.

Important APIs and functions: public entry points are `qat_uclo_map_obj()`, `qat_uclo_del_obj()`, `qat_uclo_wr_all_uimage()`, `qat_uclo_wr_mimage()`, and `qat_uclo_set_cfg_ae_mask()`. UOF helpers validate headers/checksums, map string/initmem/image tables, assign images to AEs, set AE modes, initialize LMEM/UMEM/register symbols, fill uStore, and set PCs. SUOF helpers parse signed image tables, validate CSS headers and device compatibility, build DMA authentication descriptors, call `qat_uclo_auth_fw()`, and load images via FCU. MOF helpers locate named UOF/SUOF objects inside multi-object containers.

Control flow: `qat_uclo_map_obj()` optionally unwraps MOF by object name, then chooses SUOF for authenticated chips and UOF for legacy chips. Plain UOF mapping duplicates the firmware buffer, validates UOF and compatibility, maps image pages and AE assignments, maps init memory, and programs AE modes. Signed mapping validates SUOF, maps each signed image, checks compatibility, and may reorder AE0 image placement on non-shared uStore devices. `qat_uclo_wr_all_uimage()` writes either signed images through authentication/load or plain UOF images through global initialization plus uStore page writes.

State and persistence: loader state is stored in `handle->obj_handle`, `sobj_handle`, and `mobj_handle`. UOF mapping owns a duplicated object buffer, object header, uword buffer, image page allocations, AE slice page/region allocations, and init-memory batch lists. SUOF/MOF mapping mostly points into caller-provided firmware memory while owning metadata arrays. Auth descriptors are coherent DMA allocations and are freed after auth/load.

Dependencies and integration points: depends on firmware binary formats from `icp_qat_uclo.h`, HAL register/uStore APIs, FCU auth/load CSRs, anti-rollback checks, DMA coherent memory, and PCI device identity/revision. It is the bridge between firmware blobs requested by QAT drivers and AE hardware state.

Risks: parser code handles many pointer-plus-offset structures and must trust validated lengths; missing bounds checks around nested offsets would be high impact. Some error paths return `-ENOMEM` for format failures or may leak partially allocated SUOF/MOF metadata until outer cleanup. Auth descriptor sizing differs for RSA and dual-sign formats and must remain aligned with firmware layout. Test signals include malformed header/version/checksum rejection, MOF object lookup, device-type/revision mismatch, AE mask filtering, UOF unsupported feature rejection, initmem bounds, auth failure/retry including anti-rollback `-EAGAIN`, broadcast load, and cleanup after partial mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_uclo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/Makefile

Purpose: builds the physical-function DH895xCC QAT driver module when `CONFIG_CRYPTO_DEV_QAT_DH895xCC` is enabled.

Important declarations: the Kbuild target `qat_dh895xcc.o` is selected by the config symbol and is composed from `adf_drv.o` and `adf_dh895xcc_hw_data.o`.

Control flow and integration: this file connects the PCI probe/remove module implementation with chip-specific hardware-data initialization. It relies on common QAT objects from parent directories and produces the module that imports the `CRYPTO_QAT` namespace.

State and persistence: no runtime state is declared here; it controls build-time object aggregation only.

Risks and test signals: build tests should verify the config symbol produces exactly the PF module and that both listed objects are linked. Missing either object would leave the PCI driver without hardware callbacks or without module entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.c

Purpose: defines DH895xCC physical-function hardware characteristics and operation callbacks for the common QAT ADF layer.

Important APIs and functions: `adf_init_hw_data_dh895xcc()` fills `struct adf_hw_device_data` with BAR IDs, bank/ring counts, masks, firmware names, admin/arbiter/interrupt/reset/config callbacks, heartbeat callbacks, PF/VF messaging ops, CSR ops, and compression ops. Helpers derive accelerator/AE masks from fuses, compute capabilities from legacy fuse bits, return SKU, timestamp clock, SRAM/ETR/MISC BARs, and arbiter thread mappings. VF2PF interrupt helpers enable, disable, and atomically mask pending VF interrupts across lower/upper ERR registers. `adf_clean_hw_data_dh895xcc()` decrements class instance count.

Control flow: PF probe allocates hw data, calls this init function, then common ADF startup uses the populated callbacks for IRQ allocation, admin comms, arbiter setup, firmware config, SR-IOV, reset, and capability checks. VF2PF interrupt masking reads source and mask registers, disables all VF2PF sources, then re-enables only non-pending/non-disabled sources to avoid losing racing interrupts.

State and persistence: increments the static class instance counter and stores chip constants in `hw_data`. Runtime state such as fuse-derived masks and capability masks is kept by the caller in `hw_data`.

Dependencies and integration points: depends on gen2 QAT common config, CSR, PF/VF, heartbeat, admin, and compression helper layers. Firmware names match module firmware declarations in the PF driver.

Risks and test signals: fuse polarity is important because set bits disable units/features. VF2PF masking is race-sensitive and should be tested with simultaneous VF messages. Capability tests should cover disabled cipher/auth/PKE/compression slices. Probe tests should validate firmware names, BAR mapping, heartbeat clock, class instance accounting, and SR-IOV callback wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.h

Purpose: declares DH895xCC PF constants used by the PCI driver and hardware-data initializer.

Important definitions: BAR IDs are SRAM 0, PMISC 1, and ETR 2. Fuse constants define SKU extraction, accelerator and AE masks, maximum 6 accelerators, 12 engines, and 32 ETR banks. VF2PF macros translate ERR source/mask registers for lower and upper VF groups. AE-to-function mapping register counts and AE frequency are defined. Firmware filenames are `qat_895xcc.bin` and `qat_895xcc_mmp.bin`.

Control flow and integration: constants feed `adf_dh895xcc_hw_data.c` and `adf_drv.c` during probe, capability setup, interrupt handling, and module firmware declaration.

State and persistence: no runtime state; the constants shape `adf_hw_device_data` fields and hardware CSR access.

Risks and test signals: wrong BAR IDs or mask macros would cause register access to the wrong aperture or lost VF interrupts. Tests should compare constants against hardware documentation and validate that module firmware names match installed firmware files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_drv.c

Purpose: implements the PCI driver for Intel QAT DH895xCC physical-function devices.

Important APIs and functions: `adf_probe()` validates PCI ID and NUMA placement, allocates `adf_accel_dev` and hardware data, initializes DH895xCC hw data, reads revision/fuses, creates config, enables PCI/DMA, maps BARs, saves PCI state, starts debugfs, and calls `adf_dev_up()`. `adf_remove()` and `adf_shutdown()` stop the device; cleanup helpers unmap BARs, remove config/debugfs/devmgr entries, clean hw data, release regions, disable PCI, and free memory. Module init registers the PCI driver after requesting `intel_qat`.

Control flow: probe proceeds in staged allocation with labels for cleanup. After BAR mapping and `pci_set_master()`, `adf_dev_up(accel_dev, true)` starts full PF services including firmware and SR-IOV-capable common layers. Remove reverses startup with `adf_dev_down()`, ADF cleanup, PCI cleanup, and free. Shutdown only calls `adf_dev_down()`.

State and persistence: persistent per-device state is `adf_accel_dev`, `adf_accel_pci` BAR mappings, hw data, config table, debugfs entries, and devmgr registration. PCI saved state persists across reset/error flows.

Dependencies and integration points: depends on Linux PCI/module/DMA APIs, ADF common driver, config, debugfs, SR-IOV, error handler, and DH895xCC hw-data callbacks. Module firmware declarations integrate with request_firmware.

Risks and test signals: cleanup ordering must match successful stages; `adf_cleanup_accel()` assumes devmgr registration occurred. BAR enumeration indexes selected memory BARs into `ADF_PCI_MAX_BARS`, so platform resource ordering matters. Tests should cover invalid PCI IDs, NUMA rejection, no AE/accelerator fuse cases, DMA mask failure, BAR map failure, `adf_dev_up()` failure rollback, remove after partial probe failure, SR-IOV configure, PCI error handling, and firmware availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/Makefile

Purpose: builds the DH895xCC virtual-function QAT driver module when `CONFIG_CRYPTO_DEV_QAT_DH895xCCVF` is enabled.

Important declarations: `qat_dh895xccvf.o` is composed from `adf_drv.o` and `adf_dh895xccvf_hw_data.o`.

Control flow and integration: this Kbuild file links the VF PCI driver and VF-specific hardware-data callbacks into one module. It relies on common QAT VF/PFVF support from parent directories.

State and persistence: build-time only; no runtime state.

Risks and test signals: config/build tests should ensure the VF module does not pull PF-only objects and that both VF probe and hw-data initialization symbols are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.c

Purpose: defines hardware-data callbacks for DH895xCC SR-IOV virtual functions.

Important APIs and functions: `adf_init_hw_data_dh895xcciov()` sets one accelerator, one engine, one ETR bank, ring layout, VF IRQ resource handlers, no-op admin/arbiter/error-correction hooks, PF notification hooks (`adf_vf2pf_notify_init()` and shutdown), BAR IDs, SKU `DEV_SKU_VF`, gen2 config, class accounting, PFVF ops, CSR ops, and DC ops. `adf_clean_hw_data_dh895xcciov()` decrements class instances and updates class index.

Control flow: VF probe calls the init function after allocating `hw_data`; common `adf_dev_up(accel_dev, false)` uses the populated callbacks to configure rings and notify the PF instead of loading firmware directly.

State and persistence: class instance count is persistent across VF devices. All other state is stored in `hw_data` owned by the VF `adf_accel_dev`.

Dependencies and integration points: integrates with ADF VF ISR resources, gen2 config/CSR/DC operations, PFVF messaging, and the dev manager class index.

Risks and test signals: VF support relies on PF cooperation; no-op local admin/arbiter methods are intentional but make PF notification failures important. Tests should cover class instance accounting, PFVF init/shutdown messages, ring layout compatibility with PF, and multiple VFs probing/removing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.h

Purpose: declares DH895xCC VF constants and hw-data init/cleanup prototypes.

Important definitions: PMISC BAR is 1, ETR BAR is 0, accelerator and engine masks are both `0x1`, maximum accelerators/engines are one each, RX rings start at offset 8, TX rings mask is `0xFF`, and ETR max banks is one.

Control flow and integration: constants are used by VF hw-data initialization and VF PCI probe to configure ring and BAR access for a single virtual accelerator.

State and persistence: no runtime state; constants define the persistent hardware contract for VF instances.

Risks and test signals: mismatch with PF-provided VF resources would break ring setup or interrupt handling. Tests should verify BAR/resource mapping, ring service layout, and compatibility with `ADF_GEN2_DEFAULT_RING_TO_SRV_MAP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_drv.c

Purpose: implements the PCI driver for DH895xCC QAT virtual functions.

Important APIs and functions: `adf_probe()` validates the VF PCI ID, allocates an `adf_accel_dev`, marks it `is_vf`, links it to its PF in the device manager, initializes VF hw data, creates config, enables PCI/DMA, maps BARs, initializes VF2PF completion, starts debugfs, and calls `adf_dev_up(accel_dev, false)`. `adf_remove()` flushes VF work, stops the device, cleans ADF state, releases PCI resources, and frees memory. Module exit unregisters the PCI driver and clears the VF map.

Control flow: unlike PF probe, VF probe does not read fuse masks from hardware or save PCI state. It uses fixed one-engine masks from VF hw data and depends on PF messaging for lifecycle coordination. Remove explicitly calls `adf_flush_vf_wq()` before shutdown to drain PF/VF work.

State and persistence: persistent state includes VF `adf_accel_dev`, PF association, mapped BARs, config/debugfs, completion `accel_dev->vf.msg_received`, and devmgr registration under the PF.

Dependencies and integration points: depends on Linux PCI/DMA, ADF VF/PFVF common code, config/debugfs, and DH895xCCVF hw data. Imports `CRYPTO_QAT`.

Risks and test signals: probe assumes `pdev->physfn` maps to a PF accel device; missing PF association can affect devmgr behavior. Cleanup looks up PF during removal, so PF teardown ordering matters. Tests should cover PF absent/present probe, DMA/BAR failure rollback, VF2PF completion behavior, workqueue flushing, remove ordering, and module unload `adf_clean_vf_map(true)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/loongson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/loongson/Kconfig

Purpose: declares the configuration symbol for the Loongson RNG crypto driver.

Important declarations: `CRYPTO_DEV_LOONGSON_RNG` is a tristate option named "Support for Loongson RNG Driver" and depends on `MFD_LOONGSON_SE`.

Control flow and integration: enabling this symbol allows the Makefile to build `loongson-rng.o`. The dependency ensures the Loongson Security Engine MFD layer is present before this RNG driver can be selected.

State and persistence: build configuration only; no runtime state.

Risks and test signals: Kconfig should be validated for module and built-in combinations with `MFD_LOONGSON_SE`. Missing crypto RNG dependencies are supplied by includes/registration rather than explicit selects, so build coverage is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/loongson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/loongson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/loongson/Makefile

Purpose: adds the Loongson RNG object to the kernel build when `CONFIG_CRYPTO_DEV_LOONGSON_RNG` is enabled.

Important declarations: `obj-$(CONFIG_CRYPTO_DEV_LOONGSON_RNG) += loongson-rng.o`.

Control flow and integration: links the platform RNG driver into the crypto drivers tree under the selected config symbol.

State and persistence: build-time only.

Risks and test signals: build tests should verify the symbol compiles as module and built-in and that no additional objects are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/loongson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/loongson/loongson-rng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/loongson/loongson-rng.c

Purpose: implements a Linux crypto RNG algorithm backed by the Loongson Security Engine RNG command interface.

Important APIs and functions: `loongson_rng_generate()` sends repeated SE RNG commands and copies generated bytes from the engine data buffer to the caller. `loongson_rng_seed()` validates at least 32 bytes of seed, copies it into the engine buffer, and sends a seed command. `loongson_rng_init()` selects the least-used registered hardware RNG and increments its use count; `loongson_rng_exit()` decrements it. `loongson_rng_probe()` initializes an SE RNG engine, sets command ID/output offset, registers the global `rng_alg` once, and adds the device to a global list. The registered crypto algorithm is `stdrng` with driver name `loongson_stdrng`.

Control flow: platform probe creates one `loongson_rng`, initializes its engine through `loongson_se_init_engine(..., SE_ENGINE_RNG)`, and registers the crypto RNG on the first device. Crypto tfm init binds a tfm context to the least-used hardware device. Generate loops in chunks no larger than `engine->buffer_size`; seed uses `engine->buffer_off` and command return status to detect hardware failure.

State and persistence: global `rng_devices` contains a mutex, device list, and `registered` flag. Each device tracks `used`, an SE engine pointer, list node, and per-engine mutex. The crypto RNG registration persists after first probe. There is no remove function in this file, so list membership and registration are effectively device-lifetime/devm-managed assumptions.

Dependencies and integration points: depends on `mfd/loongson-se.h`, `loongson_se_send_engine_cmd()`, platform bus binding `"loongson-rng"`, and the kernel crypto RNG API.

Risks: `loongson_rng_init()` assumes at least one RNG device exists once the algorithm is registered; defensive NULL handling is absent. No remove/unregister path means hot-unplug behavior should be reviewed. `loongson_rng_generate()` ignores the input seed parameters and initializes `err` only through command execution in the loop, which is fine for nonzero output but should be tested for zero-length requests if allowed. Tests should cover chunked generation, hardware return error, seed length/buffer truncation, multiple devices load balancing, module unload, and platform-device removal expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/loongson/loongson-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/Kconfig

Purpose: declares Marvell crypto driver configuration symbols for CESA, OcteonTX CPT, and OcteonTX2 CPT.

Important declarations: `CRYPTO_DEV_MARVELL` is a shared tristate selected by concrete drivers. `CRYPTO_DEV_MARVELL_CESA` depends on Orion/MVEBU platforms or compile testing and selects AES/DES libraries, skcipher, hash, SRAM, and the Marvell umbrella symbol. OcteonTX and OcteonTX2 CPT options depend on appropriate architectures, PCI MSI, 64-bit, and select crypto/hash/AEAD/authenc support plus Marvell umbrella; OcteonTX2 also selects mailbox/devlink-related networking support.

Control flow and integration: these symbols drive the Marvell Makefile subdirectories. CESA builds the platform crypto engine researched in this subset; CPT symbols build separate PCI accelerator families.

State and persistence: build configuration only.

Risks and test signals: dependency/select drift can produce build failures when compile-testing. CESA needs SRAM and crypto library selects for the code paths in `cesa/`. Build matrix should cover platform, module, and `COMPILE_TEST` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/Makefile

Purpose: routes Marvell crypto configuration symbols to their implementation subdirectories.

Important declarations: `CRYPTO_DEV_MARVELL_CESA` builds `cesa/`, `CRYPTO_DEV_OCTEONTX_CPT` builds `octeontx/`, and `CRYPTO_DEV_OCTEONTX2_CPT` builds `octeontx2/`.

Control flow and integration: this is the top-level Kbuild switchboard for Marvell crypto drivers.

State and persistence: no runtime state.

Risks and test signals: build tests should verify enabling only CESA does not descend into CPT directories, and vice versa.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/Makefile

Purpose: builds the Marvell CESA crypto engine module.

Important declarations: `marvell-cesa.o` is built when `CONFIG_CRYPTO_DEV_MARVELL_CESA` is enabled and is composed of `cesa.o`, `cipher.o`, `hash.o`, and `tdma.o`.

Control flow and integration: this Kbuild file links core platform probing, skcipher algorithms, hash algorithms, and TDMA support into one driver.

State and persistence: build-time only.

Risks and test signals: missing `hash.o` or `tdma.o` would satisfy some symbols only when corresponding algorithms/features are used, so build coverage should include TDMA and hash-enabled platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.c

Purpose: implements Marvell CESA platform-device probing, engine setup, interrupt-driven request scheduling, and crypto algorithm registration.

Important APIs and functions: global `cesa_dev` exposes the single probed device to algorithm files. `mv_cesa_queue_req()` enqueues async requests and chains TDMA descriptors when needed. `mv_cesa_dequeue_req_locked()`, `mv_cesa_rearm_engine()`, `mv_cesa_std_process()`, `mv_cesa_int_process()`, and `mv_cesa_int()` implement request dispatch and interrupt completion. `mv_cesa_add_algs()`/`remove_algs()` register skcipher and ahash algorithm tables selected by SoC capability data. Probe helpers configure TDMA MBUS windows, DMA pools, SRAM, clocks, IRQs, queue/load state, and engine registers.

Control flow: probe rejects a second CESA device, picks capability tables from OF compatible data, allocates device/engine state, maps registers, creates DMA pools for TDMA-capable SoCs, maps or allocates SRAM per engine, requests threaded IRQs, initializes hardware registers and queues, sets IRQ affinity, stores `cesa_dev`, and registers algorithms. Runtime queueing selects an engine in algorithm code, enqueues the request, rearms idle engines, processes interrupts, completes backlog with `-EINPROGRESS`, and drains a complete queue outside engine ownership.

State and persistence: persistent state includes global `cesa_dev`, per-engine register/SRAM pointers, DMA address, spinlock, current request, crypto queue, atomic load, TDMA chains, complete queue, clocks, IRQ, and optional DMA pools. SRAM may come from a gen_pool or direct ioremap/resource DMA mapping.

Dependencies and integration points: depends on platform/OF bindings, MBUS DRAM info, SRAM gen_pool, DMA pools, Linux crypto async queues, CESA cipher/hash/TDMA modules, and hardware IRQ/status registers.

Risks: only one global device is supported; remove unregisters algorithms and releases SRAM but does not explicitly clear `cesa_dev`, which can affect reprobe assumptions. IRQ handling reads/clears status in a loop and relies on algorithm `process()` returning exact `0`, `-EINPROGRESS`, or error semantics. Error cleanup loops call `mv_cesa_put_sram()` for all engines, including possibly uninitialized ones. Tests should cover OF capability selection, no-SRAM fallback, TDMA and non-TDMA paths, IRQ status masks, backlog completion, engine load balancing, probe failure at each stage, remove/reprobe behavior, and known-answer crypto/hash tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.h

Purpose: central header for the Marvell CESA driver. It defines hardware registers, descriptor layouts, per-device/engine/request state, inline helpers, TDMA APIs, SRAM copy APIs, and algorithm externs.

Important APIs and types: register macros cover TDMA, interrupt, security-accelerator command/config/status, SRAM descriptor offsets, and crypto/hash descriptor fields. Core types include `mv_cesa_sec_accel_desc`, `mv_cesa_op_ctx`, `mv_cesa_tdma_desc`, `mv_cesa_caps`, `mv_cesa_dev_dma`, `mv_cesa_dev`, `mv_cesa_engine`, `mv_cesa_req_ops`, `mv_cesa_ctx`, `mv_cesa_req`, `mv_cesa_skcipher_req`, and `mv_cesa_ahash_req`. Inline helpers update operation config, adjust SRAM-relative descriptor pointers, set crypt/hash lengths, manage interrupt mask cache, select the least-loaded engine, and determine cleanup requirements.

Control flow and integration: algorithm code fills an `mv_cesa_op_ctx`, initializes either standard or DMA request state, selects an engine through `mv_cesa_select_engine()`, and submits via `mv_cesa_queue_req()`. Core interrupt code calls `ctx->ops` callbacks defined by cipher/hash files. TDMA functions declared here are implemented in `tdma.c`; SRAM SG copy is shared by standard-mode cipher/hash processing.

State and persistence: this header defines persistent device/engine state and per-request state. The global `cesa_dev` is used by inline helpers and algorithms, making the driver effectively singleton. Atomic engine load is incremented by request weight and decremented in cleanup.

Dependencies: includes crypto internal hash/skcipher APIs, DMA pool types, scatterlist concepts, gen_pool, and CESA algorithm definitions from sibling files.

Risks and test signals: singleton global access makes multi-device support and remove/reprobe delicate. Inline engine selection assumes `cesa_dev` and at least one engine are valid. Descriptor offset adjustment depends on SRAM DMA low bits matching hardware expectations. Tests should cover descriptor endianness, SRAM offset calculations, interrupt-mask caching, TDMA descriptor flags, request cleanup decisions for `-EINPROGRESS`/`-EBUSY`/errors, and load balancing across multi-engine Armada XP-like devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cipher.c

Purpose: implements CESA skcipher algorithms for DES, 3DES-EDE, and AES in ECB/CBC modes, including key setup, request initialization, standard SRAM processing, TDMA chain construction, completion, and crypto algorithm registration structures.

Important APIs and functions: context types are `mv_cesa_des_ctx`, `mv_cesa_des3_ctx`, and `mv_cesa_aes_ctx`. Request operations are collected in `mv_cesa_skcipher_req_ops`. Key setters verify DES/3DES keys and expand AES keys, including preparing decryption keys for hardware. `mv_cesa_skcipher_req_init()` validates block alignment, counts source/destination SG entries, sets crypt-only operation mode, and chooses TDMA or standard setup. Queueing goes through `mv_cesa_skcipher_queue_req()`. Exported algorithm objects include `mv_cesa_ecb_des_alg`, `mv_cesa_cbc_des_alg`, `mv_cesa_ecb_des3_ede_alg`, `mv_cesa_cbc_des3_ede_alg`, `mv_cesa_ecb_aes_alg`, and `mv_cesa_cbc_aes_alg`.

Control flow: an encrypt/decrypt method creates a local operation template with direction/mode bits, copies key and IV material as needed, initializes request state, selects a CESA engine weighted by `cryptlen`, prepares DMA or standard mode, and queues the request. Standard mode copies the operation context and a chunk of source SG data into SRAM, starts accelerator 0, copies output from SRAM on interrupt, and repeats until complete. TDMA mode maps SG lists, builds a chain of op descriptors, input transfers, dummy launch descriptors, output transfers, and a final result op to capture IV/context. Completion updates the request IV from SRAM or final TDMA op context and cleanup unmaps DMA/decrements engine load.

State and persistence: per-tfm key material persists in crypto contexts and is zeroed in `cra_exit()`. Per-request state tracks TDMA chain or standard offset/size/skip-context state plus SG entry counts. Engine load persists until cleanup.

Dependencies and integration points: depends on CESA core/header helpers, TDMA implementation, Linux AES/DES helpers, DMA mapping, scatterlists, and crypto skcipher API. Algorithms are registered by `cesa.c` capability tables.

Risks: IV update semantics must match CBC chaining and crypto API expectations. DMA error paths must unmap exactly the mappings that succeeded. Standard mode rewrites only the descriptor after first chunk with a FIXME noting finer-grained update would be better. `req->cryptlen == 0` returns synchronously with success and no queueing. Tests should include AES/DES/3DES ECB/CBC known-answer vectors, in-place and out-of-place SG lists, unaligned crypt lengths rejection, multi-SG and multi-SRAM-chunk requests, TDMA versus non-TDMA platforms, DMA map failure cleanup, IV after encrypt/decrypt, backlog behavior, and context zeroing on tfm exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cipher.c -->
