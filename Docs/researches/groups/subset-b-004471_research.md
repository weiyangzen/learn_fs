# subset-b-004471 research

Grouped research for Intel `ice` driver files under `sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.c

## Purpose
Implements devlink firmware flashing for Intel `ice` devices using Linux PLDM firmware parsing and device AdminQ NVM commands. It validates PLDM records against the PCI device, sends package/component metadata to firmware, erases inactive NVM banks, writes component data in AdminQ-sized blocks, activates updated banks, and reports the reset action needed to complete activation.

## Important APIs, types, and functions
- `struct ice_fwu_priv` embeds `struct pldmfw` and carries `ice_pf`, `netlink_ext_ack`, activation flags, required reset level, and EMP reset availability across PLDM callbacks.
- `ice_devlink_flash_update()` is the devlink entry point. It validates overwrite policy, unified-update support, optional single-component `fw.mgmt` mode, cancels prior pending updates, acquires the NVM write lock, and calls `pldmfw_flash_image()`.
- `ice_send_package_data()` forwards matching PLDM record package data via `ice_nvm_set_pkg_data()`.
- `ice_send_component_table()` builds `struct ice_aqc_nvm_comp_tbl`, sends it with `ice_nvm_pass_component_tbl()`, and delegates firmware response interpretation to `ice_check_component_response()`.
- `ice_flash_component()` maps PLDM component IDs to NVM modules and devlink component names: `NVM_COMP_ID_OROM` -> `fw.undi`, `NVM_COMP_ID_NVM` -> `fw.mgmt`, `NVM_COMP_ID_NETLIST` -> `fw.netlist`.
- `ice_erase_nvm_module()` and `ice_write_nvm_module()` perform erase/write sequencing with devlink progress notifications.
- `ice_write_one_nvm_block()` is exported for one-block write plus firmware completion validation.
- `ice_finalize_update()` calls `ice_switch_flash_banks()` and emits the user-facing activation instruction.
- `ice_get_pending_updates()` refreshes device capabilities from firmware and builds a pending-update bitmap.

## Control flow
`ice_devlink_flash_update()` rejects unsupported overwrite masks, rejects devices without unified update outside recovery mode, initializes PLDM ops based on MAC type, cancels any previous pending update, and holds the NVM resource while `pldmfw_flash_image()` invokes the callback sequence. The callback sequence sends package data, sends component tables, erases inactive banks, writes data in `ICE_AQ_MAX_BUF_LEN` chunks, waits for AdminQ completion events, then activates selected banks. Completion paths map firmware and PLDM failures to devlink status and netlink extended ACK messages.

## State and persistence behavior
Persistent state is in device flash banks, not host files. `activate_flags` accumulates selected components and preservation mode until activation. `reset_level` is captured from the final NVM-bank write when firmware supports reset avoidance; otherwise it defaults to full power cycle. `pf->fw_emp_reset_disabled` records whether EMP reset activation is unavailable after bank switching or reset-cancellation uncertainty. Pending-update state is read from fresh firmware capabilities rather than cached `hw->dev_caps`.

## Dependencies and integration points
Depends on `linux/pldmfw.h`, devlink flash-update callbacks, AdminQ NVM helpers (`ice_aq_update_nvm`, `ice_aq_erase_nvm`, `ice_nvm_write_activate`, `ice_acquire_nvm`), PCI IDs, recovery-mode checks, and firmware capability discovery. It integrates with `devlink/devlink.c` through `ice_devlink_flash_update()` and pending-update reporting.

## Risks
The code depends on exact firmware completion events; mismatched module or offset is treated as corruption and fails the update. NVM resource ownership is critical: most helpers assume the caller already acquired the flash lock. Timeout tuning is operationally important because erase can legitimately take minutes and writes can exceed one second. Component response handling must stay aligned with firmware codes or users will get incorrect update rejection reasons.

## Test signals
Useful validation includes devlink flash update success/failure on matching and non-matching PLDM images, overwrite-mask rejection, single `fw.mgmt` component mode, pending-update cancellation, recovery-mode partial-check behavior, AdminQ timeout/error injection, and activation messages for EMP, PCIe reset, and power-cycle paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.h

## Purpose
Declares the public firmware-update entry points used by the rest of the `ice` driver.

## Important APIs, types, and functions
- `ice_devlink_flash_update()` exposes the devlink flash-update implementation.
- `ice_get_pending_updates()` exposes pending NVM/Option ROM/netlist activation checks.
- `ice_write_one_nvm_block()` exposes the low-level NVM block write plus completion wait helper.

## Control flow
This header has no executable control flow. It defines the compile-time contract between devlink integration, update support code, and any callers that need direct block-write or pending-update behavior.

## State and persistence behavior
No state is stored here. The declarations operate on `struct ice_pf`, `struct devlink`, NVM modules, and netlink extack objects owned elsewhere.

## Dependencies and integration points
The prototypes require driver-visible definitions for `struct ice_pf`, devlink flash parameters, `netlink_ext_ack`, and fixed-width integer types. It is included by the implementation and by driver code that wires devlink operations.

## Risks
Signature changes here affect devlink registration and low-level NVM callers. Because `ice_write_one_nvm_block()` assumes NVM resource ownership, any new caller must follow the locking contract documented in the `.c` file.

## Test signals
Build coverage should catch signature drift. Runtime signals come from devlink flash update and pending-update query paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.c

## Purpose
Provides Linux GNSS subsystem support for the internal u-blox GNSS receiver found on supported E810T hardware. It exposes a `gnss_device`, polls the receiver through AdminQ I2C transactions, and forwards raw UBX data between userspace and hardware.

## Important APIs, types, and functions
- `ice_gnss_init()` allocates `struct gnss_serial`, starts a kthread worker, registers the GNSS device, and sets `ICE_FLAG_GNSS`.
- `ice_gnss_exit()` deregisters the GNSS device, clears the flag, cancels delayed work, destroys the worker, and frees state.
- `ice_gnss_is_module_present()` checks ownership of the source timer, netlist GPS support, and a PCA9575 presence bit.
- `ice_gnss_read()` is delayed work that reads the u-blox available-data length register, reads raw bytes in AdminQ I2C chunks, inserts them through `gnss_insert_raw()`, and requeues itself.
- `ice_gnss_write()` validates userspace writes and calls `ice_gnss_do_write()`.
- `ice_gnss_do_write()` chunks UBX writes around the hardware constraint that one-byte writes are not possible.
- `ice_gnss_open()` and `ice_gnss_close()` start and stop polling for a consumer.

## Control flow
Initialization creates per-PF GNSS state and registers GNSS operations. On open, polling begins immediately. Each read work item verifies the PF and feature flag, reads two big-endian length bytes from the u-blox register, skips empty reads, allocates a page buffer, reads up to a page of data using `ICE_MAX_I2C_DATA_SIZE` chunks, sends the data to the GNSS core, then requeues at either the fast poll interval or the normal message interval. Close and exit synchronously cancel the delayed work.

## State and persistence behavior
State lives in `pf->gnss_serial`, `pf->gnss_dev`, and `ICE_FLAG_GNSS`. The worker repeatedly requeues while enabled. No persistent host storage is used; hardware presence and data availability are polled from the adapter and receiver.

## Dependencies and integration points
Depends on the Linux GNSS subsystem, kthread delayed work, AdminQ I2C helpers (`ice_aq_read_i2c`, `ice_aq_write_i2c`), link topology addressing, PCA9575 GPIO access, timer ownership capability, and netlist GPS detection. It is invoked during probe/rebuild paths when `ice_gnss_is_module_present()` allows GNSS support.

## Risks
Polling and teardown races are mitigated by flag checks and synchronous cancellation, but any future caller must preserve that lifecycle. I2C write chunking is hardware-specific and easy to break; one-byte writes are explicitly invalid. The read path caps data to one page, so unexpectedly large receiver buffers are drained over multiple polls. Memory allocation failure causes a retry, not permanent disable.

## Test signals
Test with `CONFIG_GNSS` enabled and disabled, hardware-present and absent detection, userspace open/close loops, invalid write sizes (`0`, `1`, and above `ICE_GNSS_TTY_WRITE_BUF`), forced I2C errors, and raw UBX data flow through `/dev/gnss*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.h

## Purpose
Defines constants, state, and conditional declarations for `ice` GNSS support.

## Important APIs, types, and functions
- `struct gnss_serial` stores the PF backpointer, kthread worker, and delayed read work.
- Constants define the E810T GNSS I2C bus, u-blox address/registers, polling intervals, maximum write size, and AdminQ I2C chunk limits.
- `ice_gnss_init()`, `ice_gnss_exit()`, and `ice_gnss_is_module_present()` are declared when `CONFIG_GNSS` is enabled and stubbed otherwise.

## Control flow
The header has no runtime flow, but its `IS_ENABLED(CONFIG_GNSS)` guard compiles GNSS support into either real calls or no-op/false stubs.

## State and persistence behavior
The only defined state is the in-memory `gnss_serial` object, which is owned through `pf->gnss_serial` by the implementation.

## Dependencies and integration points
Requires `struct ice_pf`, `struct ice_hw`, kthread worker types, and AdminQ I2C field macros from surrounding driver headers. It is consumed by probe and teardown code to avoid scattering `CONFIG_GNSS` conditionals.

## Risks
Constants encode u-blox ZED-F9T behavior and AdminQ limits. Changing them without matching hardware documentation can break data transfer or polling rate. Stubs must remain behaviorally safe for callers that do not check `CONFIG_GNSS`.

## Test signals
Build both `CONFIG_GNSS=y/m` and disabled configurations. Runtime coverage should confirm the public functions are no-ops when disabled and fully register/deregister GNSS when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_gnss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hw_autogen.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hw_autogen.h

## Purpose
Machine-generated register map header for the `ice` hardware family. It provides register addresses, indexed register address formulas, bit positions, and bit masks used by AdminQ, mailbox, interrupt, queue, reset, flow director, statistics, PTP/timestamping, power-management, and E830-specific code.

## Important APIs, types, and functions
This header defines macros rather than functions. Major groups include:
- Firmware/AdminQ and mailbox rings: `PF_FW_*`, `PF_MBX_*`, `PF_SB_*`, and `VF_MBX_*`.
- DCB and parser/flex descriptor registers: `PRTDCB_*`, `GLFLXP_*`, `QRXFLXP_CNTXT`.
- Reset and function control: `GLGEN_*`, `PFGEN_*`, `VFGEN_*`, `VPGEN_*`.
- Interrupt programming: `GLINT_*`, `PFINT_*`, `QINT_*`, `VPINT_*`, `VFINT_DYN_CTLN`.
- Queue allocation and queue control: `PFLAN_TX_QALLOC`, `QRX_*`, `VPLAN_*`, `GLCOMM_QTX_*`.
- Malicious-driver detection: `GL_MDET_*`, `PF_MDET_*`, `VP_MDET_*`.
- NVM management: `GLNVM_*`, `GL_MNG_FWSM`.
- Flow director and hash/filter registers: `GLQF_*`, `PFQF_*`, `VSIQF_*`.
- Port/VSI/VF statistics: `GLPRT_*`, `GLV_*`, `GLSTAT_*`.
- PTP and timestamping: `GLTSYN_*`, `E830_GLTSYN_*`, `E830_PRTTSYN_*`, semaphores `PFTSYN_SEM` and `E830_PFPTM_SEM`.
- Power management and wake events: `PFPM_*`.

## Control flow
There is no executable control flow. The macros are expanded by low-level register accessors such as `rd32()` and `wr32()` throughout the driver. Indexed macros compute MMIO offsets from queue, vector, VF, VSI, profile, or timer indices.

## State and persistence behavior
No in-memory state is stored here. The definitions describe device MMIO state that persists according to hardware reset domains. Many masks correspond to hardware latches or enable bits that must be cleared or programmed by other modules.

## Dependencies and integration points
Depends on common bit helpers such as `BIT`, `GENMASK`, and `ICE_M`. It is included through the broader hardware headers and used by `ice_main.c`, `ice_txrx.c`, `ice_sriov.c`, `ice_ptp.c`, `ice_ptp_hw.c`, `ice_ethtool.c`, and queue/interrupt paths. The searched references show `GLINT_*` used for interrupt arming and vector-to-function mapping, `PF_FW_ATQLEN_*` used for AdminQ error handling, and `GLTSYN_*` used extensively by PTP.

## Risks
Because the file is machine generated, manual edits are high risk and likely to diverge from hardware specifications. Incorrect offsets or masks can cause silent hardware misconfiguration. Indexed macros need caller-side range discipline; only a few include explicit max-index macros. Hardware-generation differences are encoded in `E800_` and `E830_` variants, so callers must select the correct macro for `hw->mac_type`.

## Test signals
Build coverage catches missing macro names but not semantic offset errors. Functional signals include AdminQ health, interrupt delivery, queue enable/disable, SR-IOV vector mapping, PTP clock behavior, flow director configuration, statistics reads, and ethtool register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hw_autogen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.c

## Purpose
Registers an `hwmon` temperature sensor for supported Intel `ice` devices and reads internal chip temperature thresholds through firmware AdminQ.

## Important APIs, types, and functions
- `ice_hwmon_init()` registers an `hwmon` device named `ice` when internal readings are supported.
- `ice_hwmon_exit()` unregisters `pf->hwmon_dev`.
- `ice_hwmon_read()` handles `hwmon_temp_input`, `hwmon_temp_max`, `hwmon_temp_crit`, and `hwmon_temp_emergency` by calling `ice_aq_get_sensor_reading()`.
- `ice_hwmon_is_visible()` exposes those attributes as read-only.
- `ice_is_internal_reading_supported()` gates registration to PF 0 and capability bit `ICE_SENSOR_SUPPORT_E810_INT_TEMP_BIT`.

## Control flow
Initialization checks support and registers with `hwmon_device_register_with_info()`. Reads are demand-driven by the hwmon core; each read fetches a fresh sensor response from firmware and converts register degrees to millidegrees Celsius using `TEMP_FROM_REG`. Exit unregisters only if registration succeeded.

## State and persistence behavior
The only persistent driver state is `pf->hwmon_dev`. Sensor values are not cached; they are retrieved from firmware per read. No host files are written except sysfs nodes managed by the hwmon core.

## Dependencies and integration points
Depends on `linux/hwmon.h`, `ice_aq_get_sensor_reading()`, device capabilities, and `dev_get_drvdata()` returning `struct ice_pf`. Called from PF initialization and teardown paths when `CONFIG_ICE_HWMON` is enabled.

## Risks
Firmware older than the documented support level may not provide readings, so capability gating is essential. The implementation currently leaves `pf->hwmon_dev` unchanged after unregister; callers must not double-unregister without guarding. Read failures are ratelimited warnings but propagate the AdminQ error to sysfs.

## Test signals
Build with `CONFIG_ICE_HWMON` enabled and disabled. Runtime signals include creation of `temp*_input`, `temp*_max`, `temp*_crit`, and `temp*_emergency` sysfs attributes only on PF 0 with the capability bit set, successful millidegree values, and ratelimited warnings under injected AdminQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.h

## Purpose
Provides the conditional public interface for `ice` hwmon support.

## Important APIs, types, and functions
- `ice_hwmon_init(struct ice_pf *pf)` and `ice_hwmon_exit(struct ice_pf *pf)` are real declarations under `CONFIG_ICE_HWMON`.
- The same names are inline no-ops when hwmon support is not configured.

## Control flow
No runtime control flow exists in the header. Compile-time configuration selects real hooks or stubs.

## State and persistence behavior
No state is stored here; `pf->hwmon_dev` is managed by the implementation when enabled.

## Dependencies and integration points
Used by PF initialization/teardown code so callers can invoke hwmon hooks unconditionally.

## Risks
The stubs should remain side-effect free. Signature changes must be coordinated with probe/remove call sites and the implementation.

## Test signals
Build coverage for both `CONFIG_ICE_HWMON` states verifies the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc.c

## Purpose
Implements inter-driver communication between the `ice` LAN driver and an auxiliary RDMA driver. It allocates and registers auxiliary devices, exports RDMA resource-management callbacks, forwards events to the auxiliary driver, and manages RDMA device metadata for RoCE.

## Important APIs, types, and functions
- `ice_init_rdma()` allocates `iidc_rdma_core_dev_info`, private RDMA info, a global auxiliary ID from `ice_aux_id`, and fills PCI/hardware identity fields.
- `ice_rdma_finalize_setup()` populates VSI-dependent netdev/vport/QoS fields after VSI and DCB rebuild, then plugs the auxiliary device.
- `ice_plug_aux_dev()` creates an `iidc_rdma_core_auxiliary_dev`, initializes and adds `auxiliary_device`, records it under `pf->adev_mutex`, and sets `ICE_FLAG_AUX_DEV_CREATED`.
- `ice_unplug_aux_dev()` clears the created flag, detaches `cdev->adev`, and unregisters/uninitializes the auxiliary device.
- `ice_send_event_to_aux()` locks the auxiliary device and calls the RDMA driver's `event_handler`.
- Exported RDMA operations include `ice_add_rdma_qset()`, `ice_del_rdma_qset()`, `ice_rdma_request_reset()`, `ice_rdma_update_vsi_filter()`, `ice_alloc_rdma_qvector()`, and `ice_free_rdma_qvector()`.
- `ice_deinit_rdma()` releases xarray ID and RDMA metadata allocations.

## Control flow
Initialization is split: `ice_init_rdma()` prepares generic RDMA state early, while `ice_rdma_finalize_setup()` waits until the main VSI and DCB QoS state are valid before exposing an auxiliary device. The RDMA auxiliary driver calls exported symbols to allocate queue sets, configure filters, request resets, and allocate MSI-X vectors. Events flow from LAN to RDMA through `ice_send_event_to_aux()` under `pf->adev_mutex` and `device_lock()`.

## State and persistence behavior
State is in `pf->cdev_info`, `pf->aux_idx`, `pf->adev_mutex`, `ICE_FLAG_AUX_DEV_CREATED`, and the static xarray allocator `ice_aux_id`. RDMA qsets alter firmware scheduler/resource state through AdminQ. No host persistence is used.

## Dependencies and integration points
Depends on Linux auxiliary bus, Intel IIDC RDMA headers, xarray allocation, DCB QoS setup, VSI lookup/configuration, RDMA filter AdminQ commands, reset scheduling, and the shared IRQ allocator in `ice_irq.c`. The module exports symbols to the RDMA driver.

## Risks
Lifecycle ordering is critical: plugging before VSI/QoS readiness would expose incomplete data, while failing to unplug before freeing `cdev_info` would leave dangling auxiliary state. `ice_send_event_to_aux()` requires task context and uses device locking to avoid driver detach races. RDMA qset operations assume a valid main VSI and enabled RDMA capability.

## Test signals
Probe and remove with RDMA-capable and non-capable devices, auxiliary bus bind/unbind, RDMA qset add/delete, RDMA reset requests, VSI filter toggles, MSI-X allocation/free through RDMA, DCB rebuild followed by finalize setup, and race tests around unplug while events are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc_int.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc_int.h

## Purpose
Defines the internal event-forwarding interface from `ice` to the RDMA auxiliary driver.

## Important APIs, types, and functions
- Includes `linux/net/intel/iidc_rdma.h` and `iidc_rdma_ice.h` for event and device types.
- Forward declares `struct ice_pf`.
- Declares `ice_send_event_to_aux(struct ice_pf *pf, struct iidc_rdma_event *event)`.

## Control flow
No executable flow. It exposes one internal call used by other `ice` modules when they need to notify the RDMA auxiliary driver.

## State and persistence behavior
No state is stored here. State is handled by `pf->cdev_info` and auxiliary-device lifecycle code in `ice_idc.c`.

## Dependencies and integration points
Ties the LAN driver to the Intel IIDC RDMA interface without exposing the full implementation. This keeps event senders independent of auxiliary bus details.

## Risks
Any event ABI changes in IIDC headers can affect all senders. Callers must respect the implementation requirement that events be sent from task context.

## Test signals
Build coverage for IIDC header compatibility and runtime RDMA event delivery during link/reset/VSI state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_idc_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.c

## Purpose
Centralizes MSI-X interrupt vector allocation for the `ice` PF and reserves a virtual vector range for SR-IOV VFs. It supports both static vectors allocated by `pci_alloc_irq_vectors()` and dynamic MSI-X allocation when the PCI core supports it.

## Important APIs, types, and functions
- `ice_init_interrupt_scheme()` determines min/max MSI-X counts, allocates vectors, initializes the xarray tracker, and initializes the VF bitmap tracker.
- `ice_clear_interrupt_scheme()` frees PCI vectors and destroys both trackers.
- `ice_alloc_irq()` reserves an `ice_irq_entry` and returns an `msi_map`, dynamically allocating with `pci_msix_alloc_irq_at()` for dynamic entries when possible.
- `ice_free_irq()` frees dynamic PCI MSI-X state if needed and removes the tracker entry.
- `ice_virt_get_irqs()` allocates a contiguous bitmap range for VF vector indices.
- `ice_virt_free_irqs()` clears a VF bitmap range.
- Internal helpers initialize/deinitialize trackers and allocate/free xarray entries.

## Control flow
Initialization computes the default desired MSI-X amount from LAN/OICR, RSS queues, Flow Director, and RDMA needs. If dynamic MSI-X is available, it initially allocates only the minimum static vectors; otherwise it allocates the full maximum. Runtime callers request vectors through `ice_alloc_irq()`, which first reserves the lowest valid tracker slot and then either maps an existing static vector or allocates a dynamic vector at that index. VF allocation is separate: it assigns indexes from a bitmap offset by `virt_irq_tracker.base`.

## State and persistence behavior
State lives in `pf->msix`, `pf->irq_tracker.entries`, and `pf->virt_irq_tracker.bm/base/num_entries`. This is in-memory state tied to PCI interrupt vectors; it is torn down by `ice_clear_interrupt_scheme()`.

## Dependencies and integration points
Depends on PCI MSI-X APIs, xarray, bitmap allocation, RSS queue defaults, Flow Director flag state, RDMA enablement, and `ice_pf` MSI-X capability data. Integrated callers include OICR and timestamp interrupt setup in `ice_main.c`, RDMA qvector allocation in `ice_idc.c`, and SR-IOV vector mapping code.

## Risks
Off-by-one errors in `num_static - 1` and dynamic/static boundaries would leak or misclassify vectors. `ice_free_irq()` logs and returns on unknown indexes, so double-free bugs are visible but not fatal. VF bitmap APIs assume callers pass indexes originally returned by `ice_virt_get_irqs()`.

## Test signals
Exercise devices with and without dynamic MSI-X support, low-vector configurations, RDMA enabled/disabled, Flow Director enabled/disabled, repeated vector alloc/free, allocation exhaustion, SR-IOV VF range allocation/free, and teardown after partial initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.h

## Purpose
Defines interrupt tracking data structures and declares the PF/VF interrupt allocation interface.

## Important APIs, types, and functions
- `struct ice_irq_entry` records vector index and whether the entry was dynamically allocated.
- `struct ice_irq_tracker` owns the xarray of allocated PF vectors plus total/static counts.
- `struct ice_virt_irq_tracker` owns the VF bitmap, number of entries, and PF-relative base index.
- Declares `ice_init_interrupt_scheme()`, `ice_clear_interrupt_scheme()`, `ice_alloc_irq()`, `ice_free_irq()`, `ice_virt_get_irqs()`, and `ice_virt_free_irqs()`.

## Control flow
No executable flow. The structures define how `ice_irq.c` tracks static, dynamic, and VF-reserved MSI-X indices.

## State and persistence behavior
The structs are embedded in `struct ice_pf` and represent in-memory PCI interrupt allocation state. No persistent storage is involved.

## Dependencies and integration points
Requires `struct ice_pf`, `struct msi_map`, xarray, and bitmap users in implementation. It is included by code that allocates vectors for LAN, RDMA, timestamping, and virtualization.

## Risks
The header-level contract exposes `dyn_only`/dynamic behavior through a boolean; callers must understand whether static fallback is allowed. Layout changes affect `struct ice_pf` users.

## Test signals
Compile and runtime tests around vector allocation, dynamic-only RDMA vectors, and SR-IOV vector bitmap allocation cover this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.c

## Purpose
Implements link aggregation support for `ice`, especially SR-IOV VF behavior in Linux bonding configurations. It watches netdevice bond events, validates whether a bond is compatible with SR-IOV LAG, programs switch recipes/filters, shares switch IDs, moves VF scheduling nodes/queues between ports for active-backup and active-active modes, and rebuilds LAG resources after resets.

## Important APIs, types, and functions
- Public entry points: `ice_init_lag()`, `ice_deinit_lag()`, `ice_lag_rebuild()`, `ice_lag_is_switchdev_running()`, `ice_lag_move_vf_nodes_cfg()`, `ice_lag_prepare_vf_reset()`, `ice_lag_complete_vf_reset()`, and `ice_lag_aa_failover()`.
- Netdevice event path: `ice_lag_event_handler()` snapshots events and bond member lists, queues work on `ice_lag_wq`; `ice_lag_process_event()` handles `NETDEV_CHANGEUPPER`, `NETDEV_BONDING_INFO`, and `NETDEV_UNREGISTER` under `pf->lag_mutex`.
- Role/state helpers: `ice_lag_set_primary()`, `ice_lag_set_bkup()`, `ice_lag_find_primary()`, `ice_lag_link()`, `ice_lag_link_unlink()`, `ice_lag_info_event()`.
- Compatibility: `ice_lag_chk_comp()` rejects unsupported bond modes/features, non-ice members, more than two members, different PCI slot/bus, DCB mismatches, missing switchdev, and firmware LLDP peer conflicts.
- Hardware programming: `ice_create_lag_recipe()`, `ice_lag_cfg_fltr()`, `ice_lag_cfg_dflt_fltr()`, `ice_lag_cfg_drop_fltr()`, `ice_lag_cfg_lp_fltr()`, `ice_lag_primary_swid()`, `ice_lag_set_swid()`, prune-list add/delete helpers.
- VF movement: `ice_lag_move_vf_node_tc()`, `ice_lag_move_vf_nodes()`, `ice_lag_reclaim_vf_tc()`, `ice_lag_aa_move_vf_qs()`, sync/rebuild variants, and reset prepare/complete helpers.

## Control flow
Initialization checks device/package capabilities, allocates `struct ice_lag`, registers a global netdevice notifier, creates three recipes, and maps them to default profiles. Netdevice notifier callbacks filter for ice bonding events, copy notifier data and bond-member lists into a work item, then defer processing. Work processing updates disabled-bond state, validates compatibility, links/unlinks bond state, configures RDMA capability, programs filters, moves VF queues/nodes on active-port changes, and unwinds state on unregister.

Active-backup mode tracks `active_port`; when the active slave changes, VF scheduler nodes and queues move from the previous lport to the new lport, and eswitch representors are retargeted. Active-active mode tracks `port_bitmap`, primary/secondary lports, queue home (`q_home`), and placeholder secondary VF VSIs (`sec_vf`) so queues can be split or failed over between ports. Reset helpers temporarily move nodes home, then restore them after reset under the LAG mutex.

## State and persistence behavior
Driver state lives in `pf->lag`, role flags, bond mode, upper netdev, notifier block, active lport, bond lports, `port_bitmap`, recipe IDs, rule IDs, `q_home`, secondary placeholder VSIs, and bond SWID. Hardware state includes switch recipes, SWID sharing, prune lists, default/drop/control filters, queue-to-port configuration, and scheduler-tree parentage. No host files are persisted.

## Dependencies and integration points
Depends on Linux bonding/netdevice notifier APIs, workqueues, RCU bond member iteration, switchdev/eswitch representors, DCB config, RDMA capability flags, SR-IOV VF/VSI structures, scheduler tree APIs, AdminQ switch-rule and queue-config commands, recipe allocation, and hardware resource sharing. It is invoked by PF init/remove, reset rebuild paths, VF reset flows, and switchdev/SR-IOV control paths.

## Risks
This file has high concurrency and hardware-state risk. Event data is intentionally copied into work items to leave notifier context, but bond topology can change before work runs. Correct locking with `lag_mutex`, RCU list capture, and rebuild/reset pairing is essential. Queue/scheduler movement updates both firmware and software scheduler structures; partial failures can leave mismatches. Active-active placeholder VSI lifetime and `q_home` tracking are fragile. Compatibility checks intentionally disable SR-IOV LAG for unsupported topologies to avoid corrupting VF traffic.

## Test signals
Important tests include two-port same-device bonds, non-ice member rejection, more-than-two member rejection, DCB mismatch rejection, active-backup failover and failback with VFs, active-active link up/down with queue split/failover, switchdev representor Tx after failover, PF reset while bonded, VF reset while bonded, unregister/unlink cleanup, RDMA capability clear/restore on bond join/leave, and recipe/filter cleanup on driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.h

## Purpose
Defines LAG roles, constants, state structures, work-item layout, and public LAG entry points for the `ice` driver.

## Important APIs, types, and functions
- `enum ice_lag_role` models none, primary, backup, and unset roles.
- Constants define invalid lport, primary/secondary indexes and masks, reset retry count, default switch profile, metadata protocol ID, and lport extract offset.
- `struct ice_lag` stores PF/netdev linkage, upper bond netdev, notifier, bond mode, SWID, active lport, state flags, active-port bitmap, primary/secondary lports, queue-home matrix, secondary placeholder VF VSIs, recipe/rule IDs, and role.
- `struct ice_lag_work` stores deferred notifier work, a copied netdev list, event type, event netdev, and copied notifier payload.
- Declares initialization, teardown, rebuild, switchdev query, VF movement, reset prepare/complete, and active-active failover functions.

## Control flow
No executable flow is present. The struct layout directly drives the event work and queue-migration logic in `ice_lag.c`.

## State and persistence behavior
All state is per-PF runtime state. Hardware-persistent effects are managed by the implementation through recipe/rule/SWID IDs stored in `struct ice_lag`.

## Dependencies and integration points
Includes `linux/netdevice.h` and forward-declares `ice_pf` and `ice_vf`. The header is shared with PF lifecycle, reset, VF, and switchdev paths that need LAG state or helper calls.

## Risks
Bitfield state must remain large enough for encoded values such as `port_bitmap`. Arrays are sized by SR-IOV limits; changes to VF or queue maxima affect memory footprint. Public helper comments in the implementation impose locking requirements that callers must follow.

## Test signals
Build coverage plus runtime bond join/leave, VF reset, PF reset, and active-active failover exercise the exported interface and state layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lan_tx_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lan_tx_rx.h

## Purpose
Defines LAN Tx/Rx descriptor formats, filter-programming descriptor fields, queue context structures, timestamp descriptor structures, and bit masks used by the `ice` datapath and queue setup code.

## Important APIs, types, and functions
- Rx descriptors: `union ice_32byte_rx_desc`, `union ice_32b_rx_flex_desc`, `struct ice_32b_rx_flex_desc_nic`, and `struct ice_32b_rx_flex_desc_nic_2`.
- Rx descriptor metadata enums: `enum ice_rxdid`, `enum ice_flex_mdid_pkt_flags`, `enum ice_flex_rx_mdid`, `enum ice_flg64_bits`, and status/error bit enums.
- Flow Director/filter programming: `struct ice_fltr_desc` and `ICE_FXD_FLTR_*` masks for queue index, completion reporting, stats, destination queue, drop, flex metadata, command, VSI, FDID, and writeback status.
- Rx queue context: `struct ice_rlan_ctx` plus header split enums and field shift constants.
- Tx descriptors: `struct ice_tx_desc`, `enum ice_tx_desc_dtype_value`, `enum ice_tx_desc_cmd_bits`, length/offset masks, and maximum encoded header lengths.
- Tx context descriptor: `struct ice_tx_ctx_desc`, generic checksum descriptor masks, context command bits, and tunnel/offload encoding.
- Tx queue context: `struct ice_tlan_ctx` with base, port/PF/VF identity, completion queue, interrupt, shaping, TSO, and cache profile fields.
- Timestamping/TxTime: `struct ice_ts_desc`, `ICE_TS_DESC()`, `struct ice_txtime_ctx`, and TxTime queue/profile constants.

## Control flow
There is no executable flow. Datapath code fills these packed hardware structures and writes descriptors or queue contexts to DMA/MMIO areas. The descriptor unions model read and writeback layouts for the same 32-byte hardware descriptor memory.

## State and persistence behavior
The structures describe DMA-visible ring descriptors and firmware/hardware queue contexts. State persists in device queues and host descriptor rings until queue teardown or reset. Endianness annotations (`__le16`, `__le32`, `__le64`) are part of the hardware ABI.

## Dependencies and integration points
Consumed by Tx/Rx hot paths (`ice_txrx.c`, XDP/XSK, ethtool tests), queue context programming, Flow Director, timestamping, and TxTime support. It depends on common bit helpers and shared constants such as byte/word scaling and register macros.

## Risks
This is ABI-level hardware layout. Field shifts, masks, endianness, or struct packing mistakes can break packet I/O, checksum offload, RSS, Flow Director, VLAN tagging, timestamping, or queue setup. The header intentionally avoids helpers, so callers must compose fields consistently and respect hardware limits such as queue counts and maximum encoded lengths.

## Test signals
Signals include packet Rx/Tx across legacy and flex descriptors, RSS hash and flow ID correctness, VLAN tag extraction/insertion, checksum and TSO offload, XDP/XSK Tx descriptor use, Flow Director add/delete completion writebacks, timestamp descriptor processing, TxTime queue setup, and queue context programming across PF/VF/VMQ modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lan_tx_rx.h -->
