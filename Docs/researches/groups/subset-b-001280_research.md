# subset-b-001280 Research

Grouped research for the listed Ceph-client kernel-source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/sbp2.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/sbp2.c

## Purpose
Implements the FireWire SBP-2 storage transport, exposing SCSI devices over IEEE 1394 logical units. The driver binds to SBP-2 unit directories, creates a `Scsi_Host` per FireWire target, logs into each SBP-2 LUN, translates SCSI commands into SBP-2 ORBs, and reconnects or blocks SCSI I/O across FireWire bus resets.

## APIs, Types, And Functions
Key state is split between `struct sbp2_target` for the FireWire unit/Scsi_Host and `struct sbp2_logical_unit` for each LUN. ORB lifetime is represented by `struct sbp2_orb`, with management and command specializations for login/logout/reconnect and SCSI I/O. Module parameters `exclusive_login` and `workarounds` alter multi-initiator behavior and device quirk handling.

The FireWire driver entry points are `sbp2_probe()`, `sbp2_update()`, and `sbp2_remove()` in `struct fw_driver`. SCSI integration is via `scsi_driver_template`: `sbp2_scsi_queuecommand()`, `sbp2_scsi_sdev_init()`, `sbp2_scsi_sdev_configure()`, and `sbp2_scsi_abort()`. FireWire status writes arrive through `sbp2_status_write()` registered as an address handler.

## Control Flow
Probe rejects local-node targets, allocates a `Scsi_Host`, enables physical DMA, parses the Config ROM for management-agent address, LUN entries, GUID/model/firmware metadata, clamps the management ORB timeout, applies workarounds, and queues delayed login work for every discovered LUN.

`sbp2_login()` sends a management login ORB, stores the command block agent address and login ID, programs `CSR_BUSY_TIMEOUT`, resets the SBP-2 agent, and creates a SCSI device. On later reconnects, `sbp2_reconnect()` issues `SBP2_RECONNECT_REQUEST`, refreshes node/generation information, resets the agent, cancels stale ORBs, and unblocks SCSI requests. `sbp2_update()` handles FireWire bus-reset updates by enabling DMA again, conditionally blocking stale LUNs, and queueing reconnect work.

SCSI commands allocate `struct sbp2_command_orb`, map scatter-gather data as either a direct descriptor or page table, DMA-map the command ORB, then write the ORB pointer to the target agent. Completion can come from the FireWire transaction callback or from a target status write; krefs cover both races. Status blocks are converted into SCSI result/sense data, DMA mappings are released, and `scsi_done()` completes the command.

## State, Persistence, And Dependencies
Runtime state includes login IDs, generation numbers, command block agent addresses, outstanding ORB lists, high-memory status FIFO handlers, DMA mappings, SCSI devices, and target block counters. There is no on-disk persistence; user-visible state is SCSI device presence and the `ieee1394_id` sysfs attribute. Dependencies include FireWire core transactions/address handlers, IEEE 1212 CSR parsing, DMA mapping, workqueues, and the SCSI mid-layer.

## Integration Points
The driver integrates with `fw_bus_type` through the SBP-2 IEEE 1394 ID table, with SCSI scanning/removal and error handling, with sysfs via `ieee1394_id`, and with initramfs compatibility through `MODULE_ALIAS("sbp2")`. Quirk flags affect SCSI inquiry length, mode-sense behavior, capacity correction, power-condition start/stop, and maximum transfer size.

## Risks And Test Signals
Major risks are ORB completion races, stale FireWire generation/node IDs during bus resets, DMA unmap correctness, leaked address handlers or SCSI devices on probe failures, and quirk regressions for old bridge firmware. Useful test signals are FireWire SBP-2 disk attach/remove, repeated bus resets during I/O, SCSI timeout/abort handling, multi-LUN devices, module parameter coverage, and sysfs `ieee1394_id` formatting. No in-file KUnit tests exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/sbp2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/self-id-sequence-helper-test.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/self-id-sequence-helper-test.c

## Purpose
Provides KUnit coverage for FireWire self-ID sequence helper routines defined through `phy-packet-definitions.h`. It verifies sequence enumeration, malformed sequence detection, port-capacity calculation, port-status extraction, and port-status rewriting.

## APIs, Types, And Functions
The tests exercise `struct self_id_sequence_enumerator`, `self_id_sequence_enumerator_next()`, `self_id_sequence_get_port_capacity()`, `self_id_sequence_get_port_status()`, and `self_id_sequence_set_port_status()`. The expected status values use `enum phy_packet_self_id_port_status` values for child, parent, not-connected, and none.

## Control Flow
`test_self_id_sequence_enumerator_valid()` feeds a mixed sequence of primary and extended self-ID quadlets and verifies that each call advances the cursor and remaining quadlet count correctly, ending with `-ENODATA`. `test_self_id_sequence_enumerator_invalid()` checks that an incomplete extended sequence yields `-EPROTO`. `test_self_id_sequence_get_port_status()` reads 28 possible port slots, including one out-of-range slot, mirrors them into mutable quadlets with `self_id_sequence_set_port_status()`, and asserts that the reconstructed quadlets match the expected encoded sequence.

## State, Persistence, And Dependencies
State is local to KUnit stack/static arrays. There is no persistence or external device dependency. The file depends on KUnit and the FireWire PHY packet helper header.

## Integration Points
The test suite is registered as `self-id-sequence-helper` with `kunit_test_suite()`, so it participates in the FireWire KUnit configuration and kernel test runner.

## Risks And Test Signals
The tests protect bit-field layout and iterator edge cases used by topology/self-ID parsing. Gaps include broader malformed sequences and randomized port layouts. A passing KUnit suite is the direct test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/self-id-sequence-helper-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/uapi-test.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/uapi-test.c

## Purpose
KUnit suite that locks down layout of FireWire character-device UAPI event structs exposed through `<linux/firewire-cdev.h>`. It guards ABI size and offset stability for userspace.

## APIs, Types, And Functions
The suite checks `struct fw_cdev_event_response`, `fw_cdev_event_request3`, `fw_cdev_event_response2`, and `fw_cdev_event_phy_packet2` using `sizeof()` and `offsetof()`. It accounts for the known x86-32 alignment difference in `fw_cdev_event_response`.

## Control Flow
Each test function asserts the total structure size and the offset of every fixed field before the trailing flexible `data` member. The cases are registered in the `firewire-uapi-structure-layout` KUnit suite.

## State, Persistence, And Dependencies
There is no mutable state or persistence. Dependencies are KUnit and the public FireWire cdev UAPI header; test behavior varies only by architecture alignment, explicitly handled for `CONFIG_X86_32`.

## Integration Points
The suite runs in kernel KUnit environments and serves as ABI regression coverage for the FireWire userspace event interface introduced or extended across kernel releases.

## Risks And Test Signals
The risk under test is silent UAPI ABI drift caused by field reordering, type changes, or alignment changes. A passing KUnit run confirms the checked layouts; it does not validate ioctl behavior or runtime event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/uapi-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/Kconfig

## Purpose
Defines the top-level `Firmware Drivers` Kconfig menu. It exposes common firmware protocol drivers, system firmware data exports, platform-specific secure-firmware interfaces, and sources subdirectory Kconfig files for ARM SCMI/FF-A, EFI, PSCI, Qualcomm, Tegra, Xilinx, and other vendor firmware blocks.

## APIs, Types, And Functions
This is declarative Kconfig. Important symbols include `ARM_SCPI_PROTOCOL`, `ARM_SDE_INTERFACE`, `EDD`, `FIRMWARE_MEMMAP`, `DMIID`, `DMI_SYSFS`, `ISCSI_IBFT`, `RASPBERRYPI_FIRMWARE`, `FW_CFG_SYSFS`, `INTEL_STRATIX10_SERVICE`, `MTK_ADSP_IPC`, `SYSFB`, `SYSFB_SIMPLEFB`, `TH1520_AON_PROTOCOL`, `TI_SCI_PROTOCOL`, `TRUSTED_FOUNDATIONS`, and `TURRIS_MOX_RWTM`.

## Control Flow
Kconfig evaluates dependencies, defaults, and `select` relationships to decide which firmware objects and submenus are available. The file starts by sourcing ARM SCMI, defines many top-level options, then sources ARM FF-A and vendor/platform subtrees before closing the menu.

## State, Persistence, And Dependencies
Persistent output is the configured kernel `.config`; no runtime state is produced directly. Dependencies connect options to architecture support, ACPI/DMI/SCSI/SYSFS, mailbox providers, DMA, OF, KEYS, and other platform facilities.

## Integration Points
The matching `drivers/firmware/Makefile` consumes these symbols to include objects and subdirectories. Downstream drivers depend on these symbols to obtain firmware protocol APIs, sysfs exports, boot firmware data, and platform services.

## Risks And Test Signals
Risks are incorrect dependencies that expose unbuildable drivers, missing `select`s for required helper subsystems, defaults that change boot behavior, and stale sourced paths. Test signals are `olddefconfig`, `allmodconfig`, architecture build coverage, and boot/sysfs smoke tests for enabled firmware features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/Makefile

## Purpose
Builds the firmware driver directory according to Kconfig symbols. It maps top-level firmware options to object files and always descends into common firmware subdirectories whose internal Makefiles decide whether objects are built.

## APIs, Types, And Functions
The file is kbuild syntax. Important mappings include `CONFIG_ARM_SCPI_PROTOCOL` to `arm_scpi.o`, `CONFIG_DMI` to `dmi_scan.o`, `CONFIG_ISCSI_IBFT` to `iscsi_ibft.o`, `CONFIG_SYSFB` to `sysfb.o`, and unconditional `obj-y` descent into `arm_ffa/`, `arm_scmi/`, `efi/`, `imx/`, `psci/`, `qcom/`, `smccc/`, and other vendor directories.

## Control Flow
kbuild expands `obj-$(CONFIG_...)` entries based on `.config`. Directory entries route the build into nested firmware areas, while individual object entries compile directly into built-in or module targets.

## State, Persistence, And Dependencies
There is no runtime state. Build outputs are object files and modules determined by Kconfig. Dependencies are the symbols defined in `drivers/firmware/Kconfig` and subdirectory Kconfig files.

## Integration Points
This is the build-side counterpart of the firmware Kconfig menu. It controls whether firmware protocol providers and platform drivers become available to the rest of the kernel.

## Risks And Test Signals
Risks are missing object mappings, stale object names after source renames, and unconditional subdirectory traversal hiding broken nested dependencies. Build matrix coverage across built-in/module/disabled configurations is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Kconfig

## Purpose
Defines configuration for the Arm Firmware Framework for Arm A-profile processors. `ARM_FFA_TRANSPORT` enables the FF-A bus and core interface for client drivers, while `ARM_FFA_SMCCC` selects the SMCCC-based transport helper.

## APIs, Types, And Functions
Kconfig symbols are `ARM_FFA_TRANSPORT`, a tristate depending on `OF` and `ARM64`, and `ARM_FFA_SMCCC`, a bool defaulting to the transport and depending on `ARM64 && HAVE_ARM_SMCCC_DISCOVERY`.

## Control Flow
When `ARM_FFA_TRANSPORT` is enabled, kbuild enters the FF-A Makefile and builds the bus/core module pieces. `ARM_FFA_SMCCC` gates the SMCCC transport implementation used to issue FF-A calls.

## State, Persistence, And Dependencies
Persistent state is limited to `.config`. Dependencies ensure FF-A is only exposed on ARM64 systems with device tree, and SMCCC transport only when SMCCC discovery is present.

## Integration Points
The symbols drive `arm_ffa/Makefile`, `common.h` transport stubs, and the runtime FF-A driver initialized by `rootfs_initcall()`.

## Risks And Test Signals
Risks are overly narrow dependencies that hide compile-test coverage or overly broad dependencies that expose uncallable firmware transport code. Build tests with `ARM_FFA_TRANSPORT=y/m` and SMCCC discovery coverage are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Makefile

## Purpose
Defines kbuild composition for the Arm FF-A bus/core and transport module.

## APIs, Types, And Functions
`ffa-core.o` is built from `bus.o`. `ffa-module.o` is built from `driver.o` and optional transport objects, currently `smccc.o` when `CONFIG_ARM_FFA_SMCCC` is enabled. Both are tied to `CONFIG_ARM_FFA_TRANSPORT`.

## Control Flow
kbuild expands `ffa-transport-$(CONFIG_ARM_FFA_SMCCC)` and links the resulting object lists into the two FF-A build products.

## State, Persistence, And Dependencies
No runtime state is in the Makefile. Build artifacts depend on `ARM_FFA_TRANSPORT` and `ARM_FFA_SMCCC`.

## Integration Points
The split lets the bus layer register early as `ffa-core`, while the runtime driver and transport calls live in `ffa-module`.

## Risks And Test Signals
Risks are link omissions between bus, driver, and transport symbols. Test signals are module and built-in builds for FF-A with and without `ARM_FFA_SMCCC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/bus.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/bus.c

## Purpose
Implements the Linux bus type for Arm FF-A partitions. It provides FF-A device/driver matching, sysfs attributes, modalias generation, driver registration helpers, device registration helpers, and bus lifecycle.

## APIs, Types, And Functions
Exports `ffa_bus_type`, `ffa_driver_register()`, `ffa_driver_unregister()`, `ffa_devices_unregister()`, `ffa_device_is_valid()`, `ffa_device_register()`, and `ffa_device_unregister()`. Devices expose read-only `partition_id`, `uuid`, and `modalias` attributes. Device IDs are allocated from a global `DEFINE_IDA(ffa_bus_id)`.

## Control Flow
`arm_ffa_bus_init()` registers the `arm_ffa` bus at `subsys_initcall`. Driver registration requires a probe callback, assigns bus/name/owner metadata, and calls `driver_register()`. Device registration allocates an ID, allocates `struct ffa_device`, populates VM ID/properties/ops/UUID, and calls `device_register()`. Removal unregisters devices, frees IDs in the release callback, then unregisters the bus at module exit.

## State, Persistence, And Dependencies
Runtime state is the bus registry, registered `struct ffa_device` instances, and IDA allocation state. There is no persistence beyond sysfs/kobject state. Dependencies include the driver core, module infrastructure, UUID helpers, and `linux/arm_ffa.h` types.

## Integration Points
`driver.c` registers discovered FF-A partitions via `ffa_device_register()`. FF-A client drivers bind through `ffa_driver_register()` and module autoloading via `arm_ffa:%04x:%pUb` modaliases. For FF-A v1.0, devices with null UUIDs match temporarily and the driver path later resolves UUIDs through the bus notifier in `driver.c`.

## Risks And Test Signals
Risks include null UUID matching binding too broadly, IDA leaks on registration failure, and invalid device validation if bus iteration sees transient devices. Signals are sysfs attribute checks, modalias/module autoload tests, driver bind/unbind, and FF-A partition enumeration on real or emulated firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/common.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/common.h

## Purpose
Shared private header for FF-A bus, driver, and transport code. It centralizes FF-A call ABI typing, local helper prototypes, and the optional transport-init interface.

## APIs, Types, And Functions
Defines `ffa_value_t` as `struct arm_smccc_1_2_regs` and `ffa_fn` as the function-pointer type used for FF-A calls. Declares `ffa_device_is_valid()`, `ffa_device_match_uuid()`, and `ffa_transport_init()`. When `CONFIG_ARM_FFA_SMCCC` is disabled, `ffa_transport_init()` is an inline stub returning `-EOPNOTSUPP`.

## Control Flow
Consumers include this header to obtain a transport-specific `invoke_ffa_fn` pointer during FF-A driver init, or to use bus helper functions. Compile-time `#ifdef CONFIG_ARM_FFA_SMCCC` selects the real transport initializer or stub.

## State, Persistence, And Dependencies
No state is stored in the header. It depends on public FF-A, SMCCC, and errno definitions.

## Integration Points
`smccc.c` implements the real `ffa_transport_init()`, `driver.c` calls it during `ffa_init()`, and `bus.c` shares the device validation and UUID matching declarations.

## Risks And Test Signals
The main risk is ABI mismatch in `ffa_value_t` or missing transport support causing FF-A init failure. Build tests with `CONFIG_ARM_FFA_SMCCC` enabled and disabled validate the conditional declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/driver.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/driver.c

## Purpose
Implements the Arm FF-A core interface driver. It discovers firmware version/capabilities, maps RX/TX buffers, enumerates FF-A partitions as bus devices, exposes messaging/memory/CPU/notification ops to clients, and manages notification interrupts and callbacks.

## APIs, Types, And Functions
The central runtime object is global `struct ffa_drv_info`, containing firmware version, local VM ID, RX/TX buffer locks and pages, feature flags, notification IRQ/workqueue state, partition xarray, and notification callback hash. Exported client-facing behavior is grouped into `struct ffa_ops`: info ops (`api_version_get`, `partition_info_get`), message ops (`sync_send_receive`, `indirect_send`, `sync_send_receive2`, `mode_32bit_set`), memory ops (`memory_share`, `memory_lend`, `memory_reclaim`), CPU op (`run`), and notifier ops.

## Control Flow
`ffa_init()` obtains the transport call function, allocates `drv_info`, negotiates FF-A version, gets the local VM ID, sizes and maps RX/TX buffers, initializes locks and feature flags, sets up notifications, and enumerates partitions. Partition discovery uses either buffer-based `FFA_PARTITION_INFO_GET` or register-based `FFA_PARTITION_INFO_GET_REGS`, then registers `struct ffa_device` entries on the FF-A bus and tracks per-partition callback records in an xarray.

Direct messaging packages arguments into FF-A direct request calls and waits through `FFA_INTERRUPT`/`FFA_YIELD` by issuing `FFA_RUN`. Indirect messaging writes an `ffa_indirect_msg_hdr` and payload into the TX buffer. Memory share/lend builds an FF-A memory region descriptor from endpoint attributes and scatterlists, fragments it across TX buffer limits, and transmits through `MEM_SHARE`/`MEM_LEND`, with reclaim using the returned global handle.

Notification setup creates a bitmap when supported, maps schedule-receiver and notification-pending interrupts, registers per-CPU IRQ handlers, creates a workqueue, and enables CPU hotplug callbacks. Notification callbacks are registered in a hash table, bound/unbound with firmware for normal notifications, and invoked from bitmap retrieval or framework RX-buffer notifications.

## State, Persistence, And Dependencies
State is runtime-only: RX/TX pages shared with firmware, mapped FF-A buffers, partition device registrations, xarray/list callback records, notification hash entries, per-CPU IRQ registrations, CPU hotplug state, workqueue work items, and feature flags. No disk persistence exists. Dependencies include SMCCC transport, FF-A public ABI, device core, xarray, hashtable, scatterlist/DMA page helpers, OF/ACPI IRQ mapping, CPU hotplug, and workqueues.

## Integration Points
The driver registers at `rootfs_initcall()` so FF-A devices appear early. It integrates with `arm_ffa` bus helpers, client drivers through `struct ffa_ops`, firmware via `invoke_ffa_fn`, IRQ infrastructure for donated interrupt IDs, and bus notifiers to resolve UUIDs on FF-A v1.0 systems that only expose partition IDs initially.

## Risks And Test Signals
High-risk areas include RX/TX buffer locking, RX release timing, memory descriptor fragmentation, native vs 32-bit FF-A response packing, partition discovery format differences across FF-A versions, notification callback lifetime under interrupts, IRQ cleanup on partial setup, and host partition registration failures. Test signals are FF-A firmware boot logs, partition device sysfs entries, direct/indirect message round trips, memory share/lend/reclaim exercises, notification bind/send/callback tests, CPU hotplug with per-CPU IRQs, and module unload cleanup. Static analysis should also inspect the notification loop bounds and error unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/smccc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/smccc.c

## Purpose
Provides the FF-A transport initializer for SMCCC conduits. It selects whether FF-A calls should use SMC or HVC based on firmware-reported SMCCC conduit information.

## APIs, Types, And Functions
Defines private wrappers `__arm_ffa_fn_smc()` and `__arm_ffa_fn_hvc()` around `arm_smccc_1_2_smc()` and `arm_smccc_1_2_hvc()`. Implements `ffa_transport_init(ffa_fn **invoke_ffa_fn)`.

## Control Flow
Initialization checks for SMCCC v1.2 or newer, asks for the SMCCC conduit, rejects `SMCCC_CONDUIT_NONE`, and stores the appropriate wrapper function pointer for the FF-A driver to call.

## State, Persistence, And Dependencies
No persistent state is owned here; the selected function pointer is stored by the caller. Dependencies are SMCCC v1.2 register ABI and conduit discovery.

## Integration Points
`driver.c` calls `ffa_transport_init()` before any FF-A ABI call. The function is built only when `CONFIG_ARM_FFA_SMCCC` enables this transport.

## Risks And Test Signals
Risks are incorrect conduit selection or running on firmware without SMCCC v1.2 support. Test signals are FF-A driver initialization success on SMC and HVC systems and graceful `-EOPNOTSUPP` on unsupported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/smccc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Kconfig

## Purpose
Defines configuration for the ARM System Control and Management Interface protocol stack, optional debug/raw/quirk facilities, SCMI transports, vendor extensions, and the SCMI system power-control client driver.

## APIs, Types, And Functions
Main symbols are `ARM_SCMI_PROTOCOL`, `ARM_SCMI_NEED_DEBUGFS`, `ARM_SCMI_RAW_MODE_SUPPORT`, `ARM_SCMI_RAW_MODE_SUPPORT_COEX`, `ARM_SCMI_DEBUG_COUNTERS`, `ARM_SCMI_QUIRKS`, and `ARM_SCMI_POWER_CONTROL`. The file sources transport and NXP i.MX vendor Kconfig fragments.

## Control Flow
When `ARM_SCMI_PROTOCOL` is enabled, nested options expose raw mode, debug counters, quirks, transports, and vendors. `ARM_SCMI_POWER_CONTROL` remains outside the `if` block and can depend on SCMI or compile-test plus OF.

## State, Persistence, And Dependencies
Persistent effect is kernel configuration. Dependencies include ARM/ARM64/COMPILE_TEST, DEBUG_FS, JUMP_LABEL, OF for compile-tested power control, and transport-specific symbols in sourced files.

## Integration Points
These symbols drive `arm_scmi/Makefile`, enable protocol modules such as base/clock/perf/power, and control whether raw debugfs and quirk code is linked.

## Risks And Test Signals
Risks include raw mode accidentally coexisting with regular clients, missing debugfs selects, and quirk framework availability depending on jump labels. Signals are config/build coverage and boot tests with representative SCMI transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Makefile

## Purpose
Composes SCMI bus, core driver, protocols, transports, vendor extensions, and power-control client objects for kbuild.

## APIs, Types, And Functions
`scmi-core.o` contains `bus.o`. `scmi-module.o` contains the main driver, notifications, optional quirks/raw mode, optional shmem/msg transport helpers, and protocol implementations (`base.o`, `clock.o`, `perf.o`, `power.o`, `reset.o`, `sensors.o`, `system.o`, `voltage.o`, `powercap.o`, `pinctrl.o`). `scmi_power_control.o` is built under `CONFIG_ARM_SCMI_POWER_CONTROL`.

## Control Flow
kbuild descends into `transports/` and `vendors/imx/` when `CONFIG_ARM_SCMI_PROTOCOL` is set, then links bus/core and module objects according to configuration.

## State, Persistence, And Dependencies
No runtime state is in the Makefile. Build outputs depend on SCMI Kconfig symbols, transport selections, and optional debug/quirk/raw features.

## Integration Points
This file determines which SCMI protocol implementations are present for client drivers and which transport support code is linked into the SCMI module.

## Risks And Test Signals
Risks are missing protocol objects, optional object mismatches with Kconfig, and build failures when transport helpers are selected in unusual combinations. `allmodconfig`, `allyesconfig`, and minimal transport-specific builds are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/base.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/base.c

## Purpose
Implements the SCMI Base protocol. It discovers firmware identity, implementation version, number of protocols/agents, implemented protocol IDs, agent names, and Base error notifications.

## APIs, Types, And Functions
Defines Base protocol command IDs and response payload structures. Important functions include `scmi_base_attributes_get()`, `scmi_base_vendor_id_get()`, `scmi_base_implementation_version_get()`, `scmi_base_implementation_list_get()`, `scmi_base_discover_agent_get()`, and notification helpers for `BASE_NOTIFY_ERRORS`. The protocol registers through `DEFINE_SCMI_PROTOCOL_REGISTER_UNREGISTER(base, scmi_base)`.

## Control Flow
Protocol init obtains the shared revision area, stores version fields, reads attributes, allocates the implemented-protocol list, retrieves vendor/subvendor/implementation data, enumerates implemented protocols in batches, publishes them to SCMI core, logs firmware identity, and optionally logs agent names. Error notifications can be enabled or disabled through SCMI notification ops; incoming payloads are converted into `struct scmi_base_error_report`.

## State, Persistence, And Dependencies
Runtime state is written into SCMI core revision/protocol implementation areas and devm-managed protocol data. No disk persistence exists. Dependencies include SCMI transfer ops, protocol handle ops, notifications, and endian/unaligned helpers.

## Integration Points
The Base protocol underpins SCMI core enumeration, allowing later protocol clients to know which protocols are implemented. Its event descriptor integrates with the common SCMI notifier framework.

## Risks And Test Signals
Risks include malformed protocol-list replies, truncated RX payloads, overreported protocol counts, and very large Base error command counts. The code has explicit protocol-size validation and warning paths. Test signals are SCMI boot logs showing firmware version/protocol counts, protocol availability to clients, and Base error notification injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/bus.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/bus.c

## Purpose
Implements the SCMI protocol bus. It manages SCMI client driver registration, requested protocol/name device tables, SCMI device creation/destruction per SCMI instance, modalias/sysfs attributes, PM forwarding, and bus lifecycle.

## APIs, Types, And Functions
Exports `scmi_bus_type`, `scmi_requested_devices_nh`, `scmi_driver_register()`, `scmi_driver_unregister()`, `scmi_device_create()`, and `scmi_device_destroy()`. State helpers use `DEFINE_IDA(scmi_bus_id)`, `DEFINE_IDR(scmi_requested_devices)`, `scmi_requested_devices_mtx`, and `atomic_t scmi_syspower_registered`.

## Control Flow
When an SCMI driver registers, its ID table is recorded as requested devices and advertised on the blocking notifier chain. SCMI core instances later call `scmi_device_create()` to instantiate one named device or all requested devices for a protocol. Matching requires protocol ID and name equality, excluding internal transport devices. Probe defers until `scmi_dev->handle` exists. Device destruction clears the unique SystemPower registration flag when applicable, frees the bus ID, and unregisters the device.

## State, Persistence, And Dependencies
Runtime state includes requested-device IDR lists, bus devices, allocated names, IDA IDs, notifier chain entries, and a global SystemPower uniqueness flag. There is no persistent storage. Dependencies include device core, OF node association, notifier chains, IDA/IDR, mutexes, atomics, and SCMI public driver IDs.

## Integration Points
The main SCMI driver creates devices as firmware protocols are discovered; SCMI client drivers register ID tables and bind through this bus. Sysfs exposes `protocol_id`, `name`, and `modalias`, while PM callbacks forward suspend/resume to bound client drivers.

## Risks And Test Signals
Risks include races between late driver registration and SCMI instance probe, duplicate requested names, raw-mode rejection changing client availability, global SystemPower uniqueness across instances, and cleanup ordering on module unload. Signals are SCMI client module autoload, bind/unbind tests, multiple SCMI instance probing, raw-mode configs, and sysfs/modalias inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/clock.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/clock.c

## Purpose
Implements the SCMI Clock protocol. It discovers platform-managed clocks, exposes clock rate/state/parent/OEM configuration operations to SCMI clients, and supports clock rate change notifications.

## APIs, Types, And Functions
Protocol state is `struct clock_info`, containing clock count, max async requests, notification command availability, current async request count, a devm-managed array of `struct scmi_clock_info`, and version-specific config get/set function pointers. The exported protocol ops are `count_get`, `info_get`, `rate_get`, `rate_set`, `enable`, `disable`, `state_get`, `config_oem_get`, `config_oem_set`, `parent_set`, and `parent_get`.

## Control Flow
Protocol init reads protocol attributes, allocates per-clock info, then loops over every clock to read attributes, extended names, notification support, parent support, permissions, extended config support, and rates. Rates are obtained through iterator helpers and can be either a sorted discrete list or min/max/step triplet; an SCMI quirk can repair known out-of-spec triplet replies.

At runtime, rate get/set use `CLOCK_RATE_GET` and `CLOCK_RATE_SET`; rate set optionally uses asynchronous completion when firmware advertises async capacity. Enable/disable and state/config queries dispatch to v1/v2 or v3 config formats depending on protocol version. Parent operations validate parent indexes against cached possible-parent arrays and then use firmware parent IDs.

Notifications map SCMI clock events to `CLOCK_RATE_NOTIFY` or `CLOCK_RATE_CHANGE_REQUESTED_NOTIFY`, validate per-clock support, enable/disable firmware notifications, and translate payloads into `struct scmi_clock_rate_notif_report`.

## State, Persistence, And Dependencies
Runtime state is a devm-managed cache of discovered clocks, names, rate descriptions, parent IDs, permissions, notification capabilities, and extended-config support. `atomic_t cur_async_req` tracks in-flight async rate requests. There is no persistent storage. Dependencies include SCMI protocol/transfer/iterator ops, SCMI notifier framework, quirks, sorting, and endian helpers.

## Integration Points
Registered as `SCMI_PROTOCOL_CLOCK` via `DEFINE_SCMI_PROTOCOL_REGISTER_UNREGISTER(clock, scmi_clock)`. Client clock providers consume `scmi_clk_proto_ops`; notifications feed the SCMI notifier framework for consumers interested in clock rate changes.

## Risks And Test Signals
Risks include firmware overreporting rates or parents, permissions not being enforced by older firmware, async request accounting edge cases, protocol-version field differences, invalid parent indexes, and malformed notification payloads. Signals are SCMI clock enumeration logs, common clock framework consumers using rates/parents, enable/disable/state tests, notification injection, and quirk-platform coverage for malformed rate triplets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/common.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/common.h

## Purpose
Private SCMI core header shared by bus, driver, transports, protocol implementations, raw mode, and notification code. It defines common limits, error mapping, message header packing, transfer lookup helpers, bus/device APIs, transport descriptors, shared-memory/message datagram operations, debug counters, and transport-driver scaffolding.

## APIs, Types, And Functions
Important definitions include `SCMI_MAX_CHANNELS`, `SCMI_MAX_RESPONSE_TIMEOUT`, SCMI firmware-to-Linux error mapping through `scmi_to_linux_errno()`, message header masks and `pack_scmi_header()`/`unpack_scmi_header()`, `XFER_FIND()`, `struct scmi_chan_info`, `struct scmi_transport_ops`, `struct scmi_desc`, `struct scmi_debug_info`, `struct scmi_shared_mem_operations`, `struct scmi_message_operations`, `struct scmi_transport_core_operations`, `struct scmi_transport`, and `DEFINE_SCMI_TRANSPORT_DRIVER()`.

## Control Flow
Inline helpers determine whether polling is required, whether a transport is polling-capable, and whether polling is enabled. Header packing/unpacking defines the common transfer format. The transport-driver macro creates a platform transport probe that allocates an `arm-scmi` platform device, attaches copied transport descriptor data, parents it to the supplier, and registers automatic cleanup.

## State, Persistence, And Dependencies
The header declares but does not own most state. Structures defined here are embedded in runtime SCMI instances, channels, transports, and debugfs data. Optional debug counters increment/decrement atomically only when `CONFIG_ARM_SCMI_DEBUG_COUNTERS` is enabled. Dependencies include completion, device core, hash tables, lists, refcounts, spinlocks, public SCMI protocol definitions, notifications, and protocol IDs.

## Integration Points
Nearly every SCMI implementation file includes this header. It connects protocol registration to bus device creation, main driver transfer handling to transports, and shared-memory/message transport implementations to the core RX/TX callbacks.

## Risks And Test Signals
Risks are broad because this is a shared contract: header bitfield changes can break firmware ABI, transport descriptor changes can break every transport, and macro changes can alter probe ordering or cleanup. Signals are full SCMI build coverage, transport-specific boot tests, message header round trips, debug counter sanity checks, raw-mode compile coverage, and sparse/static analysis for structure contract drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/common.h -->
