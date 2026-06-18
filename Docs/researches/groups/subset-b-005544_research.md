# Research: subset-b-005544

This grouped report covers the requested vDPA core, simulator, VDUSE IOVA, Octeon EP, AMD/Pensando PDS, and SolidRun driver files. Each file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_hw.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_hw.c

Purpose: Implements low-level Marvell Octeon endpoint vDPA hardware access: emulated virtio PCI capability discovery, feature/status/config MMIO, queue register programming, notify address setup, and firmware mailbox commands for virtqueue state.

Important APIs and functions: `octep_verify_features()` enforces mandatory `VIRTIO_F_VERSION_1`, `VIRTIO_F_NOTIFICATION_DATA`, and `VIRTIO_F_RING_PACKED`; `octep_hw_get_status()`, `octep_hw_set_status()`, and `octep_hw_reset()` wrap virtio common status; `octep_hw_get_dev_features()`, `octep_hw_get_drv_features()`, and `octep_hw_set_drv_features()` select low/high feature words through firmware-acknowledged selectors. Queue APIs include `octep_set_vq_address()`, `octep_set_vq_num()`, `octep_set_vq_ready()`, `octep_get_vq_ready()`, `octep_get_vq_size()`, and `octep_notify_queue()`. `octep_hw_caps_read()` is the main setup entry.

Control flow: `octep_hw_caps_read()` verifies firmware signatures in BAR memory, walks the emulated PCI capability list, maps common/notify/device/ISR regions, processes vendor config records to learn virtio device ID, reads features and queue count, allocates `oct_hw->vqs`, computes per-queue notify and callback-notify addresses, and initializes the mailbox. Mailbox commands serialize through `octep_process_mbox()`: wait for available status, write optional payload and queue id, write request header, poll for response signature/status, then copy response data for reads.

State and persistence: State lives in MMIO registers, `oct_hw` fields, and firmware mailbox memory. There is no disk persistence. Queue state is persisted in device firmware and moved through `vdpa_vq_state` mailbox commands. Config reads use `config_generation` retry loops for consistent snapshots.

Dependencies and integration points: Depends on `octep_vdpa.h`, virtio PCI common structs, `ioread/iowrite`, PCI BAR resources, and firmware-specific signatures/offsets. Upper-layer Octeon vDPA ops call these helpers from `octep_vdpa_main.c`.

Risks: Hardware/firmware protocol assumptions are strict: unaligned mailbox buffers fail, missing ACK-bit clear causes feature or queue select timeouts, and invalid cap lengths/BARs abort setup. `octep_process_mbox()` lacks an explicit mutex, so callers must avoid concurrent mailbox users. Feature verification rejects devices that do not support packed rings and notification data.

Test signals: Probe logs should show mapped common/device/ISR/notify regions, device features, maximum queues, and mailbox mapping. Negative tests include firmware signature mismatch, malformed caps, missing mandatory features, feature selector timeout, queue selector timeout, mailbox timeout/signature failure, and get/set vq state round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_main.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_main.c

Purpose: Provides the Marvell Octeon PCI vDPA driver: PF SR-IOV setup, VF firmware readiness handling, vDPA management device registration, vDPA device creation, vDPA config ops, IRQ allocation, reset, and teardown.

Important APIs/types/functions: Defines `struct octep_pf`, `struct octep_vdpa`, and `struct octep_vdpa_mgmt_dev`. The `octep_vdpa_ops` table implements feature negotiation, status, reset, vq address/size/ready/state/callbacks, notification area, config reads, and device/vendor IDs. `octep_vdpa_probe_pf()` and `octep_vdpa_probe_vf()` split PF/VF lifecycle. `octep_vdpa_setup_task()` waits for firmware BAR initialization, maps caps, reads hardware capabilities, and registers `vdpa_mgmt_dev`. `octep_sriov_enable()` assigns VF BAR windows and signals ready signatures.

Control flow: PF probe enables PCI, maps the mailbox BAR, computes VF stride/device ID, shrinks the PF BAR resource window, and exposes SR-IOV configuration. Enabling VFs calls PCI SR-IOV, finds VFs by Cavium vendor/device, assigns BAR space out of the PF aperture, then writes per-VF ready signatures. VF probe enables DMA, maps mailbox BAR, allocates management state, and schedules setup work. The setup work waits up to 5 seconds for `OCTEP_DEV_READY_SIGNATURE`, maps caps, reads number of callback interrupts, calls `octep_hw_caps_read()`, then registers the management device. `dev_add` allocates `struct octep_vdpa`, filters provisioned features, validates mandatory features, names the device, and registers it with the vDPA bus.

State and persistence: Runtime state is in PCI driver data, `octep_hw`, per-VQ callbacks, IRQ vector arrays, atomic setup status, and firmware/MMIO. Reset clears callbacks and config callback, resets device status, and releases IRQs if the driver had reached `DRIVER_OK`.

Dependencies and integration points: Integrates with PCI core, SR-IOV, vDPA management bus, Octeon hardware helpers, virtio IDs, IOMMU/DMA mask, MSI-X interrupts, and kernel workqueues. Uses `_vdpa_register_device()` because management `dev_add` runs under vDPA's global device lock.

Risks: VF readiness is asynchronous; removal must cancel setup work before unregistering. PF BAR shrink/expand manipulates PCI resources and is platform-sensitive. IRQ handler maps shared interrupt vectors to queues by vector arithmetic and stops after first matching callback notification. `kick_vq` is intentionally unsupported; data-bearing kicks are required.

Test signals: Exercise PF probe, SR-IOV enable/disable, VF probe readiness timeout and success, netlink `vdpa dev add/del`, feature filtering, reset during setup, IRQ callback delivery, config change callback on ISR, and packed-ring vq state mailbox migration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/Makefile

Purpose: Builds the AMD/Pensando PDS vDPA module when `CONFIG_PDS_VDPA` is enabled.

Important APIs/types/functions: The Kbuild target is `obj-$(CONFIG_PDS_VDPA) := pds_vdpa.o`, with module objects `aux_drv.o`, `cmds.o`, `debugfs.o`, and `vdpa_dev.o`.

Control flow: Kernel build links the auxiliary-bus driver, admin command wrappers, debugfs support, and vDPA device implementation into one `pds_vdpa` module.

State and persistence: No runtime state; this file only controls compilation.

Dependencies and integration points: Depends on the Kconfig symbol and the PDS common/adminq/auxbus headers used by the component C files.

Risks: Omitting any object breaks core lifecycle: `aux_drv.o` owns module init/probe, `vdpa_dev.o` owns vDPA ops, `cmds.o` owns firmware commands, and `debugfs.o` owns observability.

Test signals: Build with `CONFIG_PDS_VDPA=m/y` and verify the final object contains symbols from all four listed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.c

Purpose: Implements module init/exit and auxiliary-bus probe/remove for AMD/Pensando vDPA VFs exposed by the PDS core driver.

Important APIs/functions: `pds_vdpa_probe()` allocates `struct pds_vdpa_aux`, validates VF ID, obtains management identity via `pds_vdpa_get_mgmt_info()`, probes modern virtio PCI config with `vp_modern_probe()`, registers `vdpa_mgmtdev_register()`, and creates debugfs entries. `pds_vdpa_remove()` unregisters the management device, releases IRQs, removes virtio PCI modern mappings, tears down debugfs, and frees memory. Module init/exit wrap `auxiliary_driver_register()` and debugfs root creation/destruction.

Control flow: The PDS core publishes an auxiliary device named for vDPA. Probe captures the parent `pds_auxiliary_dev`, derives `vf_id` from the VF PCI device, asks firmware for vDPA identity, probes virtio config space on the VF, and only then registers with the generic vDPA management layer. Error paths unwind in reverse order: virtio remove, IRQ vector free, memory free, drvdata clear.

State and persistence: `struct pds_vdpa_aux` is the per-auxiliary-device anchor and stores the PDS auxiliary device, `vdpa_mgmt_dev`, active `pds_vdpa_device`, firmware identity, VF ID, debugfs dentry, virtio modern device, and interrupt count.

Dependencies and integration points: Uses Linux auxiliary bus, PCI, vDPA, virtio PCI modern helpers, and PDS common/core/adminq/auxbus APIs. It is the registration bridge between the PDS PF adminq service and generic vDPA user-visible management.

Risks: Probe ordering is important: debugfs identity assumes `pds_vdpa_get_mgmt_info()` succeeded, and management registration assumes `vp_modern_probe()` found valid virtio regions. Remove calls `pds_vdpa_release_irqs(vdpa_aux->pdsv)` safely with possible NULL, but removal during an active vDPA device relies on management unregister deleting child devices first.

Test signals: Auxiliary probe should create a management device and debugfs directory for the VF. Failure injection for identity command, virtio modern probe, and management registration should unwind without leaked IRQ vectors or stale drvdata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.h

Purpose: Declares the per-auxiliary-device state and driver naming constants for the PDS vDPA driver.

Important APIs/types: `PDS_VDPA_DRV_DESCRIPTION` and `PDS_VDPA_DRV_NAME` feed module and debug naming. `struct pds_vdpa_aux` stores the parent `pds_auxiliary_dev`, registered `vdpa_mgmt_dev`, active `pds_vdpa_device`, firmware identity block, VF ID, debugfs dentry, `virtio_pci_modern_device`, and allocated interrupt count.

Control flow: This header is included by probe, debugfs, command, and device files so they share the same auxiliary state anchor.

State and persistence: Pure runtime state; no persistent storage. The `pdsv` pointer is NULL until `dev_add`, and `nintrs` tracks whether MSI-X vectors must be freed.

Dependencies and integration points: Includes `linux/virtio_pci_modern.h` and relies on PDS types from included C files. It connects the PDS auxiliary bus object with the vDPA management object and virtio PCI modern config access.

Risks: Ownership is split: `aux_drv.c` owns allocation/free of `pds_vdpa_aux`, while `vdpa_dev.c` owns the child `pds_vdpa_device` and writes `vdpa_aux->pdsv`. Bugs in that handoff can produce stale debugfs/private pointers.

Test signals: Compile-time signal is clean inclusion by all PDS C files; runtime signal is correct NULL/non-NULL `pdsv` transitions during `vdpa dev add/del`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.c

Purpose: Wraps PDS admin queue commands used by the vDPA driver to initialize/reset hardware, update status and attributes, and initialize/reset individual virtqueues.

Important APIs/functions: `pds_vdpa_init_hw()`, `pds_vdpa_cmd_reset()`, `pds_vdpa_cmd_set_status()`, `pds_vdpa_cmd_set_mac()`, `pds_vdpa_cmd_set_max_vq_pairs()`, `pds_vdpa_cmd_init_vq()`, and `pds_vdpa_cmd_reset_vq()` all build `union pds_core_adminq_cmd` requests and call `pds_client_adminq_cmd()`.

Control flow: Each wrapper fills opcode, vDPA index, VF ID, and command-specific payload. VQ init sends queue length as `ilog2(q_len)`, ring addresses, interrupt index, and avail/used indexes with packed-ring invert handling applied by the caller. VQ reset asks firmware to stop/reset the queue, then copies returned avail/used indexes back into software state after undoing the invert mask.

State and persistence: Commands mutate firmware-managed VF/vDPA state. Software state is mostly read-only input except `pds_vdpa_cmd_reset_vq()`, which updates `vq_info->avail_idx` and `vq_info->used_idx`.

Dependencies and integration points: Depends on PDS adminq definitions from `linux/pds/*`, `struct pds_vdpa_device`, and `struct pds_vdpa_vq_info`. Called by `vdpa_dev.c` during `dev_add`, status changes, reset, queue ready transitions, and MAC/max-queue configuration.

Risks: Queue length must be a valid power-of-two-like value for `ilog2` encoding to match firmware expectations. Adminq errors are logged at debug level in wrappers and often escalated by callers. Endianness conversion is explicit and must match firmware ABI. Incorrect invert handling breaks packed-ring migration indices.

Test signals: Adminq traces should show IDENT/INIT/RESET/STATUS/SET_ATTR/VQ_INIT/VQ_RESET commands. Test queue ready toggles, reset index recovery, MAC provisioning, max queue pair changes, and firmware error status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.h

Purpose: Declares the PDS vDPA admin command wrapper interface consumed by the vDPA device implementation.

Important APIs: Prototypes cover hardware init/reset/status, MAC and max VQ pair attributes, and VQ init/reset commands carrying `struct pds_vdpa_vq_info`.

Control flow: `vdpa_dev.c` includes this header and calls the wrappers at lifecycle boundaries: `dev_add`, `set_status`, `reset`, and `set_vq_ready`.

State and persistence: No state in the header. It defines the command interface that mutates firmware state and updates VQ indices through pointer arguments.

Dependencies and integration points: Requires visible declarations of `struct pds_vdpa_device` and `struct pds_vdpa_vq_info` from `vdpa_dev.h`.

Risks: Prototype drift from command implementation or caller expectations would cause compile failures or ABI misuse. Invert index arguments must be supplied consistently for packed-ring queues.

Test signals: Full PDS module build validates prototypes; queue lifecycle tests validate caller/command contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.c

Purpose: Provides debugfs observability for PDS vDPA management identity, virtio net config/status/features, and per-virtqueue software state.

Important APIs/functions: `pds_vdpa_debugfs_create()` and `destroy()` manage the root. `pds_vdpa_debugfs_add_pcidev()`, `add_ident()`, `add_vdpadev()`, `del_vdpadev()`, and `reset_vdpadev()` manage per-VF files. Show handlers render identity, config, and per-VQ data. `print_feature_bits_all()` decodes many virtio net and transport feature bits.

Control flow: Probe creates a PCI-device directory and identity file after firmware identity is read. `dev_add` adds a config file and one file per VQ. `dev_del` resets the vDPA-specific files by removing and rebuilding the base directory and identity file.

State and persistence: Debugfs files are read-only views over live driver state and MMIO config. `config_show()` reads the virtio net config from the modern device's `device` region and status through `vp_modern_get_status()`. VQ files reflect `pds_vdpa_vq_info`.

Dependencies and integration points: Depends on Linux debugfs/seq_file, virtio net config layout, PDS auxiliary state, and PDS vDPA device structs. It is optional observability, not required for data path.

Risks: Debugfs pointers become invalid if files outlive the associated `vdpa_aux` or `pdsv`; lifecycle functions remove/recreate entries to avoid that. Feature decoding is hard-coded and will show unknown bits as `bit_N`. `pds_vdpa_debugfs_del_vdpadev()` removes the whole PCI directory, so callers must recreate identity after device deletion.

Test signals: Inspect `/sys/kernel/debug/<module>/<pci>/identity`, `config`, and `vqNN` while adding/removing devices. Verify feature names, status bits, queue addresses/indices, and absence of stale files after `dev_del` and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.h

Purpose: Declares the PDS vDPA debugfs lifecycle functions.

Important APIs: Root management functions `pds_vdpa_debugfs_create()` and `destroy()`, PCI/identity creation functions, vDPA device file add/delete, and vDPA debugfs reset.

Control flow: `aux_drv.c` calls root create/destroy at module init/exit and base debugfs creation at probe. `vdpa_dev.c` calls vDPA add/reset around `dev_add` and `dev_del`.

State and persistence: No state in the header; functions manage in-kernel debugfs dentries.

Dependencies and integration points: Includes `linux/debugfs.h` and expects `struct pds_vdpa_aux` from the shared PDS driver context.

Risks: Header users must call functions in lifecycle order; reset assumes a valid auxiliary object and rebuilds base entries.

Test signals: Compile-time linkage and runtime debugfs directory creation/removal validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.c

Purpose: Implements the PDS vDPA management-device callbacks and `vdpa_config_ops` for a virtio-net VF backed by PDS firmware/adminq and virtio PCI modern config space.

Important APIs/functions: `pds_vdpa_dev_add()` and `pds_vdpa_dev_del()` create/delete one vDPA device per VF. The `pds_vdpa_ops` table implements queue address/size/kick/callback/ready/state/notification/IRQ/group, feature negotiation, config callbacks, status/reset, config reads/writes, and identity. `pds_vdpa_get_mgmt_info()` retrieves firmware identity via DMA-mapped adminq output.

Control flow: `dev_add` rejects multiple devices per VF, allocates `struct pds_vdpa_device`, verifies PCI status, applies requested feature mask, resets and initializes firmware, calculates queue count from firmware max VQs and requested max VQ pairs, sets MAC, maps notification addresses, initializes VQ entries, registers PDS event notifier, registers the vDPA device, and creates debugfs. Status transition to `DRIVER_OK` allocates one MSI-X vector per supported VQ; transition to `FEATURES_OK` maps notify pages; status reset clears callbacks, resets hardware, zeroes indices, and restores MAC. Queue ready true sends VQ init adminq; false sends VQ reset and stores returned indices.

State and persistence: `struct pds_vdpa_device` stores supported/negotiated features, selected MAC, num_vqs, callbacks, notifier, and an array of `pds_vdpa_vq_info` with addresses, q length, IRQ, notify mapping, and migration indices. Firmware persists active VQ and device status until reset.

Dependencies and integration points: Uses PDS adminq wrappers, virtio PCI modern helpers, PCI MSI-X, vDPA bus, netlink-supplied `vdpa_dev_set_config`, PDS event notifier API, and debugfs. `vmap.dma_dev` points to the VF PCI device for DMA mapping.

Risks: Driver requires `VIRTIO_F_ACCESS_PLATFORM` when any features are negotiated. It advertises `VIRTIO_NET_F_MAC` even if hardware lacks it and strips the bit before writing features to hardware. VQ state get/set is forbidden while ready. Split rings lack a used index, so used is forced to avail for interoperability. IRQ allocation asks for `max_supported_vqs`, but only requests IRQ handlers for `num_vqs`.

Test signals: Netlink add with feature/MAC/max-vq-pair masks, invalid unsupported features, missing access-platform negotiation, queue ready toggles, packed and split state migration, PDS reset/link-change notifier triggering config callback, debugfs contents, and MSI-X allocation/release on DRIVER_OK transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.h

Purpose: Declares PDS vDPA queue and device runtime structures plus public helper prototypes.

Important APIs/types: `struct pds_vdpa_vq_info` holds VQ readiness, descriptor/avail/used addresses, queue length, qid, IRQ metadata, notify mapping, doorbell, migration indices, callback, and parent pointer. `struct pds_vdpa_device` embeds `vdpa_device`, links to `pds_vdpa_aux`, stores fixed-size VQ array, feature masks, vDPA index, queue count, MAC, config callback, and notifier block. Constants include `PDS_VDPA_MAX_QUEUES`, `PDS_VDPA_MAX_QLEN`, and `PDS_VDPA_PACKED_INVERT_IDX`.

Control flow: Structures are populated during `dev_add`, updated by vDPA ops, read by adminq command wrappers and debugfs, and cleaned during `dev_del`/remove.

State and persistence: All fields are runtime-only software mirrors of firmware/virtio state. Queue indices survive readiness toggles in memory and are synchronized with firmware on VQ reset/init.

Dependencies and integration points: Includes PCI and vDPA headers. Exports `pds_vdpa_release_irqs()` and `pds_vdpa_get_mgmt_info()` across PDS source files.

Risks: The VQ array is fixed at 65, so management info clamps max VQs to this limit. Packed-ring invert index is a protocol convention that must match firmware and `cmds.c`.

Test signals: Compile-time structure users across PDS files and runtime debugfs VQ fields verify layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/vdpa_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/Makefile

Purpose: Builds the SolidRun vDPA module and conditionally includes hardware monitoring support.

Important APIs/types/functions: Kbuild target `obj-$(CONFIG_SNET_VDPA) += snet_vdpa.o` links `snet_main.o` and `snet_ctrl.o`; `snet_hwmon.o` is included when `CONFIG_HWMON` is enabled.

Control flow: Kernel build produces one `snet_vdpa` module from main PCI/vDPA logic, DPU control protocol, and optional hwmon code.

State and persistence: No runtime state.

Dependencies and integration points: Controlled by `CONFIG_SNET_VDPA` and `CONFIG_HWMON`. `snet_main.c` provides fallback warning when hwmon support is requested by device config but not compiled.

Risks: Building without `CONFIG_HWMON` removes `psnet_create_hwmon()`, so the header's conditional declaration and main-file preprocessor block must remain aligned.

Test signals: Build with and without `CONFIG_HWMON` to confirm optional object selection and no unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_ctrl.c

Purpose: Implements the SolidRun DPU control-register protocol for destroying, suspending, resuming devices and reading VQ state.

Important APIs/functions: Public functions are `snet_ctrl_clear()`, `snet_destroy_dev()`, `snet_read_vq_state()`, `snet_suspend_dev()`, and `snet_resume_dev()`. Internal helpers poll opcode/control registers, send old config-v1 messages, send config-v2 no-payload messages, and read chunked payloads from the DPU.

Control flow: For config version 2 or newer, commands serialize under `snet->ctrl_lock`. Send paths wait for an empty control register, write control/opcode under `ctrl_spinlock`, wait for chunk-ready/error, clear chunk-ready, and wait until the DPU clears the opcode. Read paths write expected buffer size and opcode/VQ index, then loop over ready chunks until the requested word count is consumed or the DPU clears in-process. For old config version 1, only the opcode register is used and ACK is opcode clearing.

State and persistence: State is in DPU MMIO control registers and the caller-provided buffers. There is no disk persistence. Locking state is maintained in `struct snet`.

Dependencies and integration points: Uses offsets from `snet->psnet->cfg.ctrl_off`, MMIO accessors from `snet_vdpa.h`, and version negotiation performed by `snet_main.c`.

Risks: Protocol depends on 4-byte aligned buffers, timeouts, and correct chunk-size/error-bit interpretation. Control register writes are serialized with both mutex and spinlock because opcode/control pairs must appear atomically to the DPU. `snet_read_vq_state()` is unsupported on config version 1.

Test signals: Test destroy on reset, suspend/resume netlink migration paths, VQ state read for config v2, old config v1 ACK path, DPU error bits translating to negative errno, and timeout logging for stuck opcode/control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_hwmon.c

Purpose: Registers an optional hwmon device for SolidRun DPU telemetry exposed through BAR registers.

Important APIs/functions: `psnet_create_hwmon()` registers a hwmon device with `devm_hwmon_device_register_with_info()`. `snet_howmon_read()` maps hwmon attributes to BAR offsets for voltage, power, current, and two temperature channels. `snet_hwmon_read_string()` provides labels.

Control flow: If PF config flags request hwmon and `CONFIG_HWMON` is enabled, `snet_main.c` calls `psnet_create_hwmon()` after SR-IOV setup. Sysfs hwmon reads call into the ops table, which uses `psnet_read64()` at `cfg.hwmon_off + offset`.

State and persistence: No persistent state. `psnet->hwmon_name` stores the registered name. Sensor readings are live MMIO values.

Dependencies and integration points: Depends on Linux hwmon framework and `struct psnet` from `snet_vdpa.h`. Uses register offsets agreed with DPU firmware.

Risks: All attributes are exposed read-only as visible, while unsupported type/attribute/channel combinations return `-EOPNOTSUPP`. The function names contain `howmon`/`hwmono` typos but are internally consistent. Units and scaling are assumed to already match hwmon expectations from firmware.

Test signals: With device hwmon flag set, verify `/sys/class/hwmon` entry named `snet_<pci>` and readable labels/values for temp, power, current, and voltage. Exercise unsupported temp channel max and failure to register as non-fatal warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_main.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_main.c

Purpose: Implements the SolidRun PCI vDPA driver: PF config discovery and SR-IOV enablement, VF vDPA device creation, vDPA config ops, IRQ handling, DPU config handoff, reset, suspend/resume, and removal.

Important APIs/functions: `snet_config_ops` implements queue, config, feature, status, reset, suspend, and resume vDPA operations. PF helpers open BARs, detect the config BAR, read `struct snet_cfg`, allocate PF IRQ vectors, and enable SR-IOV. VF helpers find per-VF config, allocate IRQs, map VF BAR, build VQs, reserve IRQ indexes, and register the vDPA device.

Control flow: PF probe enables PCI, maps all non-empty BARs, polls for `SNET_SIGNATURE`, keeps the BAR containing config, reads global and per-device configuration, optionally allocates all MSI-X vectors on the PF, enables configured VFs, and optionally registers hwmon. VF probe derives DPU VF ID as PCI VF index plus one, finds matching config, optionally allocates VF MSI-X vectors, allocates `struct snet`, maps VF BAR, points virtio config into BAR, clears control registers, builds VQs/kick pointers, reserves IRQ indexes, and registers the vDPA device. On `DRIVER_OK`, `snet_set_status()` requests config/VQ IRQs, writes the full host config to the DPU, and waits for DPU ACK by clearing the signature.

State and persistence: PF state lives in `struct psnet` with BARs, negotiated config version, next IRQ index, config, and hwmon name. VF state lives in `struct snet` and `struct snet_vq`: callbacks, queue addresses, state, readiness, IRQs, negotiated features, status, DPU-ready flag, BAR pointers, and config pointer. No disk persistence.

Dependencies and integration points: Uses PCI, SR-IOV, vDPA bus, MSI-X, SolidRun DPU BAR config protocol, `snet_ctrl.c` for migration/control commands, and optional `snet_hwmon.c`. Device IDs match SolidRun vendor/device/subsystem IDs.

Risks: Config parsing trusts DPU-provided counts after size checks; malformed `devices_num` can drive allocations. `snet_write_conf()` casts `vdpa_vq_state` to a 32-bit word for config v2, so only the encoded first word is sent. Status failure paths set `VIRTIO_CONFIG_S_FAILED` in local state but do not necessarily inform DPU. PF IRQ allocation requires exact vector count. Reset destroys DPU device only if previous status had `DRIVER_OK`.

Test signals: PF probe should log config version and enable requested VFs. VF probe should register one vDPA device per configured VF. Test PF-allocated and VF-allocated IRQ modes, DPU config ACK timeout, DRIVER_OK creation, reset destroy, suspend/resume, kick and kick-with-data, config read/write bounds, VQ state for config v1/v2, and remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_vdpa.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_vdpa.h

Purpose: Defines SolidRun vDPA driver shared data structures, logging helpers, config flags, MMIO helpers, and cross-file function prototypes.

Important APIs/types: `struct snet_vq` stores queue callback, state, ring addresses, size, serial ID, readiness, IRQ metadata, and kick pointer. `struct snet` embeds `vdpa_device` and owns config callback, control locks, VQs, negotiated features, status, DPU-ready state, config IRQ, BAR, PCI pointer, parent `psnet`, and device config. `struct snet_dev_cfg`, `struct snet_cfg`, and `struct psnet` model DPU-provided PF/VF configuration and parent state. Inline helpers read/write 32/64-bit values from PF/VF BARs.

Control flow: `snet_main.c` populates these structs from BAR config and vDPA ops. `snet_ctrl.c` consumes locks, offsets, and MMIO helpers for command protocol. `snet_hwmon.c` reads hwmon offsets through `psnet_read64()`.

State and persistence: All structs are runtime kernel state and MMIO views. Persistent behavior is DPU-owned and described by BAR config each probe.

Dependencies and integration points: Includes vDPA and PCI headers. Exposes optional hwmon prototype under `CONFIG_HWMON` and control prototypes used by main ops.

Risks: The packed struct declarations include pointers (`struct snet_dev_cfg **devs`, `void __iomem *virtio_cfg`) that are runtime-only and not directly firmware layout after parsing. IRQ and control locks must be initialized before use. `SNET_CFG_VER()` depends on PF negotiation in `psnet_read_cfg()`.

Test signals: Build all three SolidRun translation units together; runtime tests validate offsets, version checks, config flags, and MMIO read/write helpers under real or emulated BARs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_vdpa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa.c

Purpose: Implements the generic Linux vDPA bus, device/driver registration, management device registry, generic netlink API, device config dumping, stats retrieval, and core locking.

Important APIs/functions: Exports `vdpa_set_status()`, `__vdpa_alloc_device()`, `vdpa_register_device()`, `_vdpa_register_device()`, `vdpa_unregister_device()`, `_vdpa_unregister_device()`, `__vdpa_register_driver()`, `vdpa_unregister_driver()`, `vdpa_mgmtdev_register()`, `vdpa_mgmtdev_unregister()`, `vdpa_get_config()`, and `vdpa_set_config()`. Netlink handlers implement management-device get, device new/delete/get, config get, vendor stats get, and device attr set.

Control flow: Module init registers the `vdpa` bus and generic netlink family. Device allocation validates config ops, IOMMU/use-VA constraints, allocates an IDA index, initializes a device, and sets `cf_lock`. Registration holds global `vdpa_dev_lock`, checks duplicate names, and calls `device_add()`. Management registration adds the management device to `mdev_head`; unregister removes it and deletes child devices through each mdev's `dev_del`. Netlink `DEV_NEW` parses attributes, validates management-device capabilities and feature implications, then calls `mdev->ops->dev_add()` under the global lock.

State and persistence: Global state includes `mdev_head`, `vdpa_dev_lock`, `vdpa_index_ida`, the bus, and netlink family. Per-device state includes `vdev->config`, feature-valid status, map ops, number of VQs, groups/address spaces, and `cf_lock`. No disk persistence.

Dependencies and integration points: Depends on Linux device model, DMA API, generic netlink, virtio IDs/config structures, vDPA/vhost IOTLB headers, and individual hardware/simulator management devices. Hardware drivers call `_vdpa_register_device()` from management callbacks and `vdpa_mgmtdev_register()` during probe.

Risks: Lock ordering matters: global `vdpa_dev_lock` protects mdev and device lists, while `cf_lock` protects device config/status. Managed devices created outside mdev are rejected by user delete/config operations. Config reads before feature negotiation force legacy feature setup with zero. Netlink feature validation for multi-class management devices rejects ambiguous device-feature masks.

Test signals: Exercise netlink `vdpa mgmtdev show`, `vdpa dev add/del/show/config show`, MAC attr set, stats get, duplicate name rejection, unsupported attrs/features, unmanaged device rejection, bus driver probe/remove, and module init netlink registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/Makefile

Purpose: Builds the vDPA simulator core and optional net/block simulator frontends.

Important APIs/types/functions: `obj-$(CONFIG_VDPA_SIM) += vdpa_sim.o`, `obj-$(CONFIG_VDPA_SIM_NET) += vdpa_sim_net.o`, and `obj-$(CONFIG_VDPA_SIM_BLOCK) += vdpa_sim_blk.o`.

Control flow: The core simulator can be built independently, while net and block modules depend on it for `vdpasim_create()` and work scheduling.

State and persistence: Build-only; no runtime state.

Dependencies and integration points: Controlled by Kconfig symbols for simulator core, network, and block devices.

Risks: Net/block simulator objects require exported core symbols; building frontends without core support would fail through Kconfig dependency expectations.

Test signals: Build all three symbols as modules and verify `vdpa_sim_net` and `vdpa_sim_blk` load after or with `vdpa_sim`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.c

Purpose: Provides the shared vDPA simulator core: common vDPA ops, vringh setup, kthread worker scheduling, IOTLB mapping, reset/suspend/resume, config access, feature negotiation, and cleanup.

Important APIs/functions: Exports `vdpasim_create()` and `vdpasim_schedule_work()`. Implements two ops tables: `vdpasim_config_ops` with incremental `dma_map/dma_unmap`, and `vdpasim_batch_config_ops` with batch `set_map`. Important helpers include `vdpasim_queue_ready()`, `vdpasim_do_reset()`, `vdpasim_work_fn()`, `vdpasim_set_group_asid()`, `vdpasim_bind_mm()`, and `vdpasim_free()`.

Control flow: Frontends pass `vdpasim_dev_attr` to `vdpasim_create()`, which validates requested features, allocates a vDPA device with optional VA support, starts a kthread worker, allocates config/VQ/IOTLB state, initializes identity IOTLB mappings, and returns the typed simulator. Queue ready initializes vringh over guest descriptor/avail/used addresses using VA or IOTLB mode and restores last avail index. Kicks schedule frontend work unless suspended. Reset clears VQs, optionally resets maps, marks IOTLB passthrough, stops running, clears status/features, and increments generation.

State and persistence: `struct vdpasim` owns VQs, worker, bound mm, config buffer, per-AS vhost IOTLBs, passthrough flags, status, generation, negotiated features, running and pending-kick flags, and locks. No disk persistence; block frontend may persist only in memory.

Dependencies and integration points: Uses vDPA core, vringh, vhost IOTLB, kthread workers, DMA map ops, virtio endian helpers, and frontend callbacks for config/work/stats/free. Net and block modules register management devices and call `_vdpa_register_device()`.

Risks: `use_va` binds worker to an mm and requires careful mm lifetime handling. `vdpasim_dma_unmap()` checks passthrough before taking `iommu_lock`, unlike map path, which is a concurrency-sensitive area. Batch and incremental mapping modes expose different ops. Simulator only tracks split-ring state in `set_vq_state()`. Pending kicks while suspended are replayed on resume.

Test signals: Create/delete net and block simulated devices, run with `batch_mapping` on/off and `use_va` on/off, map/unmap IOTLB ranges, bind/unbind mm through vhost, reset with map cleanup, suspend/resume with pending kick, and verify generation increments and worker cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.h

Purpose: Defines shared simulator structures, feature constants, frontend attribute contract, exported creation/scheduling APIs, and virtio endian helpers.

Important APIs/types: `VDPASIM_FEATURES` includes any-layout, version 1, and access-platform. `struct vdpasim_virtqueue` wraps `vringh`, in/out kiovs, head, readiness, ring addresses, size, callback, and private data. `struct vdpasim_dev_attr` describes frontend-provided identity, sizes, callbacks, groups, and address spaces. `struct vdpasim` is the full simulator runtime state. Inline conversion helpers map virtio endian to CPU based on legacy/version-1 negotiation.

Control flow: Net/block modules fill `vdpasim_dev_attr`, call `vdpasim_create()`, then rely on common ops invoking their `work_fn`, `get_config`, `set_config`, `get_stats`, and `free`.

State and persistence: Header declares runtime-only fields; no persistent storage.

Dependencies and integration points: Includes IOVA, vringh, vDPA, virtio byteorder, vhost IOTLB, and virtio config headers. It is the contract between simulator core and frontends.

Risks: Frontends must set `alloc_size`, `config_size`, `nvqs`, `ngroups`, and `nas` correctly or core allocation/ops will misbehave. Endian helpers assume no cross-endian support beyond legacy/version-1 choice.

Test signals: Compile net/block against this header; runtime tests verify frontend callbacks and endian conversions in config structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_blk.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_blk.c

Purpose: Implements a virtio-blk vDPA simulator frontend using the simulator core and an in-memory backing buffer.

Important APIs/functions: `vdpasim_blk_dev_add()` creates a block simulator with one VQ/address space/group and registers it. `vdpasim_blk_work()` processes requests. `vdpasim_blk_handle_req()` handles IN, OUT, GET_ID, FLUSH, DISCARD, and WRITE_ZEROES. `vdpasim_blk_get_config()` fills `virtio_blk_config`; `vdpasim_blk_free()` releases private buffers.

Control flow: Module init registers a management device and optional shared backend buffer. `dev_add` builds `vdpasim_dev_attr`, creates the simulator, assigns shared or private storage, and registers the vDPA device. Work loops while the queue is ready and `DRIVER_OK`, handling up to five requests before rescheduling. Each request pulls the virtio block header, validates range and type, copies data between guest IOVs and the backing buffer, writes one-byte status to the final input byte, completes the descriptor, and notifies if needed.

State and persistence: `struct vdpasim_blk` embeds `vdpasim`, has a backing `buffer`, and records whether it uses the module-level `shared_buffer`. Data persists only while the module/device/shared buffer exists in memory.

Dependencies and integration points: Uses vringh IOTLB helpers, virtio block UAPI, simulator endian helpers, vDPA management registration, and `_vdpa_register_device()`.

Risks: Capacity is fixed at `0x40000` sectors, allocating a large memory buffer. Shared backend serializes access with a mutex, but per-device private backends do not share state. Unsupported or malformed requests complete with IOERR/UNSUPP where possible. The code assumes status byte is the last input byte.

Test signals: Add/delete block simulator, run read/write/flush/discard/write-zeroes/get-id IO, test out-of-range and bad flags, shared-backend visibility across devices, memory allocation failure, and used-ring notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_blk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_net.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_net.c

Purpose: Implements a virtio-net vDPA simulator frontend that loops accepted TX packets back to RX, handles basic control VQ MAC changes, and exports vendor queue stats.

Important APIs/functions: `vdpasim_net_dev_add()` creates and registers the net simulator. `vdpasim_net_work()` processes TX/RX/CVQ traffic. `vdpasim_handle_cvq()` handles control VQ descriptors; `vdpasim_handle_ctrl_mac()` supports `VIRTIO_NET_CTRL_MAC_ADDR_SET`. `vdpasim_net_get_stats()` emits RX/TX/CVQ stats via netlink attributes. `vdpasim_net_set_attr()` updates MAC after device creation.

Control flow: Module init registers a management device supporting MAC, MTU, and feature config attrs. `dev_add` creates the simulator, initializes net config from requested attrs or default MTU 1500, initializes stats, allocates a page buffer, and registers the device. Work first handles CVQ, then loops TX descriptors: pull packet into buffer, filter by broadcast/multicast/current MAC, get RX descriptor, push packet, complete TX and RX, notify, and reschedule after a small batch.

State and persistence: `struct vdpasim_net` embeds common simulator state plus TX/RX/CVQ stats and a page buffer. MAC and MTU live in the simulator config buffer. Stats persist for the device lifetime only.

Dependencies and integration points: Uses virtio-net UAPI, ethernet helpers, netlink attributes for vendor stats, u64 stats synchronization, vringh IOTLB, and simulator core.

Risks: Data path is intentionally simple loopback and filters only destination MAC/broadcast/multicast. Control VQ only supports MAC address set. Stats include `tx_drops` output but code never increments it. Packet buffer is limited to one page per processed descriptor.

Test signals: Add device with MAC/MTU/features, run packet loopback for unicast/broadcast/multicast and filtered destinations, change MAC via CVQ and netlink attr set, query vendor stats for queues 0/1/2, test invalid queue index, and verify behavior when RX queue lacks descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/vdpa_sim_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/Makefile

Purpose: Builds the VDUSE userspace vDPA module and includes the IOVA-domain implementation.

Important APIs/types/functions: `vduse-y := vduse_dev.o iova_domain.o` and `obj-$(CONFIG_VDPA_USER) += vduse.o`.

Control flow: Kernel build links the userspace-device frontend and MMU/software-IOTLB domain into the `vduse` module when `CONFIG_VDPA_USER` is enabled.

State and persistence: Build-only file; no runtime state.

Dependencies and integration points: `vduse_dev.o` depends on functions exported within `iova_domain.o` for DMA/IOTLB behavior.

Risks: Removing `iova_domain.o` would break VDUSE DMA mapping and mmap support.

Test signals: Build `CONFIG_VDPA_USER=m/y` and ensure the final `vduse` module contains IOVA-domain symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.c

Purpose: Implements the VDUSE MMU-based software IOTLB and bounce-buffer domain used to map kernel DMA/I/O virtual addresses to userspace-visible memory.

Important APIs/functions: Public functions include map set/clear, sync for device/CPU, streaming map/unmap page, coherent alloc/free, bounce map reset, user bounce page add/remove, domain create/destroy, and global init/exit. Internal helpers manage vhost IOTLB ranges with file references, allocate/free IOVA ranges, map/unmap bounce pages, copy bounce data, fault mmap pages, and release all resources.

Control flow: `vduse_domain_create()` allocates the domain, vhost IOTLB, bounce map array, anon inode file, locks, and two IOVA domains: stream IOVAs below the bounce window and coherent IOVAs above it. Streaming `map_page` allocates an IOVA from the bounce window, ensures the bounce IOTLB mapping exists, records original physical addresses per 4 KiB bounce segment, and optionally copies CPU data into bounce pages. `unmap_page` optionally copies back and frees the IOVA. Coherent alloc maps `virt_to_phys(orig)` into the IOTLB with the domain file as mmap backing. `mmap` faults return either bounce pages or coherent pages.

State and persistence: `struct vduse_iova_domain` owns stream and coherent `iova_domain`s, `bounce_maps`, bounce size, IOVA limit, vhost IOTLB, anon file, user-bounce mode, and locks. IOTLB entries hold `vdpa_map_file` references. All state is runtime-only and released on anon file close.

Dependencies and integration points: Uses vhost IOTLB, Linux IOVA allocator/cache, anon inode mmap, page copy helpers, DMA directions/attrs, and vDPA map-file context. Called by VDUSE device code for DMA mapping and userspace mmap of DMA windows.

Risks: Locking is subtle: `iotlb_lock` protects IOTLB mutations and `bounce_lock` protects bounce page/user page switching. Release calls `vduse_domain_remove_user_bounce_pages()` and kernel bounce free while holding `iotlb_lock`, while those functions take `bounce_lock`, so callers must avoid inverse ordering. Bounce segments are 4 KiB even on larger PAGE_SIZE, requiring shared page handling. User bounce pages require full mapping, not partial. Incorrect sync direction loses data.

Test signals: Create/destroy domains, map/unmap streaming pages with all DMA directions and skip-sync attrs, add/remove user bounce pages with data preservation, mmap bounce and coherent ranges, set/clear external IOTLB maps with file reference accounting, fault invalid pages to SIGBUS, and run with PAGE_SIZE larger than 4 KiB if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.h

Purpose: Declares VDUSE IOVA-domain data structures, constants, and public mapping/sync/domain lifecycle APIs.

Important APIs/types: Constants define IOVA start PFN and 4 KiB bounce-map granularity. `struct vduse_bounce_map` stores kernel/user bounce pages and original physical address. `struct vduse_iova_domain` stores stream/consistent IOVA allocators, bounce map array, size/limit, bounce-map state, vhost IOTLB, locks, anon file, and user-bounce flag. Public prototypes cover map set/clear, DMA sync, map/unmap page, coherent alloc/free, bounce map reset, user bounce page add/remove, destroy/create, and global init/exit.

Control flow: VDUSE device code includes this header to create a domain, expose mmap through the domain's anon file, perform DMA operations, and tear the domain down.

State and persistence: Header describes runtime-only memory translation state. There is no disk persistence.

Dependencies and integration points: Includes IOVA, DMA mapping, and vhost IOTLB headers. The implementation uses `vdpa_map_file` contexts through vhost IOTLB opaque pointers.

Risks: Callers must respect IOVA limits, bounce-size alignment, and sync directions. User bounce pages must cover the entire bounce window. The domain object is ultimately released by `fput(domain->file)`, so external references must not outlive destroy/release.

Test signals: Compile integration with VDUSE device code; runtime tests should cover all public APIs declared here and validate resource release through `vduse_domain_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.h -->
