# subset-b-001233 research

This grouped report covers Intel QAT common Gen2, Gen4, and Gen6 support files under `sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common`. Each section is delimited for deterministic per-file reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.c

Purpose: Implements a debugfs `fw_counters` file that snapshots firmware request/response counters per non-admin acceleration engine (AE). It is diagnostic-only and reads live device state through the admin interface when the debugfs file is opened.

Important APIs/functions: `adf_fw_counters_dbgfs_add()` creates the file and stores the dentry in `accel_dev->fw_cntr_dbgfile`; `adf_fw_counters_dbgfs_rm()` removes it. Internally, `adf_fw_counters_get()` checks `adf_dev_started()`, computes `hw_data->ae_mask & ~hw_data->admin_ae_mask`, allocates a flexible `struct adf_fw_counters`, and fills per-AE `Requests` and `Responses` values by calling `adf_get_ae_fw_counters()`. The seq-file operations render a header row and one row per AE.

Control flow and state: State is allocated per file open, assigned to `seq_file->private`, and freed in release. The counters are a point-in-time snapshot rather than a streaming view, so repeated reads of the same opened file do not refresh hardware values. Persistent driver state is limited to the debugfs dentry pointer.

Dependencies/integration: Depends on debugfs, seq_file, QAT admin counters, `adf_accel_dev` status helpers, and `hw_device` AE/admin masks. It integrates with the driver's debugfs setup/teardown path and only works after the device has started.

Risks and test signals: The main risks are stale snapshots, admin command failure propagation, and AE mask/count mismatch returning `-EINVAL`. Tests should exercise unopened/not-started behavior, allocation failure, admin-counter error handling, seq iteration boundaries, and debugfs removal setting the dentry pointer to NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.h

Purpose: Declares the public debugfs lifecycle hooks for firmware counter reporting.

Important APIs/types: Forward-declares `struct adf_accel_dev` and exports `adf_fw_counters_dbgfs_add()` and `adf_fw_counters_dbgfs_rm()`. No data structures are exposed, keeping counter storage private to the implementation.

Control flow/state: This header does not own state. Consumers call add during debugfs/device setup and rm during teardown.

Dependencies/integration: Integrated by QAT common driver code that manages per-device debugfs files. It deliberately avoids including heavy QAT headers.

Risks and test signals: Build coverage should verify callers include this header when debugfs counters are enabled and that add/remove calls are balanced in device probe/remove or start/stop paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.c

Purpose: Builds default kernel configuration sections for Gen2 QAT devices, including crypto and compression ring instances, ring sizes, ring numbers, coalescing timers, heartbeat settings, and configured status.

Important APIs/functions: `adf_gen2_dev_config()` is the exported entry point. It creates `ADF_KERNEL_SEC`, `Accelerator0`, and `ADF_GENERAL_SEC`, then calls `adf_gen2_crypto_dev_config()` and `adf_gen2_comp_dev_config()`. Crypto instances are limited by `min(num_online_cpus(), GET_MAX_BANKS())` when crypto capability exists; compression uses the same limit for compression-capable hardware. The generated keys include `ADF_NUM_CY`, `ADF_NUM_DC`, ring bank numbers, ring sizes, TX/RX ring ids, core affinity, and coalescing timer entries.

Control flow and state: All configuration is persisted through `adf_cfg_add_key_value_param()` in the device configuration database. On success the file saves the heartbeat timer default and sets `ADF_STATUS_CONFIGURED` in `accel_dev->status`. Any failure aborts with an error log and leaves partially-added config to the surrounding config cleanup path.

Dependencies/integration: Depends on `adf_cfg`, config key strings, crypto/compression capability helpers, transport ring macros, and heartbeat configuration. It is invoked by Gen2-specific device setup before service instances are created.

Risks and test signals: Ring ids are hard-coded for the Gen2 ring layout, so regressions appear as failed service instance creation or broken request routing. Tests should verify crypto-only, compression-only, combined, and no-capability devices; CPU count greater/less than bank count; key insertion failures; and that `ADF_STATUS_CONFIGURED` is only set after all sections and keys succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.h

Purpose: Exposes the Gen2 device configuration entry point.

Important APIs/types: Includes `adf_accel_devices.h` and declares `int adf_gen2_dev_config(struct adf_accel_dev *accel_dev);`.

Control flow/state: The header owns no state. Its function initializes config sections and marks the device configured in the implementation.

Dependencies/integration: Used by Gen2 device-specific drivers to install default config before instance creation.

Risks and test signals: Build coverage should ensure Gen2 callers link against the exported implementation and that non-Gen2 code does not depend on Gen2-specific ring constants through this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.c

Purpose: Provides Gen2 implementations of the generic `adf_hw_csr_ops` ring CSR access table.

Important APIs/functions: `adf_gen2_init_hw_csr_ops()` assigns function pointers for ring base-address construction, ring head/tail reads and writes, empty status reads, ring config/base writes, interrupt flag/source/coalescing control, and ring service arbiter enable writes. The individual static functions are thin wrappers around macros in `adf_gen2_hw_csr_data.h`.

Control flow and state: No persistent state is owned. The function pointer table is populated during hardware-data initialization and later used by transport/ring code against mapped ETR CSR bases.

Dependencies/integration: Depends on `adf_hw_csr_ops`, QAT CSR read/write helpers, and the Gen2 CSR layout macros. It integrates with generic transport code through the ops table instead of exposing Gen2 offsets directly.

Risks and test signals: The wrappers are simple but sensitive to offset math and address packing. Test signals include ring setup success, correct DMA base programming for 64-bit addresses, interrupt coalescing behavior, and no regressions in service arbiter programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.h

Purpose: Defines the Gen2 ring CSR address map and macro-level register accessors used by Gen2 CSR ops.

Important APIs/types: Provides constants for ring config, base, head, tail, empty status, interrupt flag/source/coalescing registers, bundle size, arbiter slot spacing, and `WRITE_CSR_RING_SRV_ARB_EN()`. `BUILD_RING_BASE_ADDR()` converts DMA address plus ring-size encoding into hardware base format. Declares `adf_gen2_init_hw_csr_ops()`.

Control flow/state: Header macros directly read/write MMIO through `ADF_CSR_RD/WR`; no state is stored. The `WRITE_CSR_RING_BASE` macro splits lower and upper 32-bit base registers.

Dependencies/integration: Consumed by the Gen2 CSR ops implementation and generic ring/transport code through initialized ops.

Risks and test signals: Risks are incorrect bundle stride, split-base programming, and interrupt source mask values. Hardware smoke tests should validate ring producer/consumer movement, coalesced interrupts, empty-status reporting, and service arbitration under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.c

Purpose: Implements Gen2 hardware helper operations for accelerator counts, error correction, IOV thread mapping, admin/arbiter info, interrupts, capability discovery, watchdog timers, and compression request templates.

Important APIs/functions: Exported helpers include `adf_gen2_get_num_accels()`, `adf_gen2_get_num_aes()`, `adf_gen2_enable_error_correction()`, `adf_gen2_cfg_iov_thds()`, `adf_gen2_get_admin_info()`, `adf_gen2_get_arb_info()`, `adf_gen2_enable_ints()`, `adf_gen2_get_accel_cap()`, `adf_gen2_set_ssm_wdtimer()`, and `adf_gen2_init_dc_ops()`. Compression ops build Gen2 firmware config words for DEFLATE compression/decompression only.

Control flow and state: The file programs PMISC CSRs to enable AE ECC, SSM shared-memory errors, AE-to-function valid bits, interrupt masks, and watchdog timers. Capability state is computed from PCI `LEGFUSE`, straps, and fuses and returned as a mask; it is not persisted here. DC ops are stored in an ops table supplied by the caller.

Dependencies/integration: Depends on PCI config reads, QAT firmware compression structs, admin/arbiter consumers, IOV setup, and Gen2 register macros from the header.

Risks and test signals: The capability mask must match fused-off slices and power-gated PKE/DC. IOV thread valid-bit toggling can affect SR-IOV isolation. Tests should validate fuse/strap combinations, interrupt masks with/without VFs, watchdog CSR writes for each accelerator, and that unsupported compression algorithms return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.h

Purpose: Publishes Gen2 hardware constants, register helpers, and helper prototypes.

Important APIs/types: Defines Gen2 RX/TX ring layout, AE-to-function mapping registers, admin mailbox offsets, arbiter offsets/config, power-gating fuse bits, default ring-to-service map, watchdog timer offsets/values, ECC/error-correction bits, heartbeat counter count, interrupt mask offsets, and prototypes for all Gen2 hardware helper functions.

Control flow/state: Macros directly address PMISC CSRs for IOV mapping and watchdog/error-control registers. No state is owned by the header.

Dependencies/integration: Included by Gen2 product drivers and common hardware-data code that installs function pointers and constants into `adf_hw_device_data`.

Risks and test signals: Offset or mask mistakes can break service routing, heartbeat, IOV mapping, or error correction. Tests should include boot/probe on Gen2 hardware, SR-IOV enable/disable, heartbeat operation, and compression/crypto instance creation using the default ring map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.c

Purpose: Implements Gen2 PF/VF mailbox communication over a shared 32-bit CSR, including interrupt mask management, send/receive encoding, compatibility behavior, and PF/VF ops initialization.

Important APIs/functions: `adf_gen2_init_pf_pfvf_ops()` and `adf_gen2_init_vf_pfvf_ops()` populate `adf_pfvf_ops`. Static helpers map PF and VF CSR offsets, enable/disable VF2PF interrupts, atomically disable pending VF interrupts, convert 16-bit messages between PF2VF and VF2PF halves, and track the Gen2 in-use pattern. `adf_gen2_pfvf_send()` serializes with a CSR mutex, writes message plus interrupt bit, polls for ACK, handles notification collisions, and retries. `adf_gen2_pfvf_recv()` validates the interrupt bit, ignores legacy non-system messages, decodes `pfvf_message`, conditionally clears in-use bits, and ACKs by clearing the local interrupt bit.

Control flow and state: The shared CSR carries both directions, so local and remote offsets determine ownership and ACK semantics. Persistent state is external: CSR mutexes, compatibility version, PF/VF info, and interrupt masks. Notification messages intentionally preserve the in-use marker to detect collisions.

Dependencies/integration: Depends on `adf_pfvf_msg`, PF/VF protocol helpers, CSR polling, mutexes, PMISC mapping, and SR-IOV conditionals. PF ops wire VF interrupt management; VF ops only need offset and send/recv hooks.

Risks and test signals: Collision handling, legacy compatibility, and interrupt-mask races are the main risks. Tests should stress simultaneous PF/VF notifications, ACK timeout/retry paths, legacy user message filtering, `disable_pending_vf2pf_interrupts()` races, and compat versions before/after fast ACK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.h

Purpose: Declares Gen2 PF/VF communication initialization and Gen2 error source/mask offsets used for VF2PF interrupt handling.

Important APIs/types: Defines ERRSOU/ERRMSK offsets and, when `CONFIG_PCI_IOV` is enabled, declares `adf_gen2_init_pf_pfvf_ops()` and `adf_gen2_init_vf_pfvf_ops()`. Without SR-IOV, inline fallbacks disable communications by assigning `adf_pfvf_comms_disabled`.

Control flow/state: No state is stored. The compile-time branch decides whether real PF/VF ops are installed.

Dependencies/integration: Used by Gen2 PF and VF product drivers during `adf_pfvf_ops` setup.

Risks and test signals: Build matrix coverage with and without `CONFIG_PCI_IOV` is important. Runtime tests should confirm PF/VF messaging is unavailable but harmless when SR-IOV support is compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.c

Purpose: Builds default service instance configuration for Gen4 QAT devices and initializes the default service selection.

Important APIs/functions: `adf_gen4_dev_config()` creates common sections, chooses service-specific configuration through `adf_get_service_enabled()`, and marks the device configured. `adf_crypto_dev_config()` configures crypto instances using paired banks (`asym` on even bank, `sym` on odd bank) and writes `ADF_NUM_CY` plus zero `ADF_NUM_DC`. `adf_comp_dev_config()` configures compression instances with one bank per instance and writes `ADF_NUM_DC` plus zero `ADF_NUM_CY`. `adf_no_dev_config()` explicitly sets both counts to zero. `adf_gen4_cfg_dev_init()` creates the general section, defaults even accelerator ids to crypto and odd ids to compression, and saves a minimum heartbeat timer.

Control flow and state: Configuration is persisted in the QAT config table. Gen4 service mode controls which instance keys are present. `ADF_STATUS_CONFIGURED` is set only after successful instance configuration.

Dependencies/integration: Depends on config-service parsing, crypto/compression capability helpers, ring config strings, heartbeat setup, and transport macros. It is called before service instance creation.

Risks and test signals: The paired-bank crypto layout differs from Gen2 and must match Gen4 two-rings-per-bank behavior. Tests should validate each service mode (`SVC_SYM_ASYM`, `SVC_DC`, `SVC_DCC`, default/none), odd/even default service assignment, failure rollback behavior, and instance counts with CPU count versus bank count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.h

Purpose: Publishes Gen4 configuration entry points and the service-specific config builders.

Important APIs/types: Declares `adf_gen4_dev_config()`, `adf_gen4_cfg_dev_init()`, `adf_crypto_dev_config()`, `adf_comp_dev_config()`, and `adf_no_dev_config()`.

Control flow/state: The header owns no state; functions update the per-device config database and status bits in the implementation.

Dependencies/integration: Included by Gen4 product-specific drivers and any code that needs to reuse the standard Gen4 crypto/compression/no-service config builders.

Risks and test signals: Because service-specific helpers are exported through the header, ABI/API drift should be caught by build coverage across all Gen4 product drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.c

Purpose: Provides Gen4 implementations of generic ring CSR operations, including expanded status and interrupt controls not present in Gen2.

Important APIs/functions: `adf_gen4_init_hw_csr_ops()` populates function pointers for base address encoding, head/tail access, status reads (`stat`, `uo`, `e`, `ne`, `nf`, `f`, `c`, exception), exception interrupt enable access, ring config/base read/write, interrupt enable/flag/source/coalescing access, service arbiter enable, and `get_int_col_ctl_enable_mask()`.

Control flow and state: No state is stored here. The generic transport code calls through `adf_hw_csr_ops` with an ETR CSR base; this file's wrappers delegate to Gen4 offset macros.

Dependencies/integration: Depends on `adf_gen4_hw_csr_data.h`, the generic CSR ops type, and MMIO access macros. It is installed during Gen4 hardware initialization.

Risks and test signals: The larger Gen4 ring window includes `ADF_RING_CSR_ADDR_OFFSET` and 0x2000 bundle stride, so any mismatch breaks all ring operations. Tests should validate ring base readback, exception interrupt enable programming, interrupt coalescing, and service arbiter behavior for multiple banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.h

Purpose: Defines the Gen4 ring CSR layout and low-level register access macros.

Important APIs/types: Provides offsets for ring config/base/head/tail, multiple status registers, interrupt enable/flag/source/coalescing, exception status/interrupt enable, ring service arbiter, address offset, and bundle size. `BUILD_RING_BASE_ADDR()` preserves hardware-required alignment. `read_base()` handles non-contiguous LBASE/UBASE reads. Declares `adf_gen4_init_hw_csr_ops()`.

Control flow/state: Macros operate directly on MMIO addresses and do not store state. The base read/write helpers split or combine 64-bit DMA addresses.

Dependencies/integration: Consumed by `adf_gen4_hw_csr_data.c`, transport ring setup, bank reset/drain paths, and debug/status flows through `adf_hw_csr_ops`.

Risks and test signals: Risks include wrong address offset, incorrect 64-bit base handling, and interrupt/coalescing mask drift. Hardware tests should check ring traffic, interrupt source selection, base readback, and exception status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.c

Purpose: Implements core Gen4 hardware operations: BAR selection, counts, admin/arbiter offsets, heartbeat clock, PM power-up, error/interrupt setup, ring-pair reset/drain/quiesce, firmware-thread-to-arbiter mapping, ring-to-service mapping, compression request template construction, and rate-limiting slice helpers.

Important APIs/functions: Exported helpers include `adf_gen4_init_device()`, `adf_gen4_enable_ints()`, `adf_gen4_ring_pair_reset()`, `adf_gen4_init_thd2arb_map()`, `adf_gen4_get_ring_to_svc_map()`, `adf_gen4_bank_quiesce_coal_timer()`, `adf_gen4_bank_drain_start()/finish()`, `adf_gen4_services_supported()`, `adf_gen4_init_dc_ops()`, `adf_gen4_init_num_svc_aes()`, and `adf_gen4_get_svc_slice_cnt()`.

Control flow and state: `adf_gen4_init_device()` masks PM interrupt, asserts `DRV_ACTIVE`, and polls `PM_STATUS` for `INIT_STATE`. Ring reset/drain writes WQM reset control and polls reset status. Thread-to-arbiter mapping is computed from loaded firmware object AE masks, thread masks, ring-pair groups, and service mode, then stored in `hw_data->thd_to_arb_map`. Ring-to-service mapping is derived from firmware object type per RP group. Compression template ops fill firmware header command ids and hardware config words for DEFLATE and LZ4S.

Dependencies/integration: Depends on Gen4 hardware constants, PM constants, firmware config introspection callbacks, config service ids, compression firmware structs, CSR ops, and rate-limiting data. It is central to Gen4 product driver hardware setup.

Risks and test signals: Important risks are PM power-up timeout, invalid firmware object callbacks, DCC map special casing, unsupported service combinations, and ring drain/reset timeouts. Tests should cover service-mask validation, DCC versus mixed-service arb maps, ring-pair reset timeout, coalesced timer quiesce math, DEFLATE/LZ4S template generation, and slice-count reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.h

Purpose: Publishes Gen4 hardware constants, register offsets, service/ring topology constants, VF migration private state, and hardware helper prototypes.

Important APIs/types: Defines Gen4 BAR ids, KPT heartbeat frequency, fuse offsets, accelerator counts, MSI-X routing offsets, ring/bank counts, arbiter/admin offsets, default ring-to-service map, watchdog values, ring reset/drain registers, coalescing timeout constants, ERRSOU/ERRMSK offsets, rate-limiting offsets, PF2VM/VM2PF register layout, `struct adf_gen4_vfmig`, Gen4 slice mask enum, RP group enum, and prototypes for Gen4 helpers.

Control flow/state: The header defines MMIO address formulas and `adf_gen4_vfmig` state (`mstate_mgr`, per-bank stopped flags) used by migration. Runtime state is owned by callers and implementation files.

Dependencies/integration: Included by Gen4 config, PFVF, PM, RAS, VF migration, and product-specific hardware data code.

Risks and test signals: Offset and topology constants are high blast-radius. Tests should cover SR-IOV bank mapping, PF/VF mailbox offsets, MSI-X routing, rate-limiting access, ring drain/reset, heartbeat, and VF migration bank counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.c

Purpose: Implements Gen4 PF-side PF/VF communication over dedicated PF2VM and VM2PF CSRs.

Important APIs/functions: `adf_gen4_init_pf_pfvf_ops()` installs PF operations. Offset helpers return `ADF_GEN4_PF2VM_OFFSET(i)` and `ADF_GEN4_VM2PF_OFFSET(i)`. Interrupt helpers enable, disable, and atomically disable pending VM2PF interrupts using `VM2PF_SOU`/`VM2PF_MSK`. `adf_gen4_pfvf_send()` encodes a message with a 6-bit type and 24-bit payload, writes it with `ADF_PFVF_INT`, and polls for the remote side to clear the interrupt bit. `adf_gen4_pfvf_recv()` reads the CSR, filters spurious interrupts, clears the interrupt bit to ACK, and decodes the generic message.

Control flow and state: A CSR mutex serializes sends. Unlike Gen2, Gen4 has separate PF2VM/VM2PF registers and no shared in-use half-word protocol. Interrupt mask state is maintained in PMISC registers.

Dependencies/integration: Depends on Gen4 hardware-data offsets, PF/VF utility encoding, PF protocol enablement, mutexes, and poll helpers. Only PF ops are provided in this file.

Risks and test signals: ACK timeout and interrupt-mask race behavior are the main risks. Tests should validate message encoding bounds, spurious interrupt handling, pending interrupt disabling under concurrent VF events, and communication behavior across all VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.h

Purpose: Declares Gen4 PF/VF PF-side operation initialization.

Important APIs/types: Declares `adf_gen4_init_pf_pfvf_ops()` when `CONFIG_PCI_IOV` is enabled. Otherwise, an inline fallback sets `enable_comms` to `adf_pfvf_comms_disabled`.

Control flow/state: No runtime state is stored. Compile-time SR-IOV support controls whether real communication ops are installed.

Dependencies/integration: Used by Gen4 PF product drivers during PF/VF ops setup.

Risks and test signals: Build tests should cover `CONFIG_PCI_IOV=y/n`. Runtime tests should confirm no accidental PF/VF communication dependency when SR-IOV is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.c

Purpose: Enables Gen4 power management and handles PM interrupts through deferred work.

Important APIs/functions: `adf_gen4_enable_pm()` initializes firmware PM via `adf_init_admin_pm()`, initializes debugfs PM data, enables idle/throttle interrupt bits, clears PM status bits, and unmasks PM in `ERRMSK2`. `adf_gen4_handle_pm_interrupt()` filters for unmasked PM source in `ERRSOU2`, masks PM interrupts, captures `PM_INTERRUPT`, allocates `adf_gen4_pm_data`, and queues `pm_bh_handler()`. `send_host_msg()` sends `PM_SET_MIN` or `PM_NO_CHANGE` based on `ADF_PM_IDLE_SUPPORT` config and polls for firmware to clear the pending bit.

Control flow and state: Interrupt top-half work is minimal and allocates per-event work data. Bottom-half work increments counters in `accel_dev->power_management`, sends host idle acknowledgement/nack, clears PM interrupt status, unmasks PM, and frees work data. Persistent state consists of PM counters and the debugfs print callback installed elsewhere.

Dependencies/integration: Depends on PM CSRs from `adf_gen4_pm.h`, admin PM initialization, config lookup, the miscellaneous workqueue, and Gen4 ERRSOU/ERRMSK constants.

Risks and test signals: `kzalloc(GFP_ATOMIC)` failure causes the handler to return false after masking PM, which is a notable risk. Tests should exercise idle/throttle/fw interrupts, idle-support config parsing defaults, host message busy/timeout, workqueue execution, and PM interrupt re-enable after bottom-half completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.h

Purpose: Defines Gen4 power-management registers, bit masks, host-message payloads, and public PM functions.

Important APIs/types: `enum qat_pm_host_msg` has `PM_NO_CHANGE` and `PM_SET_MIN`. The header defines PM host message/status/interrupt offsets, ERRSOU2 PM source, interrupt enable/status bits, pending/payload masks, idle filter defaults, PM debug field masks, and active/managed SSM slice count masks. Declares `adf_gen4_enable_pm()` and `adf_gen4_handle_pm_interrupt()`, plus debugfs `adf_gen4_init_dev_pm_data()` or an inline no-op.

Control flow/state: No state is stored. The masks are consumed by PM enable, interrupt handling, and PM debugfs formatting.

Dependencies/integration: Included by Gen4 PM, PM debugfs, and Gen4 hardware power-up code.

Risks and test signals: Register mask drift can break PM interrupt handling or debugfs decoding. Tests should cover PM enabled with and without debugfs and verify decoded PM status fields against known firmware data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm_debugfs.c

Purpose: Provides the Gen4 debugfs PM status printer used by the common PM debugfs utilities.

Important APIs/functions: `adf_gen4_init_dev_pm_data()` sets `accel_dev->power_management.print_pm_status` and marks PM present. `adf_gen4_print_pm_status()` allocates a firmware PM info page and output buffer, DMA maps the PM info buffer, calls `adf_get_pm_info()`, formats fuse, PM, SSM, log/event, interrupt counter, host ack/nack counter, and hardware CSR sections, then copies to userspace via `simple_read_from_buffer()`.

Control flow and state: Reads firmware state on each debugfs read. It does not persist the snapshot, but it reports persistent PM counters stored in `accel_dev->power_management`. DMA mapping is always unmapped after admin query.

Dependencies/integration: Depends on `icp_qat_fw_init_admin_pm_info`, admin PM query, DMA mapping, PM debugfs table formatting helpers, Gen4 PM masks, and direct PM CSR reads.

Risks and test signals: Output is PAGE_SIZE-bounded; adding rows can truncate silently through `scnprintf`. Tests should check allocation and DMA mapping failures, admin query errors, `pos` handling for repeated reads, and field decoding for all row tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.c

Purpose: Implements Gen4 Reliability, Availability, and Serviceability operations: enabling/disabling hardware error reporting and demultiplexing RAS interrupts into logs, counters, CSR clears, and reset-required decisions.

Important APIs/functions: `adf_gen4_init_ras_ops()` installs `enable_ras_errors`, `disable_ras_errors`, and `handle_interrupt`. Enable/disable helpers program ERRSOU masks, AE logs, CPP command parity, RI/TI parity, RF parity, SSM error handling, and ARAM ECC/error controls. `adf_gen4_handle_interrupt()` reads ERRSOU0..3 and dispatches to `adf_gen4_process_errsou0/1/2/3()`.

Control flow and state: ERRSOU0 handles correctable AE errors. ERRSOU1 handles AE uncorrectable, CPP command parity, RI memory parity, TI memory parity groups, and IOSFP command parity. ERRSOU2 handles SSM and CPP CFC errors. ERRSOU3 handles TI misc, RI/TI CPP interface, ARAM correctable/uncorrectable, ARAM memory target, and ATU faults. Handlers increment `accel_dev->ras_errors` counters, log with `dev_warn` or `dev_err`, clear status CSRs by writing the observed bits, and OR fatal conditions into `*reset_required`.

Dependencies/integration: Depends on Gen4 hardware and RAS headers, ARAM and PMISC BAR mappings, `adf_sysfs_ras_counters`, and per-device error masks from `GET_ERR_MASK()`. It is called from the common interrupt/RAS handling path.

Risks and test signals: The code is register-mask dense; risks include over-clearing status, missing optional WAT/WCP masks, misclassifying fatal versus uncorrectable errors, and reset-required decisions drifting from hardware requirements. Tests should inject or emulate ERRSOU bits for each group, verify counter class increments, verify status clear writes, confirm optional mask behavior, and check that fatal SPP command, SSM CPP fatal, CPP CFC command/multiple, RI fatal, TIMISC, and ARAM multiple errors request reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.h

Purpose: Defines the Gen4 RAS register map, error source masks, per-block status/control masks, and the RAS ops initializer declaration.

Important APIs/types: The header enumerates ERRSOU0..3 source bits, AE correctable/uncorrectable log offsets, CPP command parity registers, RI/TI parity status and masks, SSM interrupt/status/control registers, SPP pull/push command/data parity registers, SER SSM shared-memory masks, CPP CFC registers, SSM compression/translator/decompression exception registers, ARAM ECC/memory target registers, ATU fault registers, and `adf_gen4_init_ras_ops()`.

Control flow/state: No state is stored, but these constants directly drive enable/disable and interrupt clear behavior in `adf_gen4_ras.c`. Several masks encode severity by grouping correctable, uncorrectable, and fatal bits.

Dependencies/integration: Included by Gen4 RAS implementation and tied to `adf_ras_ops` from common device data.

Risks and test signals: Header mask errors cause incorrect RAS behavior across the driver. Tests should compare masks with hardware documentation, compile all users, and verify each named mask through targeted fault injection or CSR mock tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.c

Purpose: Supplies Gen4 telemetry layout metadata and debug counter descriptors.

Important APIs/functions: `adf_gen4_init_tl_data()` fills `adf_tl_hw_data` with layout sizes, number of history buffers, max monitored ring pairs, message counter offset, CPP nanoseconds per cycle, bandwidth conversion factor, counter descriptor arrays, and maximum slice count. Counter arrays describe device-level PCIe/latency/bandwidth/DevTLB metrics, slice utilization/execution metrics, and ring-pair metrics.

Control flow and state: No hardware state is read here. The file describes offsets into firmware-populated telemetry shared memory; telemetry collection/debugfs code uses the descriptors later to interpret snapshots.

Dependencies/integration: Depends on `adf_telemetry` and `adf_tl_debugfs` macros and the Gen4 telemetry structs in the header. Compiled only into debugfs/telemetry capable paths through the header guard.

Risks and test signals: Counter offsets must match the packed layout. Tests should verify `layout_sz`, slice/ring-pair sizes, message count offset, descriptor counts, and sample debugfs output from known telemetry buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.h

Purpose: Defines the Gen4 firmware telemetry memory layout and telemetry constants.

Important APIs/types: Defines conversion constants, maximum aggregation time, history buffer count, max slices per type, max ring pairs, `struct adf_gen4_tl_slice_data_regs`, `struct adf_gen4_tl_device_data_regs`, `struct adf_gen4_tl_ring_pair_data_regs`, `struct adf_gen4_tl_layout`, layout size macros, and message count offset. Declares `adf_gen4_init_tl_data()` under `CONFIG_DEBUG_FS`, otherwise an inline no-op.

Control flow/state: The structs describe shared telemetry state populated by firmware/device code and consumed by debugfs readers. The header itself stores no state.

Dependencies/integration: Integrated with the common telemetry subsystem through `adf_tl_hw_data`.

Risks and test signals: Struct layout changes are ABI-sensitive against firmware. Tests should use static layout/offset assertions where possible and validate telemetry parsing with firmware-produced buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_tl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.c

Purpose: Implements Gen4 VF live-migration device operations, including migration buffer setup, VF bank quiesce/resume, compatibility checks, state serialization, and state restore.

Important APIs/functions: `adf_gen4_init_vf_mig_ops()` fills `qat_migdev_ops`. Device lifecycle functions allocate/free a 4096-byte state buffer, open/close per-VF `adf_gen4_vfmig` with an `adf_mstate_mgr`, and reset setup sizes. `adf_gen4_vfmig_suspend_device()` drains each VF bank, records stopped banks, and quiesces coalescing timers; resume clears drain status for stopped banks. Save/load setup handles config sections for capabilities, ring-to-service map, and extended DC capabilities. Save/load state handles generic VF state, misc PF2VM/VM2PF/VINT registers, and ETR bank state.

Control flow and state: Migration state is organized with `adf_mstate_mgr` sections: config/setup, generic VF fields, misc BAR registers, and per-bank ETR registers. `mdev->setup_size` and `remote_setup_size` split static setup from dynamic state. Rate-limiting SLAs are serialized as `mig_user_sla` records and checked on load to ensure destination CIR/PIR and service/ring-pair coverage are sufficient. PFVF misc save takes `pfvf_mig_lock` with a timeout to avoid racing PF/VF messages.

Dependencies/integration: Depends on bank state save/restore callbacks, Gen4 bank drain/quiesce helpers, PFVF compatibility helpers, rate limiting, migration state manager APIs, VF info fields, and Gen4 mailbox/VINT offsets.

Risks and test signals: Risks include insufficient 4096-byte state space, partial setup loads returning `-EAGAIN`, PFVF lock timeout, SLA mismatch, incompatible VF protocol version, capability mask mismatch, and failure to resume drained banks after errors. Tests should cover save/load round trips, partial remote setup lengths, incompatible/newer VF compat versions, destination capability superset/equality rules, SLA capacity checks, bank save/restore failures, and suspend/resume cleanup after a mid-bank drain failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.h

Purpose: Declares the Gen4 VF migration ops initializer.

Important APIs/types: Includes `adf_accel_devices.h` and declares `void adf_gen4_init_vf_mig_ops(struct qat_migdev_ops *vfmig_ops);`.

Control flow/state: No state is stored. The implementation installs all lifecycle, suspend/resume, setup, and state save/load callbacks into the supplied ops table.

Dependencies/integration: Used by Gen4 product drivers that expose VF migration support.

Risks and test signals: Build coverage should ensure migration-capable products include this header and link the implementation. Runtime validation is through the ops table installed by this single entry point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm.h

Purpose: Defines Gen6 PM register offsets, masks, defaults, and debugfs data initialization hook.

Important APIs/types: Defines PM poll timing, `PM_STATUS`, `PM_INTERRUPT`, PM source bit, `DRV_ACTIVE`, default idle filter, init-state and CPM state masks, fuse PM enable masks, firmware idle masks, SSM PM enable/domain powered-up masks, and `adf_gen6_init_dev_pm_data()` under `CONFIG_DEBUG_FS` with an inline no-op fallback.

Control flow/state: No state is stored. Gen6 PM debugfs and product power-up code use these masks to decode status and expose PM data.

Dependencies/integration: Included by Gen6 PM debugfs and Gen6 hardware data paths. It is intentionally smaller than Gen4 PM because Gen6 debug status exposes fewer fields and no host message protocol in this file set.

Risks and test signals: Register mask drift affects PM status decoding. Build tests should cover debugfs on/off, and runtime tests should verify PM debug output for init state, CPM state, idle enable/filter, and SSM powered-up status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm_dbgfs.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm_dbgfs.c

Purpose: Provides Gen6 PM debugfs status printing.

Important APIs/functions: `adf_gen6_init_dev_pm_data()` installs `adf_gen6_print_pm_status()` and marks PM present. The printer allocates zeroed PM info and output pages, DMA maps the info page, calls `adf_get_pm_info()`, formats PM fuse, PM info, SSM PM info, and hardware CSR sections, reads `ADF_GEN6_PM_INTERRUPT`, and returns data via `simple_read_from_buffer()`.

Control flow and state: Each read captures fresh firmware PM info. It stores only the print callback and `present` flag in `accel_dev->power_management`; no counters are maintained here.

Dependencies/integration: Depends on Gen6 PM masks, admin PM info query, DMA mapping, PM debugfs formatting helpers, and PMISC CSR access.

Risks and test signals: PAGE_SIZE output limits and DMA/admin failures are the main operational risks. Tests should validate allocation failure paths, DMA mapping error handling, admin query failure, repeated reads with offsets, and field decoding versus known firmware PM info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_pm_dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.c

Purpose: Implements Gen6 RAS enable/disable and interrupt handling for correctable, uncorrectable, and fatal hardware errors.

Important APIs/functions: `adf_gen6_init_ras_ops()` installs Gen6 RAS callbacks. Enable/disable helpers program ERRSOU masks, AE logs, CPP command parity, CPP CFC control, RI/TI parity, TIMISC, RI/TI CPP interface controls, and SSM interrupt masks. `adf_gen6_handle_interrupt()` reads ERRSOU0..3, dispatches to processors, and then calls `adf_gen6_is_reset_required()`.

Control flow and state: ERRSOU0 handles correctable AE logs. ERRSOU1 handles AE uncorrectable, CPP command parity, RI memory parity, TI parity group, IOSFP command parity, and SFI command parity. ERRSOU2 handles SSM and CPP CFC. ERRSOU3 handles TI misc, RI/TI CPP interface errors, ATU faults, rate-limiting block errors, VFLR, PCIe TC/VC mapping, PCIe/page-request/translation DEVHALT, and TI internal DEVHALT. Handlers log, increment `accel_dev->ras_errors`, and clear status CSRs. After processing, the reset decision is derived from `GENSTS`: PFLR is required when device state is DEVHALT and reset type is PFLR; cold reset is logged but `reset_required` is false for that path.

Dependencies/integration: Depends on `adf_gen6_ras.h` constants, PMISC mapping, bitfield helpers, and sysfs RAS counters. Compared with Gen4 it does not use ARAM BAR helpers and has a hardware-state based reset decision.

Risks and test signals: Important risks are status bits remaining set after handler clears, severity classification, and reset decision interpretation from `GENSTS`. Tests should inject each ERRSOU group, verify counter classes and clear writes, check warnings for still-set ERRSOU registers, and cover GENSTS DEVHALT/PFLR and cold-reset cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.c -->
